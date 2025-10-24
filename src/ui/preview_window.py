"""Preview window for viewing decoded results before export - Enhanced v2.2"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
from typing import Optional, Callable, List, Dict
from pathlib import Path

from .ui_constants import ICONS, COLORS, TOOLTIPS, FONTS, PADDING
from .ui_utils import ToolTip, show_context_menu, confirm_dialog, info_dialog, error_dialog


class PreviewWindow:
    """Enhanced preview window with context menus, visual indicators, and bulk operations"""

    def __init__(self, parent, dataframe: pd.DataFrame, stats: dict, on_save_callback: Optional[Callable] = None):
        """
        Initialize preview window

        Args:
            parent: Parent tkinter window
            dataframe: DataFrame with processed order data
            stats: Dictionary with processing statistics
            on_save_callback: Optional callback function when save is clicked
        """
        self.parent = parent
        self.df = dataframe.copy()
        self.original_df = dataframe.copy()
        self.stats = stats
        self.on_save_callback = on_save_callback

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Row notes and important marks
        self.row_notes = {}  # {row_index: note_text}
        self.important_rows = set()  # {row_index}

        # Identify decoded rows (rows that were created from set decoding)
        self._identify_decoded_rows()

        # Create toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title(f"{ICONS['preview']} Preview Decoded Results")
        self.window.geometry("1300x750")

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        # Sorting state
        self.sort_column = None
        self.sort_reverse = False

        self._create_ui()
        self._populate_table()
        self._create_context_menu()

        # Bind keyboard shortcuts
        self.window.bind('<Control-z>', lambda e: self._undo())
        self.window.bind('<Control-y>', lambda e: self._redo())
        self.window.bind('<Delete>', lambda e: self._delete_selected_rows())

    def _identify_decoded_rows(self):
        """Identify which rows were created from set decoding"""
        self.decoded_rows = set()

        # Rows with price = 0 are likely decoded set components (except first component)
        if 'Lineitem price' in self.df.columns:
            for idx, row in self.df.iterrows():
                # Simple heuristic: if price is 0 and it's in original data
                if row.get('Lineitem price', 0) == 0.0:
                    self.decoded_rows.add(idx)

    def _create_ui(self):
        """Create the UI layout"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=PADDING['normal'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Statistics section at top
        self._create_stats_section(main_frame)

        # Toolbar with actions
        self._create_toolbar(main_frame)

        # Search and filter section
        self._create_filter_section(main_frame)

        # Table section
        self._create_table_section(main_frame)

        # Action buttons at bottom
        self._create_action_buttons(main_frame)

    def _create_stats_section(self, parent):
        """Create statistics display section"""
        stats_frame = ttk.LabelFrame(parent, text=f"{ICONS['info']} Processing Summary",
                                     padding=PADDING['normal'])
        stats_frame.pack(fill=tk.X, pady=(0, PADDING['normal']))

        # Create columns for statistics
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        row = 0
        col = 0
        for key, value in self.stats.items():
            # Create label with key
            key_label = ttk.Label(stats_grid, text=f"{key}:", font=FONTS['bold'])
            key_label.grid(row=row, column=col*2, sticky=tk.W, padx=(0, PADDING['small']))

            # Create label with value
            value_label = ttk.Label(stats_grid, text=str(value), foreground=COLORS['info'])
            value_label.grid(row=row, column=col*2+1, sticky=tk.W, padx=(0, PADDING['large']))

            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1

    def _create_toolbar(self, parent):
        """Create toolbar with action buttons"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, PADDING['small']))

        # Undo/Redo buttons
        self.undo_btn = ttk.Button(toolbar, text=f"{ICONS['edit']} Undo",
                                   command=self._undo, state='disabled')
        self.undo_btn.pack(side=tk.LEFT, padx=(0, PADDING['tiny']))
        ToolTip(self.undo_btn, "Undo last operation (Ctrl+Z)")

        self.redo_btn = ttk.Button(toolbar, text=f"{ICONS['reload']} Redo",
                                   command=self._redo, state='disabled')
        self.redo_btn.pack(side=tk.LEFT, padx=(0, PADDING['normal']))
        ToolTip(self.redo_btn, "Redo last undone operation (Ctrl+Y)")

        # Bulk operations
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y,
                                                       padx=PADDING['small'])

        bulk_btn = ttk.Button(toolbar, text=f"{ICONS['delete']} Delete Selected",
                             command=self._delete_selected_rows)
        bulk_btn.pack(side=tk.LEFT, padx=(0, PADDING['tiny']))
        ToolTip(bulk_btn, "Delete selected rows (Del key)")

        # Legend for visual indicators
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y,
                                                       padx=PADDING['small'])

        legend_label = ttk.Label(toolbar, text=f"{ICONS['info']} Legend:",
                                font=FONTS['small'])
        legend_label.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        decoded_label = ttk.Label(toolbar, text="[Decoded Set]",
                                 foreground=COLORS['decoded_set'],
                                 font=FONTS['small'], background=COLORS['decoded_set'])
        decoded_label.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        important_label = ttk.Label(toolbar, text=f"{ICONS['important']} Important",
                                   foreground=COLORS['error'], font=FONTS['small'])
        important_label.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        note_label = ttk.Label(toolbar, text=f"{ICONS['note']} Has Note",
                              foreground=COLORS['warning'], font=FONTS['small'])
        note_label.pack(side=tk.LEFT)

    def _create_filter_section(self, parent):
        """Create search and filter controls"""
        filter_frame = ttk.LabelFrame(parent, text=f"{ICONS['search']} Search & Filter",
                                      padding=PADDING['normal'])
        filter_frame.pack(fill=tk.X, pady=(0, PADDING['normal']))

        # Search box
        search_container = ttk.Frame(filter_frame)
        search_container.pack(fill=tk.X)

        ttk.Label(search_container, text="Search:").pack(side=tk.LEFT,
                                                         padx=(0, PADDING['small']))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._apply_filter())

        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, PADDING['normal']))
        ToolTip(search_entry, TOOLTIPS['search'])

        # Filter by order ID
        ttk.Label(search_container, text="Order ID:").pack(side=tk.LEFT,
                                                           padx=(PADDING['normal'], PADDING['small']))

        self.order_filter_var = tk.StringVar()
        self.order_filter_var.trace('w', lambda *args: self._apply_filter())

        order_combo = ttk.Combobox(search_container, textvariable=self.order_filter_var,
                                   width=15, state='readonly')
        order_combo['values'] = ['(All)'] + sorted(self.df['Name'].unique().tolist())
        order_combo.current(0)
        order_combo.pack(side=tk.LEFT, padx=(0, PADDING['normal']))
        ToolTip(order_combo, TOOLTIPS['filter_order'])

        # Clear filters button
        clear_btn = ttk.Button(search_container, text=f"{ICONS['delete']} Clear",
                              command=self._clear_filters)
        clear_btn.pack(side=tk.LEFT)

        # Results count
        self.results_label = ttk.Label(search_container, text="",
                                      foreground=COLORS['info'], font=FONTS['small'])
        self.results_label.pack(side=tk.RIGHT, padx=(PADDING['normal'], 0))

    def _create_table_section(self, parent):
        """Create table with scrollbars"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['normal']))

        # Create Treeview with scrollbars
        self.tree = ttk.Treeview(table_frame, show='headings', selectmode='extended')

        # Vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define columns (show most important ones)
        display_columns = ['Name', 'Lineitem sku', 'Lineitem name',
                          'Lineitem quantity', 'Lineitem price']

        # Filter to only include columns that exist in dataframe
        self.display_columns = [col for col in display_columns if col in self.df.columns]

        self.tree['columns'] = self.display_columns

        # Configure column headings and widths
        column_widths = {
            'Name': 100,
            'Lineitem sku': 150,
            'Lineitem name': 350,
            'Lineitem quantity': 80,
            'Lineitem price': 80
        }

        for col in self.display_columns:
            # Add sort indicator
            self.tree.heading(col, text=col,
                            command=lambda c=col: self._sort_by_column(c))
            width = column_widths.get(col, 150)
            align = tk.CENTER if col in ['Lineitem quantity', 'Lineitem price'] else tk.W
            self.tree.column(col, width=width, anchor=align)

        # Configure tags for visual indicators
        self.tree.tag_configure('decoded', background=COLORS['decoded_set'])
        self.tree.tag_configure('important', foreground=COLORS['error'], font=FONTS['bold'])
        self.tree.tag_configure('has_note', foreground=COLORS['warning'])

        # Bind events
        self.tree.bind('<Double-1>', self._show_row_details)
        self.tree.bind('<Button-3>', self._show_context_menu)  # Right-click

    def _create_action_buttons(self, parent):
        """Create action buttons at bottom"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        export_btn = ttk.Button(left_buttons, text=f"{ICONS['export']} Export Selected",
                               command=self._export_selected)
        export_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))
        ToolTip(export_btn, TOOLTIPS['export_selected'])

        copy_btn = ttk.Button(left_buttons, text=f"{ICONS['copy']} Copy to Clipboard",
                             command=self._copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT)
        ToolTip(copy_btn, TOOLTIPS['copy_all'])

        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        cancel_btn = ttk.Button(right_buttons, text="Cancel",
                               command=self.window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        save_btn = ttk.Button(right_buttons, text=f"{ICONS['save']} Save As...",
                             command=self._save_as)
        save_btn.pack(side=tk.LEFT)

    def _create_context_menu(self):
        """Create right-click context menu for table rows"""
        self.context_menu = tk.Menu(self.window, tearoff=0)

        self.context_menu.add_command(
            label=f"{ICONS['copy']} Copy Row Data",
            command=self._copy_selected_row
        )

        self.context_menu.add_command(
            label=f"{ICONS['delete']} Delete Row",
            command=self._delete_selected_rows
        )

        self.context_menu.add_separator()

        self.context_menu.add_command(
            label=f"{ICONS['details']} View Full Details",
            command=lambda: self._show_row_details(None)
        )

        self.context_menu.add_separator()

        self.context_menu.add_command(
            label=f"{ICONS['important']} Mark as Important",
            command=self._toggle_important
        )

        self.context_menu.add_command(
            label=f"{ICONS['note']} Add/Edit Note",
            command=self._edit_note
        )

    def _show_context_menu(self, event):
        """Show context menu at mouse position"""
        # Select row under mouse
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            show_context_menu(event, self.context_menu)

    def _populate_table(self):
        """Populate table with data and apply visual indicators"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows with appropriate tags
        for idx, row in self.df.iterrows():
            values = [row[col] for col in self.display_columns]

            # Determine tags for this row
            tags = [str(idx)]  # Store index as tag

            if idx in self.decoded_rows:
                tags.append('decoded')

            if idx in self.important_rows:
                tags.append('important')

            if idx in self.row_notes:
                tags.append('has_note')
                # Add note indicator to name
                if 'Lineitem name' in self.display_columns:
                    name_idx = self.display_columns.index('Lineitem name')
                    values[name_idx] = f"{ICONS['note']} {values[name_idx]}"

            self.tree.insert('', tk.END, values=values, tags=tuple(tags))

        # Update results count
        self._update_results_count()

    def _apply_filter(self):
        """Apply search and filter criteria"""
        search_text = self.search_var.get().lower()
        order_filter = self.order_filter_var.get()

        # Start with original dataframe
        filtered_df = self.original_df.copy()

        # Apply order filter
        if order_filter and order_filter != '(All)':
            filtered_df = filtered_df[filtered_df['Name'] == order_filter]

        # Apply search filter
        if search_text:
            # Search in all displayed columns
            mask = filtered_df[self.display_columns].astype(str).apply(
                lambda x: x.str.lower().str.contains(search_text, na=False, regex=False)
            ).any(axis=1)
            filtered_df = filtered_df[mask]

        self.df = filtered_df
        self._populate_table()

    def _clear_filters(self):
        """Clear all filters"""
        self.search_var.set('')
        self.order_filter_var.set('(All)')
        self.df = self.original_df.copy()
        self._populate_table()

    def _sort_by_column(self, column):
        """Sort table by column with visual indicator"""
        try:
            # Toggle sort direction if same column
            if self.sort_column == column:
                self.sort_reverse = not self.sort_reverse
            else:
                self.sort_column = column
                self.sort_reverse = False

            # Sort dataframe
            self.df = self.df.sort_values(by=column, ascending=not self.sort_reverse)

            # Update heading to show sort direction
            for col in self.display_columns:
                if col == column:
                    indicator = " ↓" if self.sort_reverse else " ↑"
                    self.tree.heading(col, text=f"{col}{indicator}")
                else:
                    self.tree.heading(col, text=col)

            self._populate_table()
        except Exception as e:
            error_dialog(self.window, "Sort Error", f"Could not sort by {column}: {str(e)}")

    def _update_results_count(self):
        """Update results count label"""
        total = len(self.original_df)
        shown = len(self.df)

        if shown == total:
            self.results_label.config(text=f"Showing {total} rows")
        else:
            self.results_label.config(text=f"Showing {shown} of {total} rows (filtered)")

    def _get_selected_indices(self) -> List[int]:
        """Get indices of selected rows"""
        selection = self.tree.selection()
        if not selection:
            return []

        return [int(self.tree.item(item)['tags'][0]) for item in selection]

    def _show_row_details(self, event):
        """Show full details for selected row"""
        indices = self._get_selected_indices()
        if not indices:
            return

        row_idx = indices[0]
        row_data = self.original_df.iloc[row_idx]

        # Create detail window
        detail_window = tk.Toplevel(self.window)
        detail_window.title(f"{ICONS['details']} Row Details")
        detail_window.geometry("650x550")
        detail_window.transient(self.window)

        # Create text widget with scrollbar
        frame = ttk.Frame(detail_window, padding=PADDING['normal'])
        frame.pack(fill=tk.BOTH, expand=True)

        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                                font=FONTS['default'],
                                                width=70, height=30)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Populate with row data
        text_widget.insert(tk.END, "ROW DETAILS\n", 'title')
        text_widget.insert(tk.END, "=" * 60 + "\n\n", 'separator')

        for col, value in row_data.items():
            text_widget.insert(tk.END, f"{col}:\n", 'bold')
            text_widget.insert(tk.END, f"  {value}\n\n")

        # Add note if exists
        if row_idx in self.row_notes:
            text_widget.insert(tk.END, "\nNOTE:\n", 'bold')
            text_widget.insert(tk.END, f"  {self.row_notes[row_idx]}\n", 'note')

        # Configure tags
        text_widget.tag_configure('title', font=FONTS['heading'], foreground=COLORS['primary'])
        text_widget.tag_configure('separator', foreground=COLORS['default'])
        text_widget.tag_configure('bold', font=FONTS['bold'])
        text_widget.tag_configure('note', foreground=COLORS['warning'], font=FONTS['default'])

        text_widget.configure(state='disabled')

        # Close button
        button_frame = ttk.Frame(detail_window, padding=(PADDING['normal'], 0))
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Close", command=detail_window.destroy).pack(side=tk.RIGHT)

    def _copy_selected_row(self):
        """Copy selected row data to clipboard"""
        indices = self._get_selected_indices()
        if not indices:
            return

        row_idx = indices[0]
        row_data = self.original_df.iloc[row_idx]

        # Format as tab-separated values
        clipboard_text = "\t".join([f"{col}: {value}" for col, value in row_data.items()])

        self.window.clipboard_clear()
        self.window.clipboard_append(clipboard_text)

        info_dialog(self.window, "Copied", "Row data copied to clipboard")

    def _delete_selected_rows(self):
        """Delete selected rows with undo support"""
        indices = self._get_selected_indices()
        if not indices:
            warning_dialog(self.window, "No Selection", "Please select rows to delete")
            return

        if not confirm_dialog(self.window, "Delete Rows",
                             f"Delete {len(indices)} selected row(s)?"):
            return

        # Save state for undo
        self._save_state()

        # Delete rows
        self.original_df = self.original_df.drop(indices).reset_index(drop=True)
        self.df = self.df[~self.df.index.isin(indices)].reset_index(drop=True)

        # Update metadata
        for idx in indices:
            self.decoded_rows.discard(idx)
            self.important_rows.discard(idx)
            if idx in self.row_notes:
                del self.row_notes[idx]

        self._populate_table()
        info_dialog(self.window, "Deleted", f"Deleted {len(indices)} row(s)")

    def _toggle_important(self):
        """Toggle important flag for selected rows"""
        indices = self._get_selected_indices()
        if not indices:
            return

        self._save_state()

        for idx in indices:
            if idx in self.important_rows:
                self.important_rows.remove(idx)
            else:
                self.important_rows.add(idx)

        self._populate_table()

    def _edit_note(self):
        """Add or edit note for selected row"""
        indices = self._get_selected_indices()
        if not indices:
            return

        row_idx = indices[0]

        # Create note dialog
        note_dialog = tk.Toplevel(self.window)
        note_dialog.title(f"{ICONS['note']} Edit Note")
        note_dialog.geometry("500x300")
        note_dialog.transient(self.window)

        frame = ttk.Frame(note_dialog, padding=PADDING['normal'])
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Note:", font=FONTS['bold']).pack(anchor=tk.W)

        text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=60)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=PADDING['small'])

        # Load existing note if any
        if row_idx in self.row_notes:
            text_widget.insert('1.0', self.row_notes[row_idx])

        def save_note():
            self._save_state()
            note_text = text_widget.get('1.0', tk.END).strip()
            if note_text:
                self.row_notes[row_idx] = note_text
            elif row_idx in self.row_notes:
                del self.row_notes[row_idx]
            self._populate_table()
            note_dialog.destroy()

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(PADDING['normal'], 0))

        ttk.Button(button_frame, text="Save", command=save_note).pack(side=tk.RIGHT,
                                                                      padx=(PADDING['small'], 0))
        ttk.Button(button_frame, text="Cancel", command=note_dialog.destroy).pack(side=tk.RIGHT)

    def _save_state(self):
        """Save current state for undo"""
        state = {
            'df': self.original_df.copy(),
            'decoded_rows': self.decoded_rows.copy(),
            'important_rows': self.important_rows.copy(),
            'row_notes': self.row_notes.copy()
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo stack on new action
        self._update_undo_redo_buttons()

    def _undo(self):
        """Undo last operation"""
        if not self.undo_stack:
            return

        # Save current state to redo stack
        current_state = {
            'df': self.original_df.copy(),
            'decoded_rows': self.decoded_rows.copy(),
            'important_rows': self.important_rows.copy(),
            'row_notes': self.row_notes.copy()
        }
        self.redo_stack.append(current_state)

        # Restore previous state
        state = self.undo_stack.pop()
        self.original_df = state['df']
        self.df = self.original_df.copy()
        self.decoded_rows = state['decoded_rows']
        self.important_rows = state['important_rows']
        self.row_notes = state['row_notes']

        self._populate_table()
        self._update_undo_redo_buttons()

    def _redo(self):
        """Redo last undone operation"""
        if not self.redo_stack:
            return

        # Save current state to undo stack
        self._save_state()
        self.undo_stack.pop()  # Remove the state we just saved (we're redoing)

        # Restore redo state
        state = self.redo_stack.pop()
        self.original_df = state['df']
        self.df = self.original_df.copy()
        self.decoded_rows = state['decoded_rows']
        self.important_rows = state['important_rows']
        self.row_notes = state['row_notes']

        self._populate_table()
        self._update_undo_redo_buttons()

    def _update_undo_redo_buttons(self):
        """Update undo/redo button states"""
        self.undo_btn.config(state='normal' if self.undo_stack else 'disabled')
        self.redo_btn.config(state='normal' if self.redo_stack else 'disabled')

    def _export_selected(self):
        """Export only selected rows"""
        indices = self._get_selected_indices()

        if not indices:
            warning_dialog(self.window, "No Selection", "Please select rows to export")
            return

        # Get selected rows
        selected_df = self.original_df.iloc[indices]

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Selected Rows",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                selected_df.to_csv(file_path, index=False)
                info_dialog(self.window, "Success",
                          f"Saved {len(selected_df)} rows to:\n{Path(file_path).name}")
            except Exception as e:
                error_dialog(self.window, "Save Error", f"Failed to save file:\n{str(e)}")

    def _copy_to_clipboard(self):
        """Copy visible data to clipboard"""
        try:
            # Convert displayed data to TSV (tab-separated) for easy pasting into Excel
            clipboard_text = self.df[self.display_columns].to_csv(sep='\t', index=False)
            self.window.clipboard_clear()
            self.window.clipboard_append(clipboard_text)
            info_dialog(self.window, "Copied", f"Copied {len(self.df)} rows to clipboard")
        except Exception as e:
            error_dialog(self.window, "Copy Error", f"Failed to copy to clipboard:\n{str(e)}")

    def _save_as(self):
        """Save processed data"""
        if self.on_save_callback:
            self.on_save_callback(self.original_df)
            self.window.destroy()
        else:
            # Default save behavior
            file_path = filedialog.asksaveasfilename(
                title="Save Processed Orders",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                try:
                    self.original_df.to_csv(file_path, index=False)
                    info_dialog(self.window, "Success", f"File saved:\n{Path(file_path).name}")
                    self.window.destroy()
                except Exception as e:
                    error_dialog(self.window, "Save Error", f"Failed to save file:\n{str(e)}")


def show_preview(parent, dataframe: pd.DataFrame, stats: dict, on_save_callback: Optional[Callable] = None):
    """
    Convenience function to show preview window

    Args:
        parent: Parent tkinter window
        dataframe: DataFrame to preview
        stats: Statistics dictionary
        on_save_callback: Optional save callback
    """
    PreviewWindow(parent, dataframe, stats, on_save_callback)

"""Preview window for viewing decoded results before export"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import Optional, Callable


class PreviewWindow:
    """Window for previewing and confirming decoded order data"""

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

        # Create toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Preview Decoded Results")
        self.window.geometry("1200x700")

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        self._create_ui()
        self._populate_table()

    def _create_ui(self):
        """Create the UI layout"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Statistics section at top
        self._create_stats_section(main_frame)

        # Search and filter section
        self._create_filter_section(main_frame)

        # Table section
        self._create_table_section(main_frame)

        # Action buttons at bottom
        self._create_action_buttons(main_frame)

    def _create_stats_section(self, parent):
        """Create statistics display section"""
        stats_frame = ttk.LabelFrame(parent, text="Processing Summary", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Create columns for statistics
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        row = 0
        col = 0
        for key, value in self.stats.items():
            # Create label with key
            key_label = ttk.Label(stats_grid, text=f"{key}:", font=('TkDefaultFont', 9, 'bold'))
            key_label.grid(row=row, column=col*2, sticky=tk.W, padx=(0, 5))

            # Create label with value
            value_label = ttk.Label(stats_grid, text=str(value), foreground="blue")
            value_label.grid(row=row, column=col*2+1, sticky=tk.W, padx=(0, 20))

            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1

    def _create_filter_section(self, parent):
        """Create search and filter controls"""
        filter_frame = ttk.LabelFrame(parent, text="Search & Filter", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Search box
        search_container = ttk.Frame(filter_frame)
        search_container.pack(fill=tk.X)

        ttk.Label(search_container, text="Search:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._apply_filter())

        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Filter by order ID
        ttk.Label(search_container, text="Order ID:").pack(side=tk.LEFT, padx=(10, 5))

        self.order_filter_var = tk.StringVar()
        self.order_filter_var.trace('w', lambda *args: self._apply_filter())

        order_combo = ttk.Combobox(search_container, textvariable=self.order_filter_var, width=15)
        order_combo['values'] = ['(All)'] + sorted(self.df['Name'].unique().tolist())
        order_combo.current(0)
        order_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Clear filters button
        ttk.Button(search_container, text="Clear Filters", command=self._clear_filters).pack(side=tk.LEFT)

        # Results count
        self.results_label = ttk.Label(search_container, text="", foreground="gray")
        self.results_label.pack(side=tk.RIGHT, padx=(10, 0))

    def _create_table_section(self, parent):
        """Create table with scrollbars"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

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
        display_columns = ['Name', 'Lineitem sku', 'Lineitem name', 'Lineitem quantity', 'Lineitem price']

        # Filter to only include columns that exist in dataframe
        self.display_columns = [col for col in display_columns if col in self.df.columns]

        self.tree['columns'] = self.display_columns

        # Configure column headings and widths
        column_widths = {
            'Name': 100,
            'Lineitem sku': 150,
            'Lineitem name': 300,
            'Lineitem quantity': 80,
            'Lineitem price': 80
        }

        for col in self.display_columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
            width = column_widths.get(col, 150)
            self.tree.column(col, width=width, anchor=tk.W if col != 'Lineitem quantity' else tk.CENTER)

        # Bind double-click to show full row details
        self.tree.bind('<Double-1>', self._show_row_details)

    def _create_action_buttons(self, parent):
        """Create action buttons at bottom"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        ttk.Button(left_buttons, text="Export Selected Rows", command=self._export_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side=tk.LEFT)

        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        ttk.Button(right_buttons, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="Save As...", command=self._save_as, style='Accent.TButton').pack(side=tk.LEFT)

        # Configure accent button style
        style = ttk.Style()
        style.configure('Accent.TButton', foreground='blue')

    def _populate_table(self):
        """Populate table with data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows
        for idx, row in self.df.iterrows():
            values = [row[col] for col in self.display_columns]
            self.tree.insert('', tk.END, values=values, tags=(idx,))

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
                lambda x: x.str.lower().str.contains(search_text, na=False)
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
        """Sort table by column"""
        try:
            self.df = self.df.sort_values(by=column)
            self._populate_table()
        except Exception as e:
            messagebox.showerror("Sort Error", f"Could not sort by {column}: {str(e)}")

    def _update_results_count(self):
        """Update results count label"""
        total = len(self.original_df)
        shown = len(self.df)

        if shown == total:
            self.results_label.config(text=f"Showing {total} rows")
        else:
            self.results_label.config(text=f"Showing {shown} of {total} rows")

    def _show_row_details(self, event):
        """Show full details for selected row"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        row_idx = int(self.tree.item(item)['tags'][0])
        row_data = self.original_df.iloc[row_idx]

        # Create detail window
        detail_window = tk.Toplevel(self.window)
        detail_window.title("Row Details")
        detail_window.geometry("600x500")

        # Create text widget with scrollbar
        frame = ttk.Frame(detail_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=30)
        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate with row data
        for col, value in row_data.items():
            text_widget.insert(tk.END, f"{col}:\n", 'bold')
            text_widget.insert(tk.END, f"  {value}\n\n")

        text_widget.tag_configure('bold', font=('TkDefaultFont', 10, 'bold'))
        text_widget.configure(state='disabled')

        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=(0, 10))

    def _export_selected(self):
        """Export only selected rows"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select rows to export")
            return

        # Get selected row indices
        indices = [int(self.tree.item(item)['tags'][0]) for item in selection]
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
                messagebox.showinfo("Success", f"Saved {len(selected_df)} rows to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")

    def _copy_to_clipboard(self):
        """Copy visible data to clipboard"""
        try:
            # Convert displayed data to TSV (tab-separated) for easy pasting into Excel
            clipboard_text = self.df[self.display_columns].to_csv(sep='\t', index=False)
            self.window.clipboard_clear()
            self.window.clipboard_append(clipboard_text)
            messagebox.showinfo("Copied", f"Copied {len(self.df)} rows to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard:\n{str(e)}")

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
                    messagebox.showinfo("Success", f"File saved:\n{file_path}")
                    self.window.destroy()
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")


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

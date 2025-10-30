"""Profile Manager Window - UI for managing client profiles"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.client_profile import ClientProfile, create_default_profile, PLATFORM_TEMPLATES
from src.models.client_profile_manager import ClientProfileManager
from src.ui.ui_constants import COLORS, FONTS, PADDING
from src.ui.ui_utils import info_dialog, error_dialog, warning_dialog, confirm_dialog


class ProfileManagerWindow:
    """Window for managing client profiles"""

    def __init__(self, parent, profile_manager: ClientProfileManager,
                 on_profile_selected: Optional[Callable[[str], None]] = None):
        """
        Initialize profile manager window

        Args:
            parent: Parent tkinter window
            profile_manager: ClientProfileManager instance
            on_profile_selected: Callback when a profile is selected (receives client_id)
        """
        self.parent = parent
        self.profile_manager = profile_manager
        self.on_profile_selected = on_profile_selected

        # Create top-level window
        self.window = tk.Toplevel(parent)
        self.window.title("Client Profile Manager")
        self.window.geometry("900x600")
        self.window.resizable(True, True)

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()

        self._create_ui()
        self._refresh_profile_list()

        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create the UI layout"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=PADDING['normal'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top section: Config path
        self._create_config_section(main_frame)

        # Middle section: Profile list
        self._create_list_section(main_frame)

        # Bottom section: Profile details
        self._create_details_section(main_frame)

        # Button bar
        self._create_button_bar(main_frame)

    def _create_config_section(self, parent):
        """Create configuration path section"""
        config_frame = ttk.LabelFrame(parent, text="Configuration Location", padding=PADDING['normal'])
        config_frame.pack(fill=tk.X, pady=(0, PADDING['normal']))

        # Current config path
        path_frame = ttk.Frame(config_frame)
        path_frame.pack(fill=tk.X)

        ttk.Label(path_frame, text="Profiles folder:").pack(side=tk.LEFT, padx=(0, PADDING['small']))

        self.config_path_label = ttk.Label(
            path_frame,
            text=str(self.profile_manager.config_path),
            foreground=COLORS['info'],
            font=FONTS['small']
        )
        self.config_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PADDING['small'])

        # Change button
        change_btn = ttk.Button(path_frame, text="Change Location", command=self._change_config_path)
        change_btn.pack(side=tk.RIGHT)

        # Help text
        help_text = ttk.Label(
            config_frame,
            text="Tip: Set this to a network file server path to share profiles across multiple PCs",
            foreground=COLORS['info'],
            font=FONTS['small']
        )
        help_text.pack(anchor=tk.W, pady=(PADDING['tiny'], 0))

    def _create_list_section(self, parent):
        """Create profile list section"""
        list_frame = ttk.LabelFrame(parent, text="Client Profiles", padding=PADDING['normal'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['normal']))

        # Treeview for profiles
        columns = ('client_id', 'client_name', 'platform', 'has_mapping')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # Define columns
        self.tree.heading('client_id', text='Client ID')
        self.tree.heading('client_name', text='Client Name')
        self.tree.heading('platform', text='Platform')
        self.tree.heading('has_mapping', text='Has Mapping')

        self.tree.column('client_id', width=150)
        self.tree.column('client_name', width=250)
        self.tree.column('platform', width=150)
        self.tree.column('has_mapping', width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_profile_select)

        # List action buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(PADDING['small'], 0))

        ttk.Button(btn_frame, text="New Profile", command=self._new_profile, width=15).pack(pady=PADDING['tiny'])
        ttk.Button(btn_frame, text="Edit Profile", command=self._edit_profile, width=15).pack(pady=PADDING['tiny'])
        ttk.Button(btn_frame, text="Delete Profile", command=self._delete_profile, width=15).pack(pady=PADDING['tiny'])
        ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=PADDING['small'])
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_profile_list, width=15).pack(pady=PADDING['tiny'])

    def _create_details_section(self, parent):
        """Create profile details section"""
        details_frame = ttk.LabelFrame(parent, text="Profile Details", padding=PADDING['normal'])
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['normal']))

        # Details text widget
        self.details_text = tk.Text(details_frame, height=8, width=80, state='disabled', wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_button_bar(self, parent):
        """Create bottom button bar"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=(PADDING['small'], 0))
        ttk.Button(btn_frame, text="Select Profile", command=self._select_profile).pack(side=tk.RIGHT)

    def _change_config_path(self):
        """Change configuration path"""
        new_path = filedialog.askdirectory(
            title="Select Profiles Folder",
            initialdir=str(self.profile_manager.config_path)
        )

        if not new_path:
            return

        try:
            self.profile_manager.set_config_path(new_path)
            self.config_path_label.config(text=str(self.profile_manager.config_path))
            self._refresh_profile_list()
            info_dialog(self.window, "Success", f"Configuration path changed to:\n{new_path}")
        except Exception as e:
            error_dialog(self.window, "Error", f"Failed to change configuration path:\n{str(e)}")

    def _refresh_profile_list(self):
        """Refresh the profile list"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reload profiles
        self.profile_manager.reload()

        # Populate tree
        for profile in self.profile_manager.get_all_profiles():
            has_mapping = "Yes" if profile.has_column_mapping() else "No"
            self.tree.insert('', tk.END, values=(
                profile.client_id,
                profile.client_name,
                profile.platform,
                has_mapping
            ))

        # Clear details
        self._update_details(None)

    def _on_profile_select(self, event):
        """Handle profile selection"""
        selection = self.tree.selection()
        if not selection:
            self._update_details(None)
            return

        # Get selected profile
        item = selection[0]
        values = self.tree.item(item, 'values')
        client_id = values[0]

        profile = self.profile_manager.get_profile(client_id)
        self._update_details(profile)

    def _update_details(self, profile: Optional[ClientProfile]):
        """Update details panel"""
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)

        if not profile:
            self.details_text.insert('1.0', "Select a profile to view details")
        else:
            details = []
            details.append(f"Client ID: {profile.client_id}")
            details.append(f"Client Name: {profile.client_name}")
            details.append(f"Platform: {profile.platform}")
            details.append("")

            if profile.output_folder:
                details.append(f"Output Folder: {profile.output_folder}")
                details.append("")

            if profile.has_column_mapping():
                details.append("Column Mapping:")
                for client_col, std_col in profile.column_mapping.items():
                    details.append(f"  {client_col} → {std_col}")
            else:
                details.append("No column mapping (using standard column names)")

            self.details_text.insert('1.0', '\n'.join(details))

        self.details_text.config(state='disabled')

    def _new_profile(self):
        """Create new profile"""
        dialog = ProfileEditDialog(self.window, self.profile_manager, mode='new')
        self.window.wait_window(dialog.window)

        if dialog.result:
            self._refresh_profile_list()

    def _edit_profile(self):
        """Edit selected profile"""
        selection = self.tree.selection()
        if not selection:
            warning_dialog(self.window, "No Selection", "Please select a profile to edit")
            return

        # Get selected profile
        item = selection[0]
        values = self.tree.item(item, 'values')
        client_id = values[0]

        profile = self.profile_manager.get_profile(client_id)
        if not profile:
            error_dialog(self.window, "Error", "Profile not found")
            return

        dialog = ProfileEditDialog(self.window, self.profile_manager, mode='edit', profile=profile)
        self.window.wait_window(dialog.window)

        if dialog.result:
            self._refresh_profile_list()

    def _delete_profile(self):
        """Delete selected profile"""
        selection = self.tree.selection()
        if not selection:
            warning_dialog(self.window, "No Selection", "Please select a profile to delete")
            return

        # Get selected profile
        item = selection[0]
        values = self.tree.item(item, 'values')
        client_id = values[0]
        client_name = values[1]

        if not confirm_dialog(
            self.window,
            "Confirm Delete",
            f"Are you sure you want to delete profile:\n{client_name} ({client_id})?"
        ):
            return

        try:
            self.profile_manager.delete_profile(client_id)
            self._refresh_profile_list()
            info_dialog(self.window, "Success", f"Profile '{client_name}' deleted successfully")
        except Exception as e:
            error_dialog(self.window, "Error", f"Failed to delete profile:\n{str(e)}")

    def _select_profile(self):
        """Select current profile and close window"""
        selection = self.tree.selection()
        if not selection:
            warning_dialog(self.window, "No Selection", "Please select a profile")
            return

        # Get selected profile
        item = selection[0]
        values = self.tree.item(item, 'values')
        client_id = values[0]

        if self.on_profile_selected:
            self.on_profile_selected(client_id)

        self.window.destroy()


class ProfileEditDialog:
    """Dialog for creating/editing a profile"""

    def __init__(self, parent, profile_manager: ClientProfileManager,
                 mode: str = 'new', profile: Optional[ClientProfile] = None):
        """
        Initialize profile edit dialog

        Args:
            parent: Parent window
            profile_manager: ClientProfileManager instance
            mode: 'new' or 'edit'
            profile: ClientProfile to edit (for edit mode)
        """
        self.parent = parent
        self.profile_manager = profile_manager
        self.mode = mode
        self.profile = profile
        self.result = None

        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("New Profile" if mode == 'new' else "Edit Profile")
        self.window.geometry("700x550")
        self.window.resizable(False, False)

        # Make modal
        self.window.transient(parent)
        self.window.grab_set()

        self._create_ui()
        self._load_profile_data()

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create UI"""
        main_frame = ttk.Frame(self.window, padding=PADDING['normal'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Basic info section
        basic_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding=PADDING['normal'])
        basic_frame.pack(fill=tk.X, pady=(0, PADDING['normal']))

        # Client ID
        ttk.Label(basic_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.client_id_entry = ttk.Entry(basic_frame, width=40)
        self.client_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=PADDING['small'])
        if self.mode == 'edit':
            self.client_id_entry.config(state='disabled')

        # Client Name
        ttk.Label(basic_frame, text="Client Name:").grid(row=1, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.client_name_entry = ttk.Entry(basic_frame, width=40)
        self.client_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=PADDING['small'])

        # Platform
        ttk.Label(basic_frame, text="Platform:").grid(row=2, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.platform_var = tk.StringVar(value='Shopify')
        platform_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.platform_var,
            values=list(PLATFORM_TEMPLATES.keys()),
            state='readonly',
            width=37
        )
        platform_combo.grid(row=2, column=1, sticky=tk.W, padx=PADDING['small'])
        platform_combo.bind('<<ComboboxSelected>>', self._on_platform_change)

        # Output Folder
        ttk.Label(basic_frame, text="Output Folder:").grid(row=3, column=0, sticky=tk.W, pady=PADDING['tiny'])
        folder_frame = ttk.Frame(basic_frame)
        folder_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=PADDING['small'])
        self.output_folder_entry = ttk.Entry(folder_frame)
        self.output_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder, width=10).pack(side=tk.RIGHT, padx=(PADDING['small'], 0))

        basic_frame.columnconfigure(1, weight=1)

        # Column mapping section
        mapping_frame = ttk.LabelFrame(main_frame, text="Column Mapping", padding=PADDING['normal'])
        mapping_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['normal']))

        # Instructions
        ttk.Label(
            mapping_frame,
            text="Map client-specific column names to standard column names:",
            foreground=COLORS['info']
        ).pack(anchor=tk.W, pady=(0, PADDING['small']))

        # Mapping entries frame with scrollbar
        mapping_canvas_frame = ttk.Frame(mapping_frame)
        mapping_canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(mapping_canvas_frame, height=200)
        scrollbar = ttk.Scrollbar(mapping_canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.mapping_entries_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=self.mapping_entries_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Update scroll region when frame changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.mapping_entries_frame.bind("<Configure>", on_frame_configure)

        # Store mapping entries
        self.mapping_entries = []

        # Add mapping button
        ttk.Button(mapping_frame, text="Add Mapping", command=self._add_mapping_row).pack(pady=(PADDING['small'], 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=(PADDING['small'], 0))
        ttk.Button(btn_frame, text="Save", command=self._save_profile).pack(side=tk.RIGHT)

    def _load_profile_data(self):
        """Load profile data into fields"""
        if self.mode == 'edit' and self.profile:
            self.client_id_entry.insert(0, self.profile.client_id)
            self.client_name_entry.insert(0, self.profile.client_name)
            self.platform_var.set(self.profile.platform)

            if self.profile.output_folder:
                self.output_folder_entry.insert(0, self.profile.output_folder)

            # Load mappings
            for client_col, std_col in self.profile.column_mapping.items():
                self._add_mapping_row(client_col, std_col)

    def _on_platform_change(self, event):
        """Handle platform change"""
        platform = self.platform_var.get()
        if platform in PLATFORM_TEMPLATES:
            template = PLATFORM_TEMPLATES[platform]
            # Clear existing mappings
            for entry_pair in self.mapping_entries:
                entry_pair[2].destroy()  # Destroy the frame
            self.mapping_entries.clear()

            # Load template mappings
            for client_col, std_col in template.column_mapping.items():
                self._add_mapping_row(client_col, std_col)

    def _browse_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder)

    def _add_mapping_row(self, client_col: str = "", std_col: str = ""):
        """Add a row for column mapping"""
        row_frame = ttk.Frame(self.mapping_entries_frame)
        row_frame.pack(fill=tk.X, pady=PADDING['tiny'])

        ttk.Label(row_frame, text="Client column:").pack(side=tk.LEFT, padx=(0, PADDING['small']))
        client_entry = ttk.Entry(row_frame, width=25)
        client_entry.pack(side=tk.LEFT, padx=(0, PADDING['small']))
        client_entry.insert(0, client_col)

        ttk.Label(row_frame, text="→").pack(side=tk.LEFT, padx=PADDING['tiny'])

        ttk.Label(row_frame, text="Standard column:").pack(side=tk.LEFT, padx=(PADDING['small'], PADDING['tiny']))
        std_entry = ttk.Entry(row_frame, width=25)
        std_entry.pack(side=tk.LEFT, padx=(0, PADDING['small']))
        std_entry.insert(0, std_col)

        # Remove button
        def remove():
            row_frame.destroy()
            self.mapping_entries.remove((client_entry, std_entry, row_frame))

        ttk.Button(row_frame, text="Remove", command=remove, width=10).pack(side=tk.RIGHT)

        self.mapping_entries.append((client_entry, std_entry, row_frame))

    def _save_profile(self):
        """Save the profile"""
        try:
            # Get values
            client_id = self.client_id_entry.get().strip()
            client_name = self.client_name_entry.get().strip()
            platform = self.platform_var.get()
            output_folder = self.output_folder_entry.get().strip() or None

            if not client_id:
                error_dialog(self.window, "Validation Error", "Client ID is required")
                return

            if not client_name:
                error_dialog(self.window, "Validation Error", "Client Name is required")
                return

            # Build column mapping
            column_mapping = {}
            for client_entry, std_entry, _ in self.mapping_entries:
                client_col = client_entry.get().strip()
                std_col = std_entry.get().strip()
                if client_col and std_col:
                    column_mapping[client_col] = std_col

            # Create profile
            if self.mode == 'new':
                profile = ClientProfile(
                    client_id=client_id,
                    client_name=client_name,
                    column_mapping=column_mapping,
                    output_folder=output_folder,
                    platform=platform
                )
                self.profile_manager.add_profile(profile)
                info_dialog(self.window, "Success", "Profile created successfully")
            else:
                # Update existing profile
                self.profile.client_name = client_name
                self.profile.platform = platform
                self.profile.column_mapping = column_mapping
                self.profile.output_folder = output_folder
                self.profile_manager.update_profile(self.profile)
                info_dialog(self.window, "Success", "Profile updated successfully")

            self.result = True
            self.window.destroy()

        except Exception as e:
            error_dialog(self.window, "Error", f"Failed to save profile:\n{str(e)}")


def show_profile_manager(parent, profile_manager: ClientProfileManager,
                         on_profile_selected: Optional[Callable[[str], None]] = None):
    """
    Show profile manager window

    Args:
        parent: Parent tkinter window
        profile_manager: ClientProfileManager instance
        on_profile_selected: Callback when profile is selected
    """
    ProfileManagerWindow(parent, profile_manager, on_profile_selected)

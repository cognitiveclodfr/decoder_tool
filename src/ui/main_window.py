"""Main GUI window for Decoder Tool application v2.2 - Enhanced Edition"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.product_manager import ProductManager
from src.models.set_manager import SetManager
from src.models.order_processor import OrderProcessor
from src.utils.file_handlers import MasterFileLoader, OrdersFileLoader
from src.ui.preview_window import show_preview
from src.ui.ui_constants import ICONS, COLORS, TOOLTIPS, FONTS, PADDING, WINDOW_SIZES, STATUS_MESSAGES
from src.ui.ui_utils import (ToolTip, create_button_with_icon, StatusBar, set_status_color,
                              show_context_menu, confirm_dialog, info_dialog, error_dialog, warning_dialog)
from src.utils.file_history import FileHistory
from src.utils.error_logger import ErrorLogger, CrashRecovery, get_logger


class DecoderToolApp:
    """Main application window for Decoder Tool v2.2"""

    def __init__(self, root):
        """
        Initialize the application

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title(f"Shopify Order Set Decoder Tool v2.2")
        self.root.geometry(WINDOW_SIZES['main'])
        self.root.resizable(True, True)

        # Initialize error logger and crash recovery
        self.logger = get_logger()
        self.crash_recovery = CrashRecovery()
        self.logger.log_info("Application started", "MainWindow")

        # Check for crash recovery
        self._check_crash_recovery()

        # Initialize file history
        self.file_history = FileHistory()

        # Initialize managers
        self.product_manager = ProductManager()
        self.set_manager = SetManager()
        self.order_processor = OrderProcessor(self.product_manager, self.set_manager)

        # State tracking
        self.master_loaded = False
        self.orders_loaded = False
        self.current_master_file = None
        self.current_orders_files = []

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Set up auto-save
        self._setup_autosave()

        # Create UI
        self._create_ui()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.logger.log_info("UI initialized successfully", "MainWindow")

    def _check_crash_recovery(self):
        """Check if there's a crash recovery state"""
        if self.crash_recovery.has_recovery_state():
            if messagebox.askyesno(
                "Crash Recovery",
                "A previous session was not closed properly. Do you want to restore the last state?",
                icon='warning'
            ):
                state = self.crash_recovery.load_state()
                if state:
                    self.logger.log_info("Restored previous session state", "CrashRecovery")
                    # Restore master file if available
                    if 'master_file' in state and Path(state['master_file']).exists():
                        self.current_master_file = state['master_file']
                    # Restore orders if available
                    if 'orders_files' in state:
                        self.current_orders_files = [f for f in state['orders_files'] if Path(f).exists()]

            # Clear recovery state after check
            self.crash_recovery.clear_state()

    def _setup_autosave(self):
        """Set up periodic auto-save of application state"""
        def autosave():
            try:
                state = {
                    'master_file': self.current_master_file,
                    'orders_files': self.current_orders_files,
                    'master_loaded': self.master_loaded,
                    'orders_loaded': self.orders_loaded,
                }
                self.crash_recovery.save_state(state)
            except Exception as e:
                self.logger.log_error(f"Autosave failed: {str(e)}", "Autosave")
            finally:
                # Schedule next autosave in 60 seconds
                self.root.after(60000, autosave)

        # Start autosave after 60 seconds
        self.root.after(60000, autosave)

    def _create_ui(self):
        """Create the main UI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=PADDING['normal'])
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        current_row = 0

        # Section 1: Master File
        self._create_master_file_section(main_frame, row=current_row)
        current_row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=current_row, column=0, sticky=(tk.W, tk.E), pady=PADDING['normal']
        )
        current_row += 1

        # Section 2: Orders
        self._create_orders_section(main_frame, row=current_row)
        current_row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=current_row, column=0, sticky=(tk.W, tk.E), pady=PADDING['normal']
        )
        current_row += 1

        # Section 2.5: Data Processing Utilities
        self._create_utilities_section(main_frame, row=current_row)
        current_row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=current_row, column=0, sticky=(tk.W, tk.E), pady=PADDING['normal']
        )
        current_row += 1

        # Section 3: Process & Save
        self._create_process_section(main_frame, row=current_row)
        current_row += 1

        # Status bar at bottom
        self._create_status_bar(main_frame, row=current_row)

    def _create_master_file_section(self, parent, row):
        """Create Section 1: Master File Loading with enhanced features"""
        section = ttk.LabelFrame(parent, text=f"{ICONS['excel']} Section 1: Load Master File",
                                padding=PADDING['normal'], style='Enhanced.TLabelframe')
        section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=PADDING['small'])
        section.columnconfigure(2, weight=1)

        # Buttons frame
        buttons_frame = ttk.Frame(section)
        buttons_frame.grid(row=0, column=0, sticky=tk.W, padx=PADDING['small'])

        # Load button
        load_btn = create_button_with_icon(
            buttons_frame, "Load Master File", ICONS['load'],
            self._load_master_file, TOOLTIPS['load_master']
        )
        load_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        # Reload button
        self.reload_master_btn = create_button_with_icon(
            buttons_frame, "Reload", ICONS['reload'],
            self._reload_master_file, TOOLTIPS['reload_master']
        )
        self.reload_master_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))
        self.reload_master_btn.config(state='disabled')

        # Pin button
        self.pin_master_btn = create_button_with_icon(
            buttons_frame, "Pin", ICONS['pin'],
            self._toggle_pin_master, TOOLTIPS['pin_master']
        )
        self.pin_master_btn.pack(side=tk.LEFT)
        self.pin_master_btn.config(state='disabled')

        # Status label with color coding
        self.master_status_label = ttk.Label(section, text=STATUS_MESSAGES['no_master'],
                                            font=FONTS['default'])
        self.master_status_label.grid(row=0, column=1, sticky=tk.W, padx=PADDING['normal'])
        set_status_color(self.master_status_label, 'default')

        # Recent/Favorites menu button
        recent_btn = ttk.Menubutton(section, text=f"{ICONS['folder']} Recent & Favorites")
        recent_btn.grid(row=0, column=2, sticky=tk.E, padx=PADDING['small'])
        self.master_recent_menu = tk.Menu(recent_btn, tearoff=0)
        recent_btn['menu'] = self.master_recent_menu
        self._update_master_recent_menu()

        # Context menu for master file section
        self._create_master_context_menu()

    def _create_orders_section(self, parent, row):
        """Create Section 2: Orders Loading with enhanced features"""
        section = ttk.LabelFrame(parent, text=f"{ICONS['csv']} Section 2: Load Orders & Add Products",
                                padding=PADDING['normal'])
        section.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N), pady=PADDING['small'])
        section.columnconfigure(2, weight=1)

        # Load buttons frame
        load_frame = ttk.Frame(section)
        load_frame.grid(row=0, column=0, sticky=tk.W, padx=PADDING['small'], pady=PADDING['small'])

        # Load single file button
        load_single_btn = create_button_with_icon(
            load_frame, "Load Single CSV", ICONS['file'],
            self._load_orders, TOOLTIPS['load_single']
        )
        load_single_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        # Load folder button
        load_folder_btn = create_button_with_icon(
            load_frame, "Load Folder", ICONS['folder'],
            self._load_orders_folder, TOOLTIPS['load_folder']
        )
        load_folder_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))

        # Reload button
        self.reload_orders_btn = create_button_with_icon(
            load_frame, "Reload", ICONS['reload'],
            self._reload_orders, TOOLTIPS['reload_orders']
        )
        self.reload_orders_btn.pack(side=tk.LEFT)
        self.reload_orders_btn.config(state='disabled')

        # Orders status label with color coding
        self.orders_status_label = ttk.Label(section, text=STATUS_MESSAGES['no_orders'],
                                            font=FONTS['default'])
        self.orders_status_label.grid(row=0, column=1, sticky=tk.W, padx=PADDING['normal'])
        set_status_color(self.orders_status_label, 'default')

        # Manual addition subsection
        manual_frame = ttk.LabelFrame(section, text=f"{ICONS['add']} Manually Add Product to Order",
                                      padding=PADDING['small'])
        manual_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=PADDING['normal'])
        manual_frame.columnconfigure(1, weight=1)

        # Order ID field
        ttk.Label(manual_frame, text="Order ID:").grid(row=0, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.order_id_entry = ttk.Entry(manual_frame, width=20)
        self.order_id_entry.grid(row=0, column=1, sticky=tk.W, padx=PADDING['small'])
        ToolTip(self.order_id_entry, "Enter order ID (e.g., #76360)")

        # SKU field
        ttk.Label(manual_frame, text="SKU:").grid(row=1, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.sku_entry = ttk.Entry(manual_frame, width=20)
        self.sku_entry.grid(row=1, column=1, sticky=tk.W, padx=PADDING['small'])
        ToolTip(self.sku_entry, "Enter product SKU to add")

        # Quantity field
        ttk.Label(manual_frame, text="Quantity:").grid(row=2, column=0, sticky=tk.W, pady=PADDING['tiny'])
        self.quantity_entry = ttk.Entry(manual_frame, width=20)
        self.quantity_entry.grid(row=2, column=1, sticky=tk.W, padx=PADDING['small'])
        ToolTip(self.quantity_entry, "Enter quantity to add")

        # Add button
        add_btn = create_button_with_icon(
            manual_frame, "Add Product", ICONS['add'],
            self._add_manual_product, TOOLTIPS['add_product']
        )
        add_btn.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=PADDING['normal'])

    def _create_utilities_section(self, parent, row):
        """Create Section 2.5: Data Processing Utilities with enhanced validation"""
        section = ttk.LabelFrame(parent, text=f"{ICONS['process']} Data Processing Utilities",
                                padding=PADDING['normal'])
        section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=PADDING['small'])
        section.columnconfigure(1, weight=1)

        # Generate SKU button
        sku_btn = create_button_with_icon(
            section, "Generate Missing SKUs", ICONS['generate'],
            self._generate_skus, TOOLTIPS['generate_skus']
        )
        sku_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, PADDING['small']), pady=PADDING['tiny'])

        # Validate button
        validate_btn = create_button_with_icon(
            section, "Validate Data", ICONS['validate'],
            self._validate_data_enhanced, TOOLTIPS['validate']
        )
        validate_btn.grid(row=1, column=0, sticky=tk.W, padx=(0, PADDING['small']), pady=PADDING['tiny'])

        # Check duplicates button
        dup_btn = create_button_with_icon(
            section, "Check Duplicates", ICONS['search'],
            self._check_duplicates, TOOLTIPS['check_duplicates']
        )
        dup_btn.grid(row=2, column=0, sticky=tk.W, padx=(0, PADDING['small']), pady=PADDING['tiny'])

        # Statistics label
        self.utils_status_label = ttk.Label(section, text="", font=FONTS['default'])
        self.utils_status_label.grid(row=0, column=1, rowspan=3, sticky=(tk.W, tk.N), padx=PADDING['normal'])

    def _create_process_section(self, parent, row):
        """Create Section 3: Process and Save with enhanced preview"""
        section = ttk.LabelFrame(parent, text=f"{ICONS['preview']} Section 3: Process & Save",
                                padding=PADDING['large'])
        section.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=PADDING['small'])
        section.columnconfigure(0, weight=1)

        # Main action button (larger and centered)
        button_frame = ttk.Frame(section)
        button_frame.pack(pady=PADDING['normal'])

        preview_btn = create_button_with_icon(
            button_frame, "Preview & Save Results", ICONS['preview'],
            self._preview_results, TOOLTIPS['preview_save'],
            width=25
        )
        preview_btn.pack()

        # Help text
        help_label = ttk.Label(
            section,
            text="Process all orders, decode sets, and preview results before saving",
            foreground=COLORS['info'],
            font=FONTS['default']
        )
        help_label.pack(pady=PADDING['tiny'])

        # Info panel with current state
        info_frame = ttk.Frame(section)
        info_frame.pack(fill=tk.X, pady=PADDING['normal'], padx=PADDING['xlarge'])

        # Quick stats/info
        self.process_info_label = ttk.Label(
            info_frame,
            text="Load master file and orders to begin processing",
            foreground=COLORS['default'],
            font=FONTS['small'],
            justify=tk.CENTER
        )
        self.process_info_label.pack()

    def _update_process_info(self):
        """Update process section info label with current state"""
        if hasattr(self, 'process_info_label'):
            if self.master_loaded and self.orders_loaded:
                product_count = len(self.product_manager._products)
                set_count = len(self.set_manager._sets)
                order_count = len(self.order_processor.get_orders_dataframe())

                info_text = (f"{ICONS['ok']} Ready to process: "
                           f"{product_count} products, {set_count} sets, {order_count} order rows")
                self.process_info_label.config(text=info_text, foreground=COLORS['success'])
            elif self.master_loaded:
                self.process_info_label.config(
                    text=f"{ICONS['info']} Master file loaded. Please load orders to continue.",
                    foreground=COLORS['info']
                )
            elif self.orders_loaded:
                self.process_info_label.config(
                    text=f"{ICONS['warning']} Orders loaded. Please load master file to continue.",
                    foreground=COLORS['warning']
                )
            else:
                self.process_info_label.config(
                    text="Load master file and orders to begin processing",
                    foreground=COLORS['default']
                )

    def _create_status_bar(self, parent, row):
        """Create enhanced status bar with multiple sections"""
        self.status_bar = StatusBar(parent)
        self.status_bar.frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(PADDING['normal'], 0))

        # Initial status
        self.status_bar.set_status("Ready", 'success')
        self.logger.log_debug("Status bar initialized", "StatusBar")

    def _update_status(self, message: str, status_type: str = 'default',
                      info: str = "", counter: str = ""):
        """
        Update status bar with message and optional info/counter

        Args:
            message: Main status message
            status_type: Status type for color coding
            info: Optional info message (center)
            counter: Optional counter text (right)
        """
        self.status_bar.set_status(message, status_type)
        if info:
            self.status_bar.set_info(info)
        if counter:
            self.status_bar.set_counter(counter)
        self.root.update_idletasks()

    # ==================== Master File Operations ====================

    def _load_master_file(self):
        """Load master file with error handling and history tracking"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Master File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir=str(Path.home())
            )

            if not file_path:
                return

            self._update_status("Loading master file...", 'info')
            self.logger.log_info(f"Loading master file: {file_path}", "MasterFile")

            # Load products and sets
            products_df, sets_df = MasterFileLoader.load(file_path)

            self.product_manager.clear()
            self.product_manager.load_from_dataframe(products_df)

            self.set_manager.clear()
            self.set_manager.load_from_dataframe(sets_df)

            # Update state
            self.master_loaded = True
            self.current_master_file = file_path

            # Add to history
            self.file_history.add_recent(file_path, 'master')
            self._update_master_recent_menu()

            # Update UI
            file_name = Path(file_path).name
            status_text = f"{ICONS['ok']} Master file loaded: {file_name}"
            self.master_status_label.config(text=status_text)
            self._update_process_info()
            set_status_color(self.master_status_label, 'success')

            # Enable reload and pin buttons
            self.reload_master_btn.config(state='normal')
            self.pin_master_btn.config(state='normal')
            self._update_pin_button_text()

            # Update status bar
            product_count = self.product_manager.count()
            set_count = self.set_manager.count()
            self._update_status(
                "Master file loaded successfully", 'success',
                info=f"{product_count} products, {set_count} sets loaded"
            )

            self.logger.log_info(f"Master file loaded: {product_count} products, {set_count} sets", "MasterFile")

            info_dialog(self.root, "Success",
                       f"Master file loaded successfully!\n\n"
                       f"Products: {product_count}\n"
                       f"Sets: {set_count}")

        except Exception as e:
            self.logger.log_exception(e, "Load Master File")
            self._update_status(f"Error loading master file", 'error')
            error_dialog(self.root, "Error", f"Failed to load master file:\n{str(e)}")

    def _reload_master_file(self):
        """Reload the current master file"""
        if not self.current_master_file or not Path(self.current_master_file).exists():
            error_dialog(self.root, "Error", "No master file to reload or file not found")
            return

        try:
            self._update_status("Reloading master file...", 'info')
            self.logger.log_info(f"Reloading master file: {self.current_master_file}", "MasterFile")

            # Save current file path
            file_path = self.current_master_file

            # Load products and sets
            products_df, sets_df = MasterFileLoader.load(file_path)

            self.product_manager.clear()
            self.product_manager.load_from_dataframe(products_df)

            self.set_manager.clear()
            self.set_manager.load_from_dataframe(sets_df)

            # Update status
            product_count = self.product_manager.count()
            set_count = self.set_manager.count()

            self._update_status(
                "Master file reloaded", 'success',
                info=f"{product_count} products, {set_count} sets"
            )

            self.logger.log_info(f"Master file reloaded successfully", "MasterFile")

            info_dialog(self.root, "Success", f"Master file reloaded!\n\n"
                       f"Products: {product_count}\nSets: {set_count}")

        except Exception as e:
            self.logger.log_exception(e, "Reload Master File")
            error_dialog(self.root, "Error", f"Failed to reload master file:\n{str(e)}")

    def _toggle_pin_master(self):
        """Toggle pin/unpin for current master file"""
        if not self.current_master_file:
            return

        try:
            if self.file_history.is_favorite(self.current_master_file):
                # Unpin
                self.file_history.remove_favorite(self.current_master_file)
                self.logger.log_info(f"Unpinned: {self.current_master_file}", "Favorites")
                info_dialog(self.root, "Unpinned", "Master file removed from favorites")
            else:
                # Pin
                nickname = Path(self.current_master_file).stem
                self.file_history.add_favorite(self.current_master_file, 'master', nickname)
                self.logger.log_info(f"Pinned: {self.current_master_file}", "Favorites")
                info_dialog(self.root, "Pinned", "Master file added to favorites!")

            self._update_pin_button_text()
            self._update_master_recent_menu()

        except Exception as e:
            self.logger.log_exception(e, "Toggle Pin")
            error_dialog(self.root, "Error", f"Failed to pin/unpin file:\n{str(e)}")

    def _update_pin_button_text(self):
        """Update pin button text based on current state"""
        if self.current_master_file and self.file_history.is_favorite(self.current_master_file):
            self.pin_master_btn.config(text=f"{ICONS['unpin']} Unpin")
        else:
            self.pin_master_btn.config(text=f"{ICONS['pin']} Pin")

    def _update_master_recent_menu(self):
        """Update recent/favorites menu for master files"""
        self.master_recent_menu.delete(0, 'end')

        # Add favorites
        favorites = self.file_history.get_favorites('master')
        if favorites:
            self.master_recent_menu.add_command(label="=== FAVORITES ===", state='disabled')
            for fav in favorites:
                file_path = fav['path']
                nickname = fav.get('nickname', Path(file_path).name)
                self.master_recent_menu.add_command(
                    label=f"{ICONS['favorite']} {nickname}",
                    command=lambda f=file_path: self._load_master_from_path(f)
                )

        # Add recent files
        recent = self.file_history.get_recent('master', limit=5)
        if recent:
            if favorites:
                self.master_recent_menu.add_separator()
            self.master_recent_menu.add_command(label="=== RECENT ===", state='disabled')
            for recent_file in recent:
                file_path = recent_file['path']
                file_name = Path(file_path).name
                self.master_recent_menu.add_command(
                    label=f"{ICONS['file']} {file_name}",
                    command=lambda f=file_path: self._load_master_from_path(f)
                )

        if not favorites and not recent:
            self.master_recent_menu.add_command(label="No recent files", state='disabled')

        # Add clear history option
        if recent:
            self.master_recent_menu.add_separator()
            self.master_recent_menu.add_command(
                label="Clear History",
                command=self._clear_master_history
            )

    def _load_master_from_path(self, file_path: str):
        """Load master file from specific path"""
        if not Path(file_path).exists():
            error_dialog(self.root, "Error", f"File not found:\n{file_path}")
            self.file_history.remove_recent(file_path)
            self._update_master_recent_menu()
            return

        try:
            self._update_status(f"Loading {Path(file_path).name}...", 'info')

            products_df, sets_df = MasterFileLoader.load(file_path)

            self.product_manager.clear()
            self.product_manager.load_from_dataframe(products_df)

            self.set_manager.clear()
            self.set_manager.load_from_dataframe(sets_df)

            self.master_loaded = True
            self.current_master_file = file_path

            self.file_history.add_recent(file_path, 'master')
            self._update_master_recent_menu()

            file_name = Path(file_path).name
            self.master_status_label.config(text=f"{ICONS['ok']} Loaded: {file_name}")
            set_status_color(self.master_status_label, 'success')

            self.reload_master_btn.config(state='normal')
            self.pin_master_btn.config(state='normal')
            self._update_pin_button_text()

            product_count = self.product_manager.count()
            set_count = self.set_manager.count()
            self._update_status(
                "Master file loaded", 'success',
                info=f"{product_count} products, {set_count} sets"
            )

        except Exception as e:
            self.logger.log_exception(e, "Load Master from Path")
            error_dialog(self.root, "Error", f"Failed to load file:\n{str(e)}")

    def _clear_master_history(self):
        """Clear master file history"""
        if confirm_dialog(self.root, "Clear History", "Clear all recent master files from history?"):
            self.file_history.clear_recent()
            self._update_master_recent_menu()
            info_dialog(self.root, "Cleared", "History cleared successfully")

    def _create_master_context_menu(self):
        """Create context menu for master file section"""
        self.master_context_menu = tk.Menu(self.root, tearoff=0)
        self.master_context_menu.add_command(
            label=f"{ICONS['reload']} Reload File",
            command=self._reload_master_file
        )
        self.master_context_menu.add_command(
            label=f"{ICONS['info']} View File Info",
            command=self._show_master_info
        )
        self.master_context_menu.add_separator()
        self.master_context_menu.add_command(
            label=f"{ICONS['folder']} Open Location",
            command=self._open_master_location
        )

    def _show_master_info(self):
        """Show detailed info about loaded master file"""
        if not self.master_loaded:
            info_dialog(self.root, "No File Loaded", "No master file is currently loaded")
            return

        product_count = self.product_manager.count()
        set_count = self.set_manager.count()
        all_sets = self.set_manager.get_all_set_skus()

        info_text = f"Master File Information\n\n"
        info_text += f"File: {Path(self.current_master_file).name}\n"
        info_text += f"Location: {self.current_master_file}\n\n"
        info_text += f"Products loaded: {product_count}\n"
        info_text += f"Sets defined: {set_count}\n\n"
        info_text += f"Set SKUs: {', '.join(all_sets[:10])}"
        if len(all_sets) > 10:
            info_text += f"... (+{len(all_sets) - 10} more)"

        info_dialog(self.root, "Master File Info", info_text)

    def _open_master_location(self):
        """Open folder containing master file"""
        if not self.current_master_file:
            return

        try:
            folder = Path(self.current_master_file).parent
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        except Exception as e:
            self.logger.log_exception(e, "Open Location")
            error_dialog(self.root, "Error", f"Failed to open folder:\n{str(e)}")

    # ==================== Orders Operations ====================

    def _load_orders(self):
        """Load single CSV orders file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Orders CSV File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=str(Path.home())
            )

            if not file_path:
                return

            self._update_status("Loading orders...", 'info')
            self.logger.log_info(f"Loading orders: {file_path}", "Orders")

            orders_df = OrdersFileLoader.load(file_path)
            self.order_processor.load_orders(orders_df)

            self.orders_loaded = True
            self.current_orders_files = [file_path]

            file_name = Path(file_path).name
            row_count = len(orders_df)
            order_count = orders_df['Name'].nunique() if 'Name' in orders_df.columns else row_count

            self.orders_status_label.config(text=f"{ICONS['ok']} Loaded: {file_name}")
            set_status_color(self.orders_status_label, 'success')
            self._update_process_info()

            self.reload_orders_btn.config(state='normal')

            self._update_status(
                "Orders loaded successfully", 'success',
                counter=f"{row_count} rows, {order_count} orders"
            )

            self.logger.log_info(f"Orders loaded: {row_count} rows, {order_count} orders", "Orders")

            info_dialog(self.root, "Success",
                       f"Orders loaded successfully!\n\n"
                       f"Total rows: {row_count}\n"
                       f"Unique orders: {order_count}")

        except Exception as e:
            self.logger.log_exception(e, "Load Orders")
            self._update_status("Error loading orders", 'error')
            error_dialog(self.root, "Error", f"Failed to load orders:\n{str(e)}")

    def _load_orders_folder(self):
        """Load multiple CSV files from folder"""
        try:
            folder_path = filedialog.askdirectory(
                title="Select Folder with CSV Files",
                initialdir=str(Path.home())
            )

            if not folder_path:
                return

            self._update_status("Loading orders from folder...", 'info')
            self.logger.log_info(f"Loading orders from folder: {folder_path}", "Orders")

            orders_df, file_names = OrdersFileLoader.load_from_folder(folder_path)
            self.order_processor.load_orders(orders_df)

            self.orders_loaded = True
            self.current_orders_files = [str(Path(folder_path) / name) for name in file_names]

            row_count = len(orders_df)
            order_count = orders_df['Name'].nunique() if 'Name' in orders_df.columns else row_count
            file_count = len(file_names)

            self.orders_status_label.config(text=f"{ICONS['ok']} Loaded {file_count} files from folder")
            set_status_color(self.orders_status_label, 'success')
            self._update_process_info()

            self.reload_orders_btn.config(state='normal')

            self._update_status(
                f"Loaded {file_count} CSV files", 'success',
                counter=f"{row_count} rows, {order_count} orders"
            )

            files_list = "\n".join([f"  • {name}" for name in file_names[:10]])
            if len(file_names) > 10:
                files_list += f"\n  ... and {len(file_names) - 10} more"

            info_dialog(self.root, "Success",
                       f"Loaded {file_count} CSV files!\n\n"
                       f"Files:\n{files_list}\n\n"
                       f"Total rows: {row_count}\n"
                       f"Unique orders: {order_count}")

            self.logger.log_info(f"Loaded {file_count} files: {row_count} rows, {order_count} orders", "Orders")

        except Exception as e:
            self.logger.log_exception(e, "Load Orders Folder")
            self._update_status("Error loading folder", 'error')
            error_dialog(self.root, "Error", f"Failed to load orders folder:\n{str(e)}")

    def _reload_orders(self):
        """Reload current orders files"""
        if not self.current_orders_files:
            error_dialog(self.root, "Error", "No orders to reload")
            return

        try:
            self._update_status("Reloading orders...", 'info')
            self.logger.log_info("Reloading orders", "Orders")

            if len(self.current_orders_files) == 1:
                orders_df = OrdersFileLoader.load(self.current_orders_files[0])
            else:
                orders_df = OrdersFileLoader.load_multiple(self.current_orders_files)

            self.order_processor.load_orders(orders_df)

            row_count = len(orders_df)
            order_count = orders_df['Name'].nunique() if 'Name' in orders_df.columns else row_count

            self._update_status(
                "Orders reloaded", 'success',
                counter=f"{row_count} rows, {order_count} orders"
            )

            info_dialog(self.root, "Success",
                       f"Orders reloaded!\n\n"
                       f"Total rows: {row_count}\n"
                       f"Unique orders: {order_count}")

        except Exception as e:
            self.logger.log_exception(e, "Reload Orders")
            error_dialog(self.root, "Error", f"Failed to reload orders:\n{str(e)}")

    def _add_manual_product(self):
        """Add product manually to order"""
        try:
            order_id = self.order_id_entry.get().strip()
            sku = self.sku_entry.get().strip()
            quantity = self.quantity_entry.get().strip()

            if not all([order_id, sku, quantity]):
                warning_dialog(self.root, "Missing Information",
                             "Please fill in all fields: Order ID, SKU, and Quantity")
                return

            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as e:
                error_dialog(self.root, "Invalid Quantity",
                           "Please enter a valid positive number for quantity")
                return

            self._update_status(f"Adding {sku} to {order_id}...", 'info')

            success = self.order_processor.add_manual_product(order_id, sku, quantity)

            if success:
                self._update_status(f"Product added to {order_id}", 'success')
                info_dialog(self.root, "Success",
                           f"Added {quantity}x {sku} to order {order_id}")

                # Clear fields
                self.order_id_entry.delete(0, tk.END)
                self.sku_entry.delete(0, tk.END)
                self.quantity_entry.delete(0, tk.END)

                self.logger.log_info(f"Manual product added: {quantity}x {sku} to {order_id}", "ManualAdd")
            else:
                error_dialog(self.root, "Error",
                           f"Failed to add product. Order {order_id} may not exist.")

        except Exception as e:
            self.logger.log_exception(e, "Add Manual Product")
            error_dialog(self.root, "Error", f"Failed to add product:\n{str(e)}")

    # ==================== Utility Operations ====================

    def _generate_skus(self):
        """Generate missing SKUs with preview"""
        try:
            if not self.orders_loaded:
                warning_dialog(self.root, "No Orders", "Please load orders first")
                return

            self._update_status("Generating SKUs...", 'info')

            count, changes = self.order_processor.generate_missing_skus()

            if count == 0:
                info_dialog(self.root, "No Changes", "All products already have SKUs")
                self._update_status("No SKUs needed generation", 'info')
                return

            # Show preview of changes
            changes_text = "\n".join([f"{change['name']} → {change['new_sku']}"
                                     for change in changes[:20]])
            if len(changes) > 20:
                changes_text += f"\n\n... and {len(changes) - 20} more"

            if confirm_dialog(self.root, "Generate SKUs",
                            f"Generate {count} SKUs?\n\n{changes_text}"):
                self._update_status(f"Generated {count} SKUs", 'success')
                self.utils_status_label.config(text=f"{ICONS['ok']} Generated {count} SKUs")
                set_status_color(self.utils_status_label, 'success')
                self.logger.log_info(f"Generated {count} SKUs", "SKUGeneration")
            else:
                # User cancelled, but SKUs were already generated - need to reload
                info_dialog(self.root, "Note",
                          "SKUs were generated but not committed. Reload orders to discard.")

        except Exception as e:
            self.logger.log_exception(e, "Generate SKUs")
            error_dialog(self.root, "Error", f"Failed to generate SKUs:\n{str(e)}")

    def _validate_data_enhanced(self):
        """Enhanced data validation with detailed report"""
        try:
            if not self.master_loaded:
                warning_dialog(self.root, "No Master File", "Please load master file first")
                return

            if not self.orders_loaded:
                warning_dialog(self.root, "No Orders", "Please load orders first")
                return

            self._update_status("Validating data...", 'info')
            self.logger.log_info("Starting data validation", "Validation")

            # Run validation
            issues = self._run_full_validation()

            # Show validation report
            self._show_validation_report(issues)

        except Exception as e:
            self.logger.log_exception(e, "Validate Data")
            error_dialog(self.root, "Error", f"Validation failed:\n{str(e)}")

    def _run_full_validation(self) -> dict:
        """Run comprehensive validation and return issues"""
        issues = {
            'critical': [],
            'warning': [],
            'info': []
        }

        orders_df = self.order_processor.get_orders_dataframe()

        # Check 1: Empty SKUs
        if 'Lineitem sku' in orders_df.columns:
            empty_skus = orders_df[orders_df['Lineitem sku'].isna() | (orders_df['Lineitem sku'] == '')]
            if len(empty_skus) > 0:
                issues['warning'].append(f"Found {len(empty_skus)} rows with empty SKUs")

        # Check 2: Orphaned SKUs (SKUs not in product map)
        if 'Lineitem sku' in orders_df.columns:
            unique_skus = orders_df['Lineitem sku'].unique()
            orphaned = []
            for sku in unique_skus:
                if pd.notna(sku) and sku != '':
                    if not self.product_manager.has_product(sku) and not self.set_manager.is_set(sku):
                        orphaned.append(sku)

            if orphaned:
                issues['warning'].append(f"Found {len(orphaned)} SKUs not in master file: {', '.join(orphaned[:5])}"
                                       + (f"... (+{len(orphaned)-5} more)" if len(orphaned) > 5 else ""))

        # Check 3: Duplicate orders
        if 'Name' in orders_df.columns:
            duplicates = orders_df[orders_df.duplicated(subset=['Name', 'Lineitem sku'], keep=False)]
            if len(duplicates) > 0:
                issues['info'].append(f"Found {len(duplicates)} duplicate order-SKU combinations")

        # Check 4: Sets with no components
        all_sets = self.set_manager.get_all_set_skus()
        empty_sets = []
        for set_sku in all_sets:
            components = self.set_manager.get_components(set_sku)
            if not components:
                empty_sets.append(set_sku)

        if empty_sets:
            issues['critical'].append(f"Found {len(empty_sets)} sets with no components: {', '.join(empty_sets)}")

        # Check 5: Missing quantities
        if 'Lineitem quantity' in orders_df.columns:
            missing_qty = orders_df[orders_df['Lineitem quantity'].isna()]
            if len(missing_qty) > 0:
                issues['warning'].append(f"Found {len(missing_qty)} rows with missing quantities")

        return issues

    def _show_validation_report(self, issues: dict):
        """Show validation report window with enhanced UI"""
        from tkinter import scrolledtext

        report_window = tk.Toplevel(self.root)
        report_window.title(f"{ICONS['validate']} Validation Report")
        report_window.geometry("900x650")  # Wider and taller
        report_window.transient(self.root)

        # Header
        header_frame = ttk.Frame(report_window, padding=PADDING['normal'])
        header_frame.pack(fill=tk.X)

        critical_count = len(issues['critical'])
        warning_count = len(issues['warning'])
        info_count = len(issues['info'])

        if critical_count > 0:
            status_icon = ICONS['error']
            status_text = "Critical Issues Found"
            status_color = COLORS['error']
        elif warning_count > 0:
            status_icon = ICONS['warning']
            status_text = "Warnings Found"
            status_color = COLORS['warning']
        else:
            status_icon = ICONS['ok']
            status_text = "Validation Passed"
            status_color = COLORS['success']

        header_label = ttk.Label(header_frame, text=f"{status_icon} {status_text}",
                                font=FONTS['heading'], foreground=status_color)
        header_label.pack()

        summary_label = ttk.Label(header_frame,
                                 text=f"Critical: {critical_count} | Warnings: {warning_count} | Info: {info_count}",
                                 font=FONTS['default'])
        summary_label.pack(pady=PADDING['small'])

        # Report text area
        text_frame = ttk.Frame(report_window, padding=PADDING['normal'])
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=FONTS['default'],
                                             height=20, width=80)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Build report text
        report_text = "VALIDATION REPORT\n"
        report_text += "=" * 60 + "\n\n"

        if issues['critical']:
            report_text += f"{ICONS['error']} CRITICAL ISSUES:\n"
            report_text += "-" * 60 + "\n"
            for issue in issues['critical']:
                report_text += f"  • {issue}\n"
            report_text += "\n"

        if issues['warning']:
            report_text += f"{ICONS['warning']} WARNINGS:\n"
            report_text += "-" * 60 + "\n"
            for issue in issues['warning']:
                report_text += f"  • {issue}\n"
            report_text += "\n"

        if issues['info']:
            report_text += f"{ICONS['info']} INFORMATION:\n"
            report_text += "-" * 60 + "\n"
            for issue in issues['info']:
                report_text += f"  • {issue}\n"
            report_text += "\n"

        if not any([issues['critical'], issues['warning'], issues['info']]):
            report_text += f"{ICONS['ok']} No issues found! Data looks good.\n\n"
            report_text += "All validations passed successfully."

        text_area.insert('1.0', report_text)
        text_area.config(state='disabled')

        # Buttons
        button_frame = ttk.Frame(report_window, padding=PADDING['normal'])
        button_frame.pack(fill=tk.X)

        def copy_report():
            """Copy validation report to clipboard"""
            report_window.clipboard_clear()
            report_window.clipboard_append(report_text)
            info_dialog(report_window, "Copied", "Validation report copied to clipboard")

        ttk.Button(button_frame, text=f"{ICONS['copy']} Copy Report",
                  command=copy_report).pack(side=tk.LEFT, padx=PADDING['small'])
        ttk.Button(button_frame, text="Close", command=report_window.destroy).pack(side=tk.RIGHT)

        # Update status
        if critical_count > 0:
            self._update_status("Validation found critical issues", 'error')
            self.utils_status_label.config(text=f"{ICONS['error']} {critical_count} critical issues")
            set_status_color(self.utils_status_label, 'error')
        elif warning_count > 0:
            self._update_status("Validation found warnings", 'warning')
            self.utils_status_label.config(text=f"{ICONS['warning']} {warning_count} warnings")
            set_status_color(self.utils_status_label, 'warning')
        else:
            self._update_status("Validation passed", 'success')
            self.utils_status_label.config(text=f"{ICONS['ok']} Validation passed")
            set_status_color(self.utils_status_label, 'success')

    def _check_duplicates(self):
        """Check for duplicate orders/SKUs"""
        try:
            if not self.orders_loaded:
                warning_dialog(self.root, "No Orders", "Please load orders first")
                return

            self._update_status("Checking for duplicates...", 'info')

            orders_df = self.order_processor.get_orders_dataframe()

            # Check for duplicate rows (same order + SKU)
            if 'Name' in orders_df.columns and 'Lineitem sku' in orders_df.columns:
                duplicates = orders_df[orders_df.duplicated(subset=['Name', 'Lineitem sku'], keep=False)]

                if len(duplicates) > 0:
                    dup_orders = duplicates['Name'].nunique()
                    message = f"Found {len(duplicates)} duplicate rows\n"
                    message += f"Affecting {dup_orders} orders\n\n"
                    message += "Sample duplicates:\n"

                    sample = duplicates.head(10)[['Name', 'Lineitem sku', 'Lineitem quantity']].to_string(index=False)
                    message += sample

                    warning_dialog(self.root, "Duplicates Found", message)

                    self.utils_status_label.config(text=f"{ICONS['warning']} Found {len(duplicates)} duplicates")
                    set_status_color(self.utils_status_label, 'warning')
                else:
                    info_dialog(self.root, "No Duplicates", "No duplicate orders found!")
                    self.utils_status_label.config(text=f"{ICONS['ok']} No duplicates")
                    set_status_color(self.utils_status_label, 'success')

        except Exception as e:
            self.logger.log_exception(e, "Check Duplicates")
            error_dialog(self.root, "Error", f"Failed to check duplicates:\n{str(e)}")

    # ==================== Processing ====================

    def _preview_results(self):
        """Process orders and show preview window"""
        try:
            # Validate prerequisites
            if not self.master_loaded:
                warning_dialog(self.root, "No Master File", "Please load master file first")
                return

            if not self.orders_loaded:
                warning_dialog(self.root, "No Orders", "Please load orders first")
                return

            self._update_status("Processing orders...", 'info')
            self.logger.log_info("Starting order processing", "Processing")

            # Process orders
            processed_df = self.order_processor.process_orders()

            # Calculate statistics
            stats = self._calculate_statistics(processed_df)

            # Update status
            self._update_status(
                "Processing complete", 'success',
                info=f"Processed {stats['Processed Rows']} rows",
                counter=f"{stats['Unique Orders']} orders"
            )

            self.logger.log_info(f"Processing complete: {stats['Processed Rows']} rows", "Processing")

            # Show preview window
            show_preview(
                self.root,
                processed_df,
                stats,
                on_save_callback=self._save_processed_data
            )

        except Exception as e:
            self.logger.log_exception(e, "Preview Results")
            self._update_status("Processing failed", 'error')
            error_dialog(self.root, "Error", f"Failed to process orders:\n{str(e)}")

    def _calculate_statistics(self, processed_df: pd.DataFrame) -> dict:
        """Calculate processing statistics"""
        original_df = self.order_processor.get_orders_dataframe()

        stats = {
            'Original Rows': len(original_df),
            'Processed Rows': len(processed_df),
            'Unique Orders': processed_df['Name'].nunique() if 'Name' in processed_df.columns else 0,
            'Unique SKUs': processed_df['Lineitem sku'].nunique() if 'Lineitem sku' in processed_df.columns else 0,
            'Sets Decoded': len(processed_df) - len(original_df) if len(processed_df) > len(original_df) else 0
        }

        return stats

    def _save_processed_data(self, dataframe: pd.DataFrame):
        """Save processed data to CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Processed Orders",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="processed_orders.csv"
            )

            if not file_path:
                return

            self._update_status("Saving processed data...", 'info')
            self.logger.log_info(f"Saving to: {file_path}", "Save")

            dataframe.to_csv(file_path, index=False)

            self._update_status("Data saved successfully", 'success')
            self.logger.log_info(f"Saved {len(dataframe)} rows to {file_path}", "Save")

            info_dialog(self.root, "Success",
                       f"Processed data saved successfully!\n\n"
                       f"File: {Path(file_path).name}\n"
                       f"Rows: {len(dataframe)}")

        except Exception as e:
            self.logger.log_exception(e, "Save Data")
            error_dialog(self.root, "Error", f"Failed to save data:\n{str(e)}")

    # ==================== Window Management ====================

    def _on_closing(self):
        """Handle window close event"""
        try:
            # Save final state
            state = {
                'master_file': self.current_master_file,
                'orders_files': self.current_orders_files,
                'master_loaded': self.master_loaded,
                'orders_loaded': self.orders_loaded,
            }
            self.crash_recovery.save_state(state)

            # Log shutdown
            self.logger.log_info("Application closed normally", "MainWindow")

            # Close window
            self.root.destroy()

        except Exception as e:
            # Even if logging fails, close the window
            self.root.destroy()


def main():
    """Main entry point for the application"""
    try:
        root = tk.Tk()
        app = DecoderToolApp(root)
        root.mainloop()
    except Exception as e:
        # Log critical error
        logger = get_logger()
        logger.log_exception(e, "Application Startup")
        messagebox.showerror("Critical Error",
                           f"Application failed to start:\n{str(e)}\n\n"
                           f"Check logs for details")


if __name__ == "__main__":
    main()

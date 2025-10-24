"""Main GUI window for Decoder Tool application"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.product_manager import ProductManager
from src.models.set_manager import SetManager
from src.models.order_processor import OrderProcessor
from src.utils.file_handlers import MasterFileLoader, OrdersFileLoader


class DecoderToolApp:
    """Main application window for Decoder Tool"""

    def __init__(self, root):
        """
        Initialize the application

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Shopify Order Set Decoder Tool")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Initialize managers
        self.product_manager = ProductManager()
        self.set_manager = SetManager()
        self.order_processor = OrderProcessor(self.product_manager, self.set_manager)

        # State flags
        self.master_loaded = False
        self.orders_loaded = False

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the main UI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Section 1: Master File
        self._create_master_file_section(main_frame, row=0)

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        # Section 2: Orders
        self._create_orders_section(main_frame, row=2)

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)

        # Section 3: Process & Save
        self._create_process_section(main_frame, row=4)

        # Status bar at bottom
        self._create_status_bar(main_frame, row=5)

    def _create_master_file_section(self, parent, row):
        """Create Section 1: Master File Loading"""
        section = ttk.LabelFrame(parent, text="Section 1: Load Master File", padding="10")
        section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        section.columnconfigure(1, weight=1)

        # Load button
        ttk.Button(
            section,
            text="Load Master File (.xlsx)",
            command=self._load_master_file
        ).grid(row=0, column=0, sticky=tk.W, padx=5)

        # Status label
        self.master_status_label = ttk.Label(section, text="No master file loaded", foreground="gray")
        self.master_status_label.grid(row=0, column=1, sticky=tk.W, padx=10)

    def _create_orders_section(self, parent, row):
        """Create Section 2: Orders Loading and Manual Addition"""
        section = ttk.LabelFrame(parent, text="Section 2: Load Orders & Add Products", padding="10")
        section.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        section.columnconfigure(1, weight=1)

        # Load orders button
        ttk.Button(
            section,
            text="Load Orders Export (.csv)",
            command=self._load_orders
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        # Orders status label
        self.orders_status_label = ttk.Label(section, text="No orders loaded", foreground="gray")
        self.orders_status_label.grid(row=0, column=1, sticky=tk.W, padx=10)

        # Manual addition subsection
        manual_frame = ttk.Frame(section)
        manual_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        manual_frame.columnconfigure(1, weight=1)

        ttk.Label(manual_frame, text="Add Product to Order:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=5
        )

        # Order ID field
        ttk.Label(manual_frame, text="Order ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.order_id_entry = ttk.Entry(manual_frame, width=20)
        self.order_id_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(manual_frame, text="(e.g., #76360)", foreground="gray").grid(row=1, column=2, sticky=tk.W)

        # SKU field
        ttk.Label(manual_frame, text="SKU:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sku_entry = ttk.Entry(manual_frame, width=20)
        self.sku_entry.grid(row=2, column=1, sticky=tk.W, padx=5)

        # Quantity field
        ttk.Label(manual_frame, text="Quantity:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.quantity_entry = ttk.Entry(manual_frame, width=20)
        self.quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=5)

        # Add button
        ttk.Button(
            manual_frame,
            text="Add Product",
            command=self._add_manual_product
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)

    def _create_process_section(self, parent, row):
        """Create Section 3: Process and Save"""
        section = ttk.LabelFrame(parent, text="Section 3: Process & Save", padding="10")
        section.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)

        # Process button (large and prominent)
        self.process_button = ttk.Button(
            section,
            text="Process and Save As...",
            command=self._process_and_save,
            width=30
        )
        self.process_button.grid(row=0, column=0, pady=10)

        # Configure button style for prominence
        style = ttk.Style()
        style.configure('Big.TButton', font=('TkDefaultFont', 11, 'bold'))
        self.process_button.configure(style='Big.TButton')

    def _create_status_bar(self, parent, row):
        """Create status bar at the bottom"""
        self.status_label = ttk.Label(
            parent,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)

    def _set_status(self, message, color="black"):
        """Update status bar message"""
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()

    def _load_master_file(self):
        """Handle master file loading"""
        file_path = filedialog.askopenfilename(
            title="Select Master File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            self._set_status("Loading master file...", "blue")

            # Load file
            products_df, sets_df = MasterFileLoader.load(file_path)

            # Load into managers
            self.product_manager.load_from_dataframe(products_df)
            self.set_manager.load_from_dataframe(sets_df)

            self.master_loaded = True

            # Update UI
            success_msg = f"Master file loaded successfully! " \
                         f"({self.product_manager.count()} products, {self.set_manager.count()} sets)"
            self.master_status_label.config(text=success_msg, foreground="green")
            self._set_status(success_msg, "green")

            messagebox.showinfo("Success", success_msg)

        except Exception as e:
            error_msg = f"Error loading master file: {str(e)}"
            self._set_status(error_msg, "red")
            messagebox.showerror("Error", error_msg)

    def _load_orders(self):
        """Handle orders file loading"""
        if not self.master_loaded:
            messagebox.showwarning("Warning", "Please load master file first")
            return

        file_path = filedialog.askopenfilename(
            title="Select Orders Export",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            self._set_status("Loading orders...", "blue")

            # Load orders
            orders_df = OrdersFileLoader.load(file_path)
            self.order_processor.load_orders(orders_df)

            self.orders_loaded = True

            # Update UI
            success_msg = f"Orders loaded successfully! ({self.order_processor.get_order_count()} rows)"
            self.orders_status_label.config(text=success_msg, foreground="green")
            self._set_status(success_msg, "green")

            messagebox.showinfo("Success", success_msg)

        except Exception as e:
            error_msg = f"Error loading orders: {str(e)}"
            self._set_status(error_msg, "red")
            messagebox.showerror("Error", error_msg)

    def _add_manual_product(self):
        """Handle manual product addition"""
        if not self.orders_loaded:
            messagebox.showwarning("Warning", "Please load orders file first")
            return

        # Get input values
        order_id = self.order_id_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()

        # Validate inputs
        if not order_id or not sku or not quantity_str:
            messagebox.showwarning("Validation Error", "Please fill in all fields")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a positive integer")
            return

        # Add product
        success, message = self.order_processor.add_manual_product(order_id, sku, quantity)

        if success:
            self._set_status(message, "green")
            messagebox.showinfo("Success", message)

            # Clear input fields
            self.order_id_entry.delete(0, tk.END)
            self.sku_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)

            # Update orders count
            success_msg = f"Orders loaded successfully! ({self.order_processor.get_order_count()} rows)"
            self.orders_status_label.config(text=success_msg, foreground="green")
        else:
            self._set_status(message, "red")
            messagebox.showerror("Error", message)

    def _process_and_save(self):
        """Handle order processing and saving"""
        # Validate prerequisites
        if not self.master_loaded:
            messagebox.showerror("Error", "Please load master file first")
            return

        if not self.orders_loaded:
            messagebox.showerror("Error", "Please load orders file first")
            return

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Orders As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            self._set_status("Processing orders...", "blue")

            # Process orders
            processed_df = self.order_processor.process_orders()

            # Save to file
            OrdersFileLoader.save(processed_df, file_path)

            success_msg = f"Success! File saved: {Path(file_path).name} ({len(processed_df)} rows)"
            self._set_status(success_msg, "green")
            messagebox.showinfo("Success", success_msg)

        except Exception as e:
            error_msg = f"Error processing orders: {str(e)}"
            self._set_status(error_msg, "red")
            messagebox.showerror("Error", error_msg)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = DecoderToolApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

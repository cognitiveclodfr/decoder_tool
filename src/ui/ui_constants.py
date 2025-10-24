"""UI constants for styling and configuration"""

# Colors for status coding
COLORS = {
    'success': '#28a745',  # Green
    'warning': '#ffc107',  # Yellow
    'error': '#dc3545',    # Red
    'info': '#17a2b8',     # Blue
    'default': '#6c757d',  # Gray
    'primary': '#007bff',  # Primary blue
    'decoded_set': '#d4edda',  # Light green (салатовий) for decoded sets
}

# Icons using Unicode emojis
ICONS = {
    # File operations
    'load': '📁',
    'save': '💾',
    'reload': '🔄',
    'export': '📤',
    'import': '📥',

    # Actions
    'preview': '👁️',
    'process': '⚙️',
    'validate': '✅',
    'generate': '✨',
    'add': '➕',
    'delete': '🗑️',
    'edit': '✏️',
    'copy': '📋',
    'paste': '📄',

    # Status
    'ok': '✓',
    'warning': '⚠️',
    'error': '❌',
    'info': 'ℹ️',

    # Data
    'folder': '📂',
    'file': '📄',
    'csv': '📊',
    'excel': '📈',

    # Special
    'pin': '📌',
    'unpin': '📍',
    'favorite': '⭐',
    'search': '🔍',
    'filter': '🔎',
    'details': '📝',
    'note': '💬',
    'important': '🔴',
}

# Fonts
FONTS = {
    'default': ('Segoe UI', 9),
    'bold': ('Segoe UI', 9, 'bold'),
    'heading': ('Segoe UI', 11, 'bold'),
    'small': ('Segoe UI', 8),
    'monospace': ('Consolas', 9),
}

# Padding and spacing
PADDING = {
    'tiny': 2,
    'small': 5,
    'normal': 10,
    'large': 15,
    'xlarge': 20,
}

# Window sizes
WINDOW_SIZES = {
    'main': '950x900',
    'preview': '1300x750',
    'validation': '800x600',
    'dialog': '500x400',
}

# Status messages
STATUS_MESSAGES = {
    'ready': 'Ready',
    'loading': 'Loading...',
    'processing': 'Processing...',
    'saving': 'Saving...',
    'complete': 'Complete',
    'error': 'Error occurred',
    'no_master': 'No master file loaded',
    'no_orders': 'No orders loaded',
    'master_loaded': 'Master file loaded',
    'orders_loaded': 'Orders loaded',
}

# Tooltips
TOOLTIPS = {
    # Master file section
    'load_master': 'Load master file containing product and set definitions (XLSX format)',
    'reload_master': 'Reload the current master file to get latest changes',
    'master_info': 'View detailed information about loaded products and sets',
    'open_excel': 'Open master file in Microsoft Excel',
    'export_sets': 'Export sets list to CSV file',
    'pin_master': 'Pin this master file to favorites for quick access',

    # Orders section
    'load_single': 'Load a single CSV file with Shopify order export',
    'load_folder': 'Load and combine all CSV files from a selected folder',
    'reload_orders': 'Reload the current orders file(s)',
    'add_product': 'Manually add a product to an existing order',

    # Data utilities
    'generate_skus': 'Automatically generate SKUs for products with empty SKU fields',
    'validate': 'Validate data and check for potential issues before processing',
    'check_duplicates': 'Find duplicate orders or SKUs in loaded data',

    # Processing
    'preview_save': 'Process orders, decode sets, and preview results before saving',
    'undo': 'Undo last operation',
    'redo': 'Redo last undone operation',

    # Preview window
    'search': 'Search across all columns',
    'filter_order': 'Filter by specific Order ID',
    'sort': 'Click column header to sort',
    'copy_row': 'Copy selected row data',
    'delete_row': 'Delete selected row(s)',
    'edit_row': 'Edit selected row',
    'mark_important': 'Mark row as important',
    'add_note': 'Add note or comment to row',
    'view_details': 'View complete row details',
    'export_selected': 'Export only selected rows',
    'copy_all': 'Copy all visible data to clipboard',
    'bulk_delete': 'Delete multiple selected rows',
}

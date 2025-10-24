# Decoder Tool - Shopify Order Set Decoder

A flexible GUI application for decoding product bundles (sets) from Shopify order exports into individual components for accurate inventory tracking.

## Overview

This tool helps e-commerce businesses that sell product bundles (sets) to properly track inventory by automatically breaking down bundle orders into their individual components. When you sell a "Relaxation Bundle" that contains 3 different products, this tool ensures your inventory system sees the 3 individual products being sold, not just the bundle SKU.

## Key Features

- **Professional GUI Interface**: Modern, intuitive interface with icons, tooltips, and color-coded feedback
- **Master File Management**: Load product and set definitions from XLSX files with favorites and recent files
- **Order Processing**: Automatically decode sets into components with visual indicators
- **Manual Product Addition**: Add products to existing orders with validation
- **Smart Price Distribution**: First component in a set receives the full price
- **Flexible Architecture**: Easy to adapt for different stores by changing master files
- **Crash Recovery**: Automatic state saving and error logging for reliability

### 🎉 New in v2.2 - Complete UI/UX Overhaul!

**Enhanced Main Window:**
- 📁 Icons on all buttons for better visual clarity
- 💡 Tooltips on every interactive element
- 🎨 Color-coded status messages (green/yellow/red)
- 📌 Pin/Unpin favorite master files
- 🔄 Reload/Refresh functionality
- ✅ Enhanced validation with detailed categorized reports
- 🔍 Duplicate detection for orders and SKUs
- 🛡️ Crash recovery with auto-save (every 60 seconds)
- 📝 Error logging to `~/.decoder_tool/logs/`

**Enhanced Preview Window:**
- 🖱️ Right-click context menu (copy, delete, mark important, add notes)
- 🔵 Visual indicators for decoded sets (light blue highlight)
- ↩️ Undo/Redo support (Ctrl+Z / Ctrl+Y)
- 🗑️ Bulk delete operations
- 💬 Add notes to specific rows
- 🔴 Mark important rows
- ⌨️ Keyboard shortcuts (Del, Ctrl+Z, Ctrl+Y)

### v2.1 Features

- **SET_QUANTITY Support**: Handle sets with multiple quantities of the same component (e.g., 2x Barrier Cream in one bundle)
- **Multi-CSV Loading**: Load single CSV file OR load entire folder with multiple CSV files at once
- **Enhanced Flexibility**: Backward compatible - works with or without SET_QUANTITY column

### v2.0 Features

- **Auto SKU Generation**: Automatically generates SKUs from product names for items without SKU (testers, samples)
- **Interactive Preview Table**: View, search, filter, and sort all processed data before saving
- **Data Validation**: Pre-processing validation to catch issues early
- **Processing Statistics**: Detailed summary of what was processed
- **Search & Filter**: Find specific orders or products in preview
- **Export Selected Rows**: Save only the rows you need
- **Copy to Clipboard**: Paste data directly into Excel or other tools

## Installation

### Option 1: Download Pre-built Executable (Easiest)

**No Python installation required!**

1. Go to the [Releases](https://github.com/cognitiveclodfr/decoder_tool/releases) page
2. Download the latest version for your operating system:
   - **Windows**: `DecoderTool-Windows-x64.zip`
   - **Linux**: `DecoderTool-Linux-x64.tar.gz`
   - **macOS**: `DecoderTool-macOS-x64.tar.gz`
3. Extract the archive
4. Run the executable:
   - **Windows**: Double-click `DecoderTool.exe`
   - **Linux/macOS**: Run `./DecoderTool` from terminal

The executable includes demo data files in the `demo_data/` folder.

### Option 2: Run from Source

**Requirements:**
- Python 3.8 or higher
- pip package manager

**Setup:**

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

Run the application with:

```bash
python main.py
```

### Workflow

#### 1. Load Master File

Click **"Load Master File (.xlsx)"** and select your master file containing:

- **PRODUCTS sheet**: Product definitions
  - `Products_Name`: Product display name
  - `SKU`: Product SKU (unique identifier)
  - `Quantity_Product`: Physical quantity in product

- **SETS sheet**: Bundle/set definitions
  - `SET_Name`: Set display name
  - `SET_SKU`: Set SKU (unique identifier)
  - `SKUs_in_SET`: Component SKU (one row per component)
  - `SET_QUANTITY`: Quantity of this component in the set (optional, defaults to 1)

**Example Master File Structure:**

*PRODUCTS Sheet:*
| Products_Name | SKU | Quantity_Product |
|--------------|-----|------------------|
| Lavender Oil 10ml | LAV-10ML | 1 |
| Rose Oil 10ml | ROSE-10ML | 1 |
| Gift Box | BOX-RELAX | 1 |

*SETS Sheet:*
| SET_Name | SET_SKU | SKUs_in_SET | SET_QUANTITY |
|----------|---------|-------------|--------------|
| Relaxation Bundle | SET-RELAX | LAV-10ML | 1 |
| Relaxation Bundle | SET-RELAX | ROSE-10ML | 1 |
| Relaxation Bundle | SET-RELAX | BOX-RELAX | 1 |
| Barrier Bundle | SET-BARRIER | BARRIER-CREAM | 2 |
| Barrier Bundle | SET-BARRIER | BOX-SMALL | 1 |

**Note**: In the Barrier Bundle example, ordering 1x set will result in 2x BARRIER-CREAM and 1x BOX-SMALL being deducted from inventory.

#### 2. Load Orders Export

You have two options for loading orders:

**Option A: Load Single CSV File**
- Click **"Load Single CSV File"** and select your Shopify order export CSV file

**Option B: Load Folder with Multiple CSV Files** (New in v2.1!)
- Click **"Load Folder with CSV Files"** and select a folder containing multiple CSV files
- All CSV files in the folder will be combined and processed together
- Perfect for processing multiple order exports at once

The file(s) should contain standard Shopify export columns including:
- `Name` (Order ID, e.g., #76360)
- `Lineitem sku`
- `Lineitem quantity`
- `Lineitem name`
- `Lineitem price`
- etc.

#### 3. Add Products Manually (Optional)

If needed, you can manually add products to existing orders:

1. Enter the **Order ID** (e.g., #76360)
2. Enter the **SKU** to add
3. Enter the **Quantity**
4. Click **"Add Product"**

The product will be added to the order with:
- Name from the product map (or SKU if not found)
- Price and discount set to 0 to avoid duplication

#### 4. Data Processing Utilities (New!)

Before processing, use these utilities to ensure data quality:

**Generate Missing SKUs:**
- Automatically generates SKUs for products with empty SKU fields
- Converts product name to SKU format (e.g., "Barrier Cream Sample" → "BARRIER_CREAM_SAMPLE")
- Perfect for testers, samples, or other products without SKUs
- Shows you all generated SKUs before applying

**Validate Data:**
- Checks for potential issues before processing
- Warns about empty SKUs, incomplete sets, and other problems
- Helps prevent errors and ensures smooth processing

#### 5. Preview & Save Results

Click **"Preview & Save Results"** to:

1. Process all orders
2. Decode sets into individual components
3. **Preview results in interactive table** (New!)
   - View all processed data before saving
   - Search and filter by any column
   - Filter by specific order ID
   - Sort by clicking column headers
   - Double-click row for full details
   - Export selected rows only
   - Copy to clipboard for Excel
4. Save the processed CSV file

**Processing Statistics** displayed in preview:
- Original vs. processed row counts
- Number of unique orders and SKUs
- Sets decoded count

**Processing Logic:**

- **Regular Products**: Pass through unchanged
- **Sets**: Decoded into components where:
  - Each component becomes a separate line item
  - Component quantities are multiplied by order quantity and physical quantity
  - First component receives the original set price
  - Subsequent components receive price = 0
  - All components maintain other order details (customer, shipping, etc.)

## Project Structure

```
decoder_tool/
├── src/
│   ├── models/
│   │   ├── product_manager.py    # Product map handling
│   │   ├── set_manager.py        # Set map handling
│   │   └── order_processor.py    # Main processing logic
│   ├── ui/
│   │   └── main_window.py        # GUI application
│   └── utils/
│       └── file_handlers.py      # File I/O operations
├── tests/
│   ├── test_product_manager.py
│   ├── test_set_manager.py
│   └── test_order_processor.py
├── demo_data/
│   ├── HERBAR_TRUTH_FILE.xlsx    # Demo master file
│   └── orders_export.csv         # Demo orders
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Testing

Run the test suite with:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Demo Data

Demo files are included in the `demo_data/` folder:

- `HERBAR_TRUTH_FILE.xlsx`: Sample master file with products and sets
- `orders_export.csv`: Sample Shopify order export

To regenerate demo files:

```bash
python create_demo_files.py
```

## Example

**Input Order:**
- Order #76360
- 2x Relaxation Bundle (SET-RELAX) @ $49.99

**Set Definition:**
- SET-RELAX contains:
  - LAV-10ML (Lavender Oil)
  - ROSE-10ML (Rose Oil)
  - BOX-RELAX (Gift Box)

**Output (Processed):**
- Order #76360
  - 2x LAV-10ML @ $49.99
  - 2x ROSE-10ML @ $0.00
  - 2x BOX-RELAX @ $0.00

This ensures your inventory system deducts 2 units each of Lavender Oil, Rose Oil, and Gift Box, while maintaining the correct total order value of $49.99.

### Example: Auto SKU Generation

**Input (products without SKU):**
```
Lineitem name: "Barrier Cream Sample"
Lineitem sku: (empty)

Lineitem name: "Face Oil Sample"
Lineitem sku: (empty)
```

**After clicking "Generate Missing SKUs":**
```
Lineitem name: "Barrier Cream Sample"
Lineitem sku: "BARRIER_CREAM_SAMPLE"

Lineitem name: "Face Oil Sample"
Lineitem sku: "FACE_OIL_SAMPLE"
```

The tool automatically:
- Converts to uppercase
- Replaces spaces with underscores
- Removes special characters
- Handles multiple spaces correctly

## Technical Details

### Price Distribution Rules

When a set is decoded:
1. The first component receives the full `Lineitem price` from the set
2. All subsequent components receive `Lineitem price = 0`
3. Total order value remains unchanged
4. Individual component values are tracked separately

### Quantity Calculation

Component quantity = Order quantity × Component physical quantity

Example:
- Order: 3x SET-RELAX
- Component: LAV-10ML with physical_qty = 1
- Result: 3 × 1 = 3 units of LAV-10ML

### Duplicate Handling

- **Product SKUs**: Duplicates are handled by keeping the first occurrence
- **Set Components**: All components for a given SET_SKU are collected via groupby

### Missing Data Handling

- **Component not in product map**: SKU is used as name, physical_qty defaults to 1
- **Empty component SKUs**: Skipped during set loading

## Troubleshooting

### "Missing required columns" error
Ensure your master file has the exact column names:
- PRODUCTS: `Products_Name`, `SKU`, `Quantity_Product`
- SETS: `SET_Name`, `SET_SKU`, `SKUs_in_SET`

### "Order ID not found" when adding manually
Verify the order ID matches exactly (including the # symbol if present in your data).

### Sets not being decoded
Check that:
1. The set SKU exists in the SETS sheet
2. The set SKU matches exactly (case-sensitive)
3. The set has at least one component defined

## Building from Source

If you want to create your own executable or contribute to development:

### Building Executables

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run the build script:
```bash
python build_exe.py
```

The executable will be created in `dist/DecoderTool_Release/`

For detailed build instructions, see [BUILD.md](BUILD.md).

### Automatic Builds

The project includes GitHub Actions workflow that automatically builds executables for Windows, Linux, and macOS when you create a release.

To trigger automatic builds:
1. Create a new release on GitHub
2. Tag it with a version (e.g., `v1.0.0`)
3. GitHub Actions will build and attach executables automatically

## Development

### Running Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=src tests/
```

### Project Structure for Developers

See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for detailed technical documentation.

## License

This project is provided as-is for e-commerce automation purposes.

## Support

For issues or questions, please refer to the documentation or check the demo files for examples.

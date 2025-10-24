# Decoder Tool - Shopify Order Set Decoder

A flexible GUI application for decoding product bundles (sets) from Shopify order exports into individual components for accurate inventory tracking.

## Overview

This tool helps e-commerce businesses that sell product bundles (sets) to properly track inventory by automatically breaking down bundle orders into their individual components. When you sell a "Relaxation Bundle" that contains 3 different products, this tool ensures your inventory system sees the 3 individual products being sold, not just the bundle SKU.

## Key Features

- **GUI Interface**: Easy-to-use tkinter-based graphical interface
- **Master File Management**: Load product and set definitions from XLSX files
- **Order Processing**: Automatically decode sets into components
- **Manual Product Addition**: Add products to existing orders
- **Smart Price Distribution**: First component in a set receives the full price
- **Flexible Architecture**: Easy to adapt for different stores by changing master files

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

**Example Master File Structure:**

*PRODUCTS Sheet:*
| Products_Name | SKU | Quantity_Product |
|--------------|-----|------------------|
| Lavender Oil 10ml | LAV-10ML | 1 |
| Rose Oil 10ml | ROSE-10ML | 1 |
| Gift Box | BOX-RELAX | 1 |

*SETS Sheet:*
| SET_Name | SET_SKU | SKUs_in_SET |
|----------|---------|-------------|
| Relaxation Bundle | SET-RELAX | LAV-10ML |
| Relaxation Bundle | SET-RELAX | ROSE-10ML |
| Relaxation Bundle | SET-RELAX | BOX-RELAX |

#### 2. Load Orders Export

Click **"Load Orders Export (.csv)"** and select your Shopify order export CSV file.

The file should contain standard Shopify export columns including:
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

#### 4. Process and Save

Click **"Process and Save As..."** to:

1. Process all orders
2. Decode sets into individual components
3. Save the processed CSV file

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

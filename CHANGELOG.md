# Changelog

All notable changes to Decoder Tool will be documented in this file.

## [2.1.0] - 2025-10-24

### 🎉 Minor Release: SET_QUANTITY Support & Multi-CSV Loading

This release adds support for sets with multiple quantities of the same component and the ability to load multiple CSV files at once.

### ✨ Added

#### SET_QUANTITY Column Support
- **New optional column** `SET_QUANTITY` in SETS sheet
- Allows sets to contain multiple quantities of the same component
  - Example: A set with 2x Barrier Cream and 1x Box
- **Backward compatible** - defaults to quantity 1 if column not present
- Works with existing master files without modification
- Quantity calculation formula: `order_quantity × set_quantity × physical_qty`
- Example use case:
  ```
  SET_Name: Barrier Bundle
  SET_SKU: SET-BARRIER
  Components:
    - BARRIER-CREAM (SET_QUANTITY: 2)
    - BOX-SMALL (SET_QUANTITY: 1)

  Order: 3x Barrier Bundle → Results in:
    - 6x BARRIER-CREAM (3 × 2 × 1)
    - 3x BOX-SMALL (3 × 1 × 1)
  ```

#### Multi-CSV Loading
- **Load folder with multiple CSV files** at once
- New "Load Folder with CSV Files" button in GUI
- All CSV files in selected folder are automatically combined
- Files are sorted alphabetically before combining
- Shows detailed message with all loaded file names
- Perfect for processing multiple order exports in one go
- **Still supports single file loading** - choose what works best for you

### 🔧 Changed
- GUI now has two separate buttons:
  - "Load Single CSV File" (existing functionality)
  - "Load Folder with CSV Files" (new)
- SetManager.get_components() now returns `List[Dict[str, any]]` instead of `List[str]`
  - Each dict contains: `{'sku': str, 'quantity': int}`
- OrderProcessor._decode_set() updated to use set_quantity from components
- Demo files updated to include SET_QUANTITY column examples

### 📊 Testing
- Added 3 new tests for SET_QUANTITY in test_set_manager.py
- Added 2 new tests for SET_QUANTITY with order processing
- Created new test_file_handlers.py with 9 tests for multi-CSV loading
- Updated existing tests to work with new dict-based component format
- Total tests increased from 69 to 83
- All tests passing (100% success rate)

### 📝 Documentation
- Updated README with v2.1 features
- Added SET_QUANTITY column to master file documentation
- Added multi-CSV loading instructions
- Added example showing Barrier Bundle with SET_QUANTITY
- Updated CHANGELOG with v2.1 changes

### 🔄 Compatibility
- **Fully backward compatible** with v2.0 master files
- Master files without SET_QUANTITY column work unchanged
- All existing functionality preserved

---

## [2.0.0] - 2025-10-24

### 🎉 Major Release: Enhanced User Experience & Auto SKU Generation

This release adds significant improvements based on real-world usage requirements, making the tool more powerful and user-friendly.

### ✨ Added

#### Auto SKU Generation
- **Automatic SKU generation** for products without SKU (testers, samples, etc.)
- Converts product names to SKU format automatically
  - Example: "Barrier Cream Sample" → "BARRIER_CREAM_SAMPLE"
- Handles special characters, multiple spaces, case conversion
- Shows preview of all generated SKUs before applying
- New "Generate Missing SKUs" button in Data Processing Utilities section

#### Interactive Preview Table
- **Full-featured preview window** before saving processed results
- **Search functionality** - find any text across all columns
- **Filter by Order ID** - view specific orders
- **Sort by column** - click any header to sort
- **Row details** - double-click for complete row information
- **Export selected rows** - save only what you need
- **Copy to clipboard** - paste directly into Excel (TSV format)
- **Processing statistics** display:
  - Original vs. processed row counts
  - Unique orders count
  - Unique SKUs count
  - Sets decoded count

#### Data Validation
- **Pre-processing validation** to catch issues before processing
- Checks for:
  - Empty SKUs that need generation
  - Sets with no components defined
  - Unusual data patterns
- Actionable warning messages
- New "Validate Data" button

#### Enhanced User Interface
- New **Data Processing Utilities section** (Section 2.5)
- Status labels showing operation results
- Larger window size (900x850 pixels) for better visibility
- Better button labels ("Preview & Save Results" instead of "Process and Save As...")
- Real-time feedback for all operations

### 🔧 Changed
- Window geometry increased from 800x700 to 900x850
- "Process and Save As..." renamed to "Preview & Save Results"
- GUI now has 4 sections instead of 3
- Version bumped from 1.0.0 to 2.0.0

### 📊 Testing
- Added 24 new unit tests for SKU generator
- Added 5 new tests for SKU generation in OrderProcessor
- Total tests increased from 40 to 69
- All tests passing (100% success rate)
- New demo file with empty SKUs for testing

### 📝 Documentation
- Updated README with new features and examples
- Updated PROJECT_SUMMARY with v2.0 status
- Added AUTO SKU generation examples
- Added preview table usage guide

### 🐛 Fixed
- Better handling of empty/missing SKU fields
- Improved error messages throughout the application

---

## [1.0.0] - 2025-10-24

### 🎉 Initial Release

#### Core Features
- GUI application using tkinter
- Load master file (XLSX) with PRODUCTS and SETS sheets
- Load Shopify order export (CSV)
- Manual product addition to orders
- Automatic set decoding into components
- Smart price distribution (first component gets price)
- Quantity multiplication based on physical quantities
- Save processed orders to CSV

#### Technical Features
- ProductManager for product data
- SetManager for bundle/set definitions
- OrderProcessor for processing logic
- File handlers for XLSX and CSV
- Comprehensive error handling
- 40 unit and integration tests (100% passing)

#### Documentation
- Complete README with usage instructions
- PROJECT_SUMMARY with technical details
- BUILD.md for creating executables
- RELEASE.md for release process
- Demo data files

#### Build System
- PyInstaller configuration
- GitHub Actions for automatic multi-platform builds
- Support for Windows, Linux, macOS

---

## Version Format

Versions follow [Semantic Versioning](https://semver.org/):
- **Major version** (X.0.0): Breaking changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

# Changelog

All notable changes to Decoder Tool will be documented in this file.

## [2.3.1] - 2025-10-24

### 🎯 Enhancement: FIXED vs MATCHED Addition Types

Enhanced automatic companion product addition with two distinct modes to handle different business scenarios.

### ✨ New Features

**TYPE Column in ADDITION Sheet**
- New optional `TYPE` column to specify addition behavior
- Two types supported: `FIXED` and `MATCHED`
- Defaults to `FIXED` for backwards compatibility

**FIXED Type** (фіксована кількість)
- Adds a fixed quantity specified in QUANTITY column
- Quantity does NOT depend on trigger product quantity
- Example: Always add 1 manual PDF regardless of product quantity
```
IF_SKU: PRODUCT-A | THEN_ADD: MANUAL-PDF | TYPE: FIXED | QUANTITY: 1
→ 5 × PRODUCT-A → add 1 × MANUAL-PDF
→ 10 × PRODUCT-A → add 1 × MANUAL-PDF
```

**MATCHED Type** (кількість співпадає)
- Adds quantity matching the trigger product quantity
- QUANTITY column is ignored for MATCHED type
- Example: Each bottle needs its own dropper
```
IF_SKU: NECTAR-30 | THEN_ADD: NECTAR-DROPPER | TYPE: MATCHED
→ 3 × NECTAR-30 → add 3 × NECTAR-DROPPER
→ 5 × NECTAR-30 → add 5 × NECTAR-DROPPER
→ 10 × NECTAR-30 → add 10 × NECTAR-DROPPER
```

### 🔧 Implementation Details

**AdditionManager Updates**
- Stores `type` field in addition rules ('FIXED' or 'MATCHED')
- Case-insensitive type parsing (fixed, FIXED, matched, MATCHED all work)
- Invalid type values default to FIXED
- Full backwards compatibility: rules without TYPE default to FIXED

**OrderProcessor Enhancement**
- Enhanced `_apply_addition_rules()` to handle both types
- For FIXED: uses `rule['quantity']`
- For MATCHED: uses `row['Lineitem quantity']` from trigger product
- Both types maintain price = 0 for added products

### ✅ Testing
- **11 new AdditionManager TYPE tests** (20 total for AdditionManager)
- **5 new integration tests** for FIXED/MATCHED scenarios
- **123 total tests, all passing**
- Tests cover:
  - FIXED type with various quantities
  - MATCHED type with various quantities
  - Mixed FIXED and MATCHED rules in same file
  - Backwards compatibility (no TYPE column)
  - Case insensitivity and invalid values
  - Multiple orders with different quantities

### 📖 Use Cases

**FIXED Type:**
- Digital products (manuals, PDFs) - always add 1 copy
- Promotional items - fixed quantity per order
- Starter kits - fixed components regardless of quantity

**MATCHED Type:**
- Consumables with accessories (bottles + droppers)
- Products with matching parts (devices + batteries)
- Items requiring 1:1 pairing

### 🔄 Backwards Compatibility
- ✅ Existing ADDITION sheets without TYPE column continue to work
- ✅ Default behavior unchanged (FIXED type)
- ✅ All existing tests pass
- ✅ No changes required to existing master files

## [2.3.0] - 2025-10-24

### 🎉 New Feature: Automatic Companion Product Addition

Added powerful new functionality to automatically add companion/accessory products to orders based on rules defined in master file.

### ✨ Features

**ADDITION Sheet Support**
- New optional `ADDITION` sheet in master file for defining addition rules
- Columns: `IF_SKU` (trigger product), `THEN_ADD` (product to add), `QUANTITY` (optional, defaults to 1)
- Example: When order contains `NECTAR-30`, automatically add `NECTAR-DROPPER` with quantity 1
- Companion products added with price = 0 to maintain order total
- Smart detection: only adds if companion product not already in order

**AdditionManager**
- New manager class for handling automatic product additions
- Full API: `load_from_dataframe()`, `has_addition_rule()`, `get_addition_rule()`, `count()`, `clear()`
- Robust validation: handles empty values, NaN, whitespace
- Supports duplicate trigger SKUs (last rule wins)

**OrderProcessor Enhancement**
- Integrated addition rules into order processing workflow
- Applies additions after set decoding
- Groups additions by order to prevent duplicates
- Preserves all order metadata for added products

**UI Integration**
- Master file loader automatically detects and loads ADDITION sheet
- Logs addition rules count when master file loaded
- Gracefully handles master files without ADDITION sheet (backwards compatible)
- All three master file loading methods support additions (load, reload, load from path)

### 🐛 Bug Fixes
- **Fixed tooltips**: Changed from unsupported `padding` parameter to `padx`/`pady` in tk.Label
  - Tooltips now display correctly without empty gray boxes
  - Proper padding around tooltip text

### ✅ Testing
- **14 new AdditionManager tests** (112 total tests now, all passing)
  - Test initialization, loading, validation
  - Test rule retrieval and existence checking
  - Test edge cases: empty values, NaN, whitespace, duplicates
  - Test quantity handling and defaults
- Updated integration tests for new MasterFileLoader signature
- Comprehensive test coverage for addition rules workflow

### 📝 Technical Details
- `MasterFileLoader.load()` now returns `Tuple[DataFrame, DataFrame, Optional[DataFrame]]`
  - Third return value is additions DataFrame or None if sheet doesn't exist
- `OrderProcessor.__init__()` now accepts optional `AdditionManager` parameter
- New `_apply_addition_rules()` method in OrderProcessor
- Addition rules applied per-order to prevent cross-order additions
- Full backwards compatibility: old master files without ADDITION sheet work fine

### 📖 Use Cases
Perfect for products that require accessories:
- Essential oils that need droppers
- Products requiring batteries
- Items with mandatory accessories
- Subscription boxes with promotional items

## [2.2.1] - 2025-10-24

### 🐛 Bug Fixes
- **Fixed critical bug**: "'ProductManager' object has no attribute '_products'" error when loading master file
  - Changed from accessing private attributes `_products` and `_sets` to using public `count()` methods
  - Added null-safety check for `get_orders_dataframe()` return value
  - UI now uses proper public API instead of internal implementation details

### ✅ Testing & Stability
- **Added comprehensive UI stability tests** (15 new tests, 98 total)
  - Test ProductManager public API methods (count, get_all_skus, has_product)
  - Test SetManager public API methods (count, get_all_set_skus, is_set)
  - Test OrderProcessor public API methods (get_orders_dataframe, process_orders, generate_missing_skus)
  - Integration tests for typical UI workflows
  - Tests specifically for the `_update_process_info()` scenario that was failing
- All 98 tests pass successfully

### 📝 Technical Details
- `_update_process_info()` now safely accesses manager data through public methods
- Proper handling of None returns from `get_orders_dataframe()`
- Better encapsulation: UI layer no longer depends on internal implementation

## [2.2.0] - 2025-10-24

### 🎉 Major Release: Complete UI/UX Overhaul

This is a comprehensive UI/UX upgrade that transforms the application into a professional-grade tool with extensive usability improvements, visual enhancements, and power-user features.

### ✨ Main Window Enhancements

#### Visual Improvements
- **Icons on all buttons** - Every button now has an intuitive emoji icon (📁 Load, 💾 Save, ✅ Preview, 🔄 Process, etc.)
- **Tooltips everywhere** - Hover over any button or field to see helpful explanations
- **Color-coded status messages** - Green for success, yellow for warnings, red for errors
- **Better spacing and grouping** - More "airy" design with improved visual hierarchy
- **Enhanced status bar** - 3-section layout (status | info | counter) with real-time updates

#### File Management
- **Pin/Unpin favorite master files** - Quick access to frequently used files
- **Recent files menu** - Separate sections for favorites and recent files
- **Reload/Refresh functionality** - Quickly reload current files to get latest changes
- **File history tracking** - Automatically remembers last 10 files with timestamps
- **Context menu for master file** - Right-click options: Reload, View Info, Open Location

#### Data Validation & Quality
- **Enhanced validation** - Comprehensive pre-flight check before processing
- **Validation report window** - Categorized warnings (Critical/Warning/Info)
- **Orphaned SKUs detection** - Find SKUs not in master file
- **Duplicate detection** - Find duplicate orders or SKUs
- **Pre-processing checks** - Catch issues early before they cause problems

#### Reliability & Safety
- **Crash recovery** - Automatic state saving every 60 seconds
- **Error logging** - Detailed logs saved to ~/.decoder_tool/logs/
- **Auto-save** - Application state preserved across sessions
- **Session restore** - Option to restore previous session after crash
- **Log rotation** - Automatic cleanup of old log files (7-day retention)

### ✨ Preview Window Enhancements

#### Interactive Features
- **Right-click context menu** with rich operations:
  - 📋 Copy row data
  - 🗑️ Delete row
  - 📝 View full details
  - 🔴 Mark as important
  - 💬 Add/edit notes
- **Undo/Redo support** - Ctrl+Z and Ctrl+Y keyboard shortcuts
- **Bulk operations** - Delete multiple selected rows at once
- **Keyboard shortcuts** - Del key for delete, Ctrl+Z/Y for undo/redo

#### Visual Indicators
- **Decoded sets highlighted** - Light blue background for decoded set components
- **Important rows** - Red bold text for marked rows
- **Rows with notes** - Yellow text with 💬 note indicator
- **Legend toolbar** - Shows meaning of all visual indicators

#### Enhanced UI
- **Toolbar with action buttons** - Undo, Redo, Delete Selected buttons
- **Sort direction indicators** - Visual ↑↓ arrows show current sort
- **Better search** - Improved filtering with visual feedback
- **Enhanced row details** - Scrollable window with formatted display

### 🔧 Technical Improvements

#### New Infrastructure
- **UI Constants module** (`ui_constants.py`) - Centralized icons, colors, tooltips, fonts
- **UI Utils module** (`ui_utils.py`) - Reusable components (ToolTip, StatusBar, dialogs)
- **File History module** (`file_history.py`) - Recent files and favorites management
- **Error Logger module** (`error_logger.py`) - Professional error logging and crash recovery

#### Code Quality
- All UI components use consistent styling
- Better error handling throughout
- Improved code organization and modularity
- Type hints for better code maintainability

### 📊 User Experience Summary

Before v2.2:
- Basic functional interface
- Limited visual feedback
- No error recovery
- Manual file management

After v2.2:
- Professional, polished interface
- Rich visual feedback and color coding
- Automatic crash recovery and error logging
- Intelligent file management with favorites
- Context menus and keyboard shortcuts
- Undo/Redo for safety
- Visual indicators for data clarity

### 🎯 Features Checklist

- ✅ 1.1: Icons, tooltips, spacing, color-coding
- ✅ 1.2: Enhanced status bar with counters
- ✅ 2.1: Pin favorites, reload/refresh
- ✅ 2.2: Duplicate detection, Undo/Redo, bulk operations
- ✅ 3.1: Right-click context menus
- ✅ 4.1: Enhanced validation with detailed report
- ✅ 6.1: Visual indicators for decoded sets
- ✅ 7.1: Crash recovery and error logging

### 🔄 Compatibility
- **Fully backward compatible** with v2.0 and v2.1
- All existing files and workflows continue to work
- No breaking changes to data formats
- Optional features don't require migration

### 📁 File Structure Updates
```
~/.decoder_tool/
├── logs/               # Error logs (auto-created)
├── recovery/           # Crash recovery states
└── history.json        # Recent files
    favorites.json      # Pinned favorites
```

---

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

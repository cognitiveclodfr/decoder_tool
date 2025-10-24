# Build Instructions

This document describes how to build standalone executables for DecoderTool.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Development dependencies installed

## Quick Build

### Install Build Dependencies

```bash
pip install -r requirements-dev.txt
```

### Build Executable

Run the build script:

```bash
python build_exe.py
```

This will:
1. Clean old build artifacts
2. Build the executable using PyInstaller
3. Create a release package with demo data and README

Output location: `dist/DecoderTool_Release/`

## Manual Build with PyInstaller

### Using the spec file (recommended)

```bash
pyinstaller DecoderTool.spec
```

### Using command line

```bash
pyinstaller --name=DecoderTool \
            --onefile \
            --windowed \
            --add-data=demo_data:demo_data \
            --hidden-import=pandas \
            --hidden-import=openpyxl \
            main.py
```

## Platform-Specific Notes

### Windows

```bash
pyinstaller DecoderTool.spec
```

Output: `dist/DecoderTool.exe`

### Linux

```bash
pyinstaller DecoderTool.spec
```

Output: `dist/DecoderTool`

Make executable:
```bash
chmod +x dist/DecoderTool
```

### macOS

```bash
pyinstaller DecoderTool.spec
```

Output: `dist/DecoderTool`

Make executable:
```bash
chmod +x dist/DecoderTool
```

## GitHub Actions (Automatic Builds)

The project includes GitHub Actions workflow that automatically builds executables for Windows, Linux, and macOS when you create a release.

### Creating a Release

1. Go to your GitHub repository
2. Click on "Releases" → "Create a new release"
3. Create a new tag (e.g., `v1.0.0`)
4. Fill in release details
5. Click "Publish release"

GitHub Actions will automatically:
- Run all tests
- Build executables for Windows, Linux, and macOS
- Upload the executables as release assets

### Manual Workflow Trigger

You can also trigger the build workflow manually:

1. Go to "Actions" tab in your GitHub repository
2. Select "Build and Release" workflow
3. Click "Run workflow"

## Build Configuration

### PyInstaller Spec File

The `DecoderTool.spec` file contains the build configuration:

- **hiddenimports**: Explicitly included modules
- **datas**: Additional files to include (demo_data, README)
- **excludes**: Modules to exclude (reduces size)
- **console**: Set to `False` for GUI app (no console window)

### Customization

To customize the build, edit `DecoderTool.spec`:

```python
# Add more data files
datas=[
    ('demo_data', 'demo_data'),
    ('my_file.txt', '.'),
],

# Add more hidden imports
hiddenimports=[
    'pandas',
    'my_module',
],
```

## Troubleshooting

### "Module not found" errors

Add missing modules to `hiddenimports` in the spec file:

```python
hiddenimports=[
    'pandas',
    'your_missing_module',
],
```

### Large executable size

Exclude unnecessary modules:

```python
excludes=[
    'matplotlib',
    'numpy.distutils',
    'pytest',
],
```

### tkinter issues

On Linux, ensure tkinter is installed:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### UPX compression issues

If UPX causes problems, disable it in spec file:

```python
exe = EXE(
    ...,
    upx=False,
    ...
)
```

## Testing the Executable

After building, test the executable:

1. Navigate to `dist/DecoderTool_Release/`
2. Run the executable
3. Test all features:
   - Load master file
   - Load orders
   - Add manual products
   - Process and save

## Distribution

### Windows

Distribute the entire `DecoderTool_Release` folder, or create an installer using tools like:
- Inno Setup
- NSIS
- WiX

### Linux

Create a `.tar.gz` archive:

```bash
cd dist
tar -czf DecoderTool-Linux-x64.tar.gz DecoderTool_Release/
```

### macOS

Create a `.dmg` image or `.zip` archive:

```bash
cd dist
zip -r DecoderTool-macOS-x64.zip DecoderTool_Release/
```

## Size Optimization

To reduce executable size:

1. **Use virtual environment**: Build in a clean venv with only required packages
2. **Exclude test files**: Don't include pytest and test files
3. **Use UPX**: Enable UPX compression (default)
4. **Exclude docs**: Remove unnecessary documentation files

Example optimized build:

```bash
python -m venv build_env
source build_env/bin/activate  # Windows: build_env\Scripts\activate
pip install pandas openpyxl pyinstaller
pyinstaller DecoderTool.spec
```

## Continuous Integration

The `.github/workflows/release.yml` file defines the CI/CD pipeline:

- Runs on: Windows, Linux, macOS
- Triggers: On release creation or manual dispatch
- Steps:
  1. Checkout code
  2. Set up Python 3.11
  3. Install dependencies
  4. Run tests
  5. Build executable
  6. Create release package
  7. Upload artifacts
  8. Attach to GitHub release

## Version Management

Update version in multiple places:

1. `src/__init__.py`: `__version__`
2. Git tag: `v1.0.0`
3. GitHub release title

Consider using tools like `bump2version` for automatic version management.

## Support

For build issues:
- Check PyInstaller documentation: https://pyinstaller.org
- Review spec file configuration
- Check GitHub Actions logs for CI builds
- Test in a clean virtual environment

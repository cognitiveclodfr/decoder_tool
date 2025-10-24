#!/usr/bin/env python3
"""
Build script for creating standalone EXE executable
Uses PyInstaller to package the application
"""
import subprocess
import sys
import shutil
from pathlib import Path


def clean_build_directories():
    """Remove old build artifacts"""
    print("Cleaning old build directories...")
    directories = ['build', 'dist']
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Removed {dir_name}/")


def build_exe():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=DecoderTool',
        '--onefile',
        '--windowed',
        '--add-data=demo_data:demo_data',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=tkinter',
        '--icon=NONE',
        '--clean',
        'main.py'
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build failed!")
        print(f"Error: {e.stderr}")
        return False


def create_release_package():
    """Create a release package with executable and demo files"""
    print("\nCreating release package...")

    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ✗ Dist directory not found!")
        return False

    # Create release directory
    release_dir = dist_dir / 'DecoderTool_Release'
    release_dir.mkdir(exist_ok=True)

    # Copy executable
    exe_file = dist_dir / 'DecoderTool.exe'
    if not exe_file.exists():
        exe_file = dist_dir / 'DecoderTool'  # Linux/Mac

    if exe_file.exists():
        shutil.copy2(exe_file, release_dir)
        print(f"  ✓ Copied executable")
    else:
        print("  ✗ Executable not found!")
        return False

    # Copy demo data
    demo_src = Path('demo_data')
    if demo_src.exists():
        demo_dst = release_dir / 'demo_data'
        shutil.copytree(demo_src, demo_dst)
        print("  ✓ Copied demo data")

    # Copy README
    readme = Path('README.md')
    if readme.exists():
        shutil.copy2(readme, release_dir)
        print("  ✓ Copied README")

    print(f"\n✓ Release package created: {release_dir}")
    return True


def main():
    """Main build process"""
    print("=" * 60)
    print("DecoderTool - Executable Build Script")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found!")
        print("  Install it with: pip install pyinstaller")
        sys.exit(1)

    # Clean old builds
    clean_build_directories()

    # Build executable
    if not build_exe():
        print("\n✗ Build failed!")
        sys.exit(1)

    # Create release package
    if not create_release_package():
        print("\n✗ Release package creation failed!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Build completed successfully!")
    print("=" * 60)
    print("\nExecutable location: dist/DecoderTool_Release/")
    print("You can now distribute the entire DecoderTool_Release folder.")


if __name__ == '__main__':
    main()

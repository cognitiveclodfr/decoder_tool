# Release Process

This document describes how to create a new release with automatic executable builds.

## Prerequisites

- Repository with GitHub Actions enabled
- Write access to the repository
- All changes committed and pushed

## Creating a Release

### 1. Update Version

Update version in `src/__init__.py`:

```python
__version__ = "1.0.0"  # Update this
```

### 2. Commit Version Change

```bash
git add src/__init__.py
git commit -m "Bump version to 1.0.0"
git push
```

### 3. Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0
```

### 4. Create GitHub Release

1. Go to your repository on GitHub
2. Click on "Releases" → "Create a new release"
3. Select the tag you just pushed (v1.0.0)
4. Fill in release details:
   - **Release title**: v1.0.0 - Brief description
   - **Description**: Detailed changes (see template below)
5. Click "Publish release"

### 5. Automatic Build Process

GitHub Actions will automatically:
1. ✓ Run all tests
2. ✓ Build executables for Windows, Linux, macOS
3. ✓ Create release packages
4. ✓ Attach executables to the release

Monitor progress: Go to "Actions" tab on GitHub

### 6. Verify Release

Once the workflow completes:
1. Check that all 3 executables are attached to the release
2. Download and test each executable
3. Update release notes if needed

## Release Notes Template

```markdown
## What's New

- Feature 1: Description
- Feature 2: Description
- Bug fix: Description

## Download

Choose the version for your operating system:

- **Windows**: [DecoderTool-Windows-x64.zip](link)
- **Linux**: [DecoderTool-Linux-x64.tar.gz](link)
- **macOS**: [DecoderTool-macOS-x64.tar.gz](link)

## Installation

### Windows
1. Download and extract the ZIP file
2. Run `DecoderTool.exe`

### Linux
1. Download and extract: `tar -xzf DecoderTool-Linux-x64.tar.gz`
2. Run: `./DecoderTool`

### macOS
1. Download and extract: `tar -xzf DecoderTool-macOS-x64.tar.gz`
2. Run: `./DecoderTool`

## Requirements

No Python installation required! All dependencies are bundled.

## Changes

Full changelog: https://github.com/user/repo/compare/v0.9.0...v1.0.0
```

## Version Numbering

Follow Semantic Versioning (SemVer):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new feature
- `v1.1.1` - Fixed a bug
- `v2.0.0` - Breaking changes

## Pre-releases

For beta/alpha releases:

```bash
git tag -a v1.0.0-beta.1 -m "Beta release 1.0.0-beta.1"
git push origin v1.0.0-beta.1
```

Mark as "pre-release" when creating the GitHub release.

## Hotfix Process

For urgent fixes:

1. Create hotfix branch: `git checkout -b hotfix/critical-bug`
2. Make fix and test
3. Update version (patch): `1.0.0` → `1.0.1`
4. Commit: `git commit -m "Fix critical bug"`
5. Merge to main: `git checkout main && git merge hotfix/critical-bug`
6. Tag: `git tag -a v1.0.1 -m "Hotfix 1.0.1"`
7. Push: `git push && git push origin v1.0.1`
8. Create release on GitHub

## Troubleshooting

### Build Fails

1. Check GitHub Actions logs
2. Ensure all tests pass locally: `pytest`
3. Verify dependencies in requirements.txt
4. Check PyInstaller compatibility

### Tag Already Exists

Delete and recreate:
```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Create new tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### Missing Executables

1. Check workflow completed successfully
2. Verify release was created (not just tag)
3. Re-run failed jobs in Actions tab

## Manual Build (Fallback)

If automatic builds fail:

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Build
python build_exe.py

# Upload manually to GitHub release
```

## Changelog Management

Keep CHANGELOG.md updated:

```markdown
# Changelog

## [1.0.0] - 2025-10-24
### Added
- Feature X
### Fixed
- Bug Y
### Changed
- Behavior Z
```

## Announcement

After release:
1. Update README if needed
2. Announce on relevant channels
3. Close related issues/PRs
4. Update documentation site (if applicable)

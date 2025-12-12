# RoboMentor Electron App Build and Deployment Guide

This guide covers building and deploying the RoboMentor Electron application with the integrated Python backend.

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- npm or yarn

## Installation

1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Install Python dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Building the Application

### Build Python Backend

The Python backend needs to be built into a standalone executable before building the Electron app:

```bash
cd frontend
npm run build-backend
```

This will create `robomentor-backend` executable in `backend/dist/`.

### Build Electron App

#### Build for Current Platform
```bash
npm run build-electron
```

#### Build for Windows
```bash
npm run build-win
```

#### Build for macOS
```bash
npm run build-mac
```

#### Build for Linux
```bash
npm run build-linux
```

#### Build for All Platforms
```bash
npm run build-all
```

Built applications will be available in the `frontend/dist/` directory.

## Platform-Specific Requirements

### Windows
- Windows 10 or later
- Visual Studio Build Tools (for PyInstaller)

### macOS
- macOS 10.13 or later
- Xcode Command Line Tools

### Linux
- Most Linux distributions supported
- AppImage format for distribution

## Deployment

### Windows
- Use the generated `.exe` installer (NSIS)
- Distribute via Microsoft Store, website download, or enterprise deployment

### macOS
- Use the generated `.dmg` file
- Can be distributed via Mac App Store or direct download
- For App Store distribution, additional code signing required

### Linux
- Use the generated AppImage file
- Can be distributed via package managers or direct download

## Code Signing (Recommended for Production)

### Windows
```bash
# Set certificate in electron-builder config
"win": {
  "certificateFile": "path/to/cert.pfx",
  "certificatePassword": "password"
}
```

### macOS
```bash
# Set certificates in electron-builder config
"mac": {
  "identity": "Developer ID Application: Your Name",
  "entitlements": "path/to/entitlements.plist"
}
```

## Troubleshooting

### Backend Build Issues
- Ensure all Python dependencies are installed
- Check that PyInstaller is compatible with your Python version
- For Windows, ensure Visual C++ Build Tools are installed

### Electron Build Issues
- Clear node_modules and reinstall if issues persist
- Check electron-builder documentation for platform-specific requirements
- Ensure backend executable is built before Electron build

### Runtime Issues
- Verify backend executable permissions (especially on Linux/macOS)
- Check that all required shared libraries are included
- Test on target platform before distribution

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build and Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-node@v2
      with:
        node-version: '16'
    - uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        cd frontend
        npm install
        cd ../backend
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build
      run: |
        cd frontend
        npm run build-all

    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: robomentor-${{ matrix.os }}
        path: frontend/dist/
```

## File Structure After Build

```
frontend/dist/
├── win/           # Windows builds
│   └── RoboMentor Setup X.X.X.exe
├── mac/           # macOS builds
│   └── RoboMentor-X.X.X.dmg
└── linux/         # Linux builds
    └── RoboMentor-X.X.X.AppImage
```

Each platform build includes the Electron app and the bundled Python backend executable.
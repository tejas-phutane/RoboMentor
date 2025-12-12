#!/usr/bin/env python3
"""
Build script for RoboMentor Python backend using PyInstaller.
"""

import os
import sys
import subprocess
import platform

def build_backend():
    """Build the Python backend into a standalone executable."""
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    os.chdir(backend_dir)

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', 'robomentor-backend',
        '--distpath', 'dist',
        '--workpath', 'build',
        '--exclude', 'PyQt5',
        '--exclude', 'PyQt6',
        '--exclude', 'PySide2',
        'main.py'
    ]

    # Add platform-specific options
    if platform.system() == 'Windows':
        cmd.extend(['--hidden-import', 'win32api', '--hidden-import', 'win32con'])
    elif platform.system() == 'Darwin':  # macOS
        cmd.extend(['--hidden-import', 'objc'])
    elif platform.system() == 'Linux':
        cmd.extend(['--hidden-import', 'linux'])

    print("Building Python backend...")
    subprocess.check_call(cmd)
    print("Backend build completed successfully!")

if __name__ == '__main__':
    build_backend()
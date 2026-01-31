"""
Quick Setup & Installation Script
Run this first to set up your environment
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("\n🔧 Installing Required Packages...\n")
    print("This may take 5-10 minutes on first run.\n")
    
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("\n✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Installation failed. Try manually:")
        print(f"   pip install -r requirements.txt")
        return False


def verify_setup():
    """Run verification checks"""
    print("\n🔍 Verifying Setup...\n")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️ Python 3.8+ recommended. You may encounter issues.")
    else:
        print("✓ Python version OK")
    
    # Check critical libraries
    libraries = ['rasterio', 'numpy', 'plotly', 'streamlit']
    missing = []
    
    print("\nLibrary Check:")
    for lib in libraries:
        try:
            __import__(lib)
            print(f"  ✓ {lib}")
        except ImportError:
            print(f"  ✗ {lib} - MISSING")
            missing.append(lib)
    
    if missing:
        print(f"\n⚠️ Missing libraries: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All critical libraries installed!")
        return True


def check_data_files():
    """Check if data files are present"""
    print("\n📁 Checking Data Files...\n")
    
    project_root = Path(__file__).parent
    dem_dir = project_root / 'data' / 'raw' / 'zone_53H13SE' / 'DEM'
    ortho_dir = project_root / 'data' / 'raw' / 'zone_53H13SE' / 'ORTHO'
    
    dem_files = list(dem_dir.glob('*.tif')) if dem_dir.exists() else []
    ortho_files = list(ortho_dir.glob('*.tif')) if ortho_dir.exists() else []
    
    print(f"DEM Files: {len(dem_files)}")
    print(f"ORTHO Files: {len(ortho_files)}")
    
    if len(dem_files) > 0 and len(ortho_files) > 0:
        print("\n✅ Data files found!")
        print("\nAvailable files:")
        for dem in dem_files[:3]:  # Show first 3
            print(f"  • {dem.name}")
        return True
    else:
        print("\n⚠️ No data files found.")
        print("\n📥 Next Steps:")
        print("1. Open DATA_DOWNLOAD_GUIDE.md")
        print("2. Download files from FTP server")
        print("3. Place files in data/raw/zone_53H13SE/DEM and ORTHO folders")
        return False


def main():
    print("\n" + "="*70)
    print(" 🌊 AQUA GUARDIANS - Riverathon 1.0 Setup ")
    print("="*70)
    
    # Ask user what to do
    print("\nSetup Options:")
    print("1. Install packages (pip install -r requirements.txt)")
    print("2. Verify installation only")
    print("3. Full setup (install + verify + check data)")
    
    choice = input("\nEnter choice (1/2/3) [3]: ").strip() or "3"
    
    if choice in ['1', '3']:
        if not install_requirements():
            print("\n❌ Setup incomplete. Please fix errors above.")
            return
    
    if choice in ['2', '3']:
        if not verify_setup():
            print("\n❌ Verification failed. Run option 1 to install packages.")
            return
    
    if choice == '3':
        check_data_files()
    
    print("\n" + "="*70)
    print("🚀 Next Steps:")
    print("="*70)
    print("1. Download LiDAR data (see DATA_DOWNLOAD_GUIDE.md)")
    print("2. Test data loading: py src/data_loader.py")
    print("3. Run flood model: py flood_model.py")
    print("4. Launch dashboard: streamlit run dashboard/app.py")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()

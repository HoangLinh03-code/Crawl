import os
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """Dọn dẹp các thư mục build cũ"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_macos():
    """Build cho macOS"""
    print("Building for macOS...")
    
    # Sử dụng pyinstaller để build ứng dụng
    subprocess.run([
        'pyinstaller',
        '--name=GoogleScraper',  # Tên ứng dụng
        '--windowed',            # Ứng dụng không có cửa sổ terminal
        '--add-data=CrawlV2.py:.',  # Thêm file CrawlV2.py vào ứng dụng
        '--add-data=ChromeDriver:ChromeDriver',  # Thêm thư mục ChromeDriver
        '--hidden-import=selenium',  # Thêm các thư viện ẩn
        '--hidden-import=tkinter',
        '--hidden-import=concurrent.futures',
        '--clean',               # Dọn dẹp trước khi build
        '--icon=app_icon.icns',  # Icon cho ứng dụng (nếu có)
        'main.py'                # File chính của ứng dụng
    ], check=True)
    
    # Tạo thư mục release
    os.makedirs('dist/release/macos', exist_ok=True)
    
    # Di chuyển file .app vào thư mục release
    app_path = Path('dist/GoogleScraper.app')
    if app_path.exists():
        shutil.move(str(app_path), 'dist/release/macos/GoogleScraper.app')
        print("macOS build completed successfully!")
    else:
        print("Error: .app file not found!")

def main():
    # Tạo thư mục release
    os.makedirs('dist/release', exist_ok=True)
    
    # Dọn dẹp và build cho macOS
    clean_build_dirs()
    build_macos()
    
    print("\nBuild completed! File .app is in dist/release/macos/")

if __name__ == "__main__":
    main()
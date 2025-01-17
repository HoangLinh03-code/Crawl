import os
import platform
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """Dọn dẹp các thư mục build cũ"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_linux():
    """Build cho Linux"""
    print("Building for Linux...")
    subprocess.run([
        'pyinstaller',
        '--name=GoogleScraper',
        '--windowed',
        '--add-data=CrawlV2.py:.',
        '--add-data=ChromeDriver:ChromeDriver',
        '--hidden-import=selenium',
        '--hidden-import=tkinter',
        '--hidden-import=concurrent.futures',
        '--clean',
        'main.py'
    ], check=True)
    
    # Tạo thư mục phân phối
    os.makedirs('dist/release/linux', exist_ok=True)
    
    # # Copy README và LICENSE
    # shutil.copy('README.md', 'dist/GoogleScraper/')
    # shutil.copy('LICENSE', 'dist/GoogleScraper/')
    
    # Nén thành file tar.gz
    subprocess.run([
        'tar', 
        '-czf', 
        'dist/release/linux/GoogleScraper-linux.tar.gz',
        '-C', 'dist/GoogleScraper',
        '.'
    ], check=True)

# def build_windows():
#     """Build cho Windows"""
#     print("Building for Windows...")
#     try:
#         # Sử dụng wine để build cho Windows trên Linux/macOS
#         if platform.system() != "Windows":
#             print("Running on Linux/macOS. Using wine to build for Windows...")
#             subprocess.run([
#                 'wine', 'pyinstaller',
#                 '--name=GoogleScraper',
#                 '--windowed',
#                 '--add-data=CrawlV2.py;.',  # Dùng ; cho Windows
#                 '--add-data=ChromeDriver;ChromeDriver',
#                 '--hidden-import=selenium',
#                 '--hidden-import=tkinter',
#                 '--hidden-import=concurrent.futures',
#                 '--clean',
#                 'main.py'
#             ], check=True)
#         else:
#             # Nếu đang chạy trên Windows, sử dụng pyinstaller trực tiếp
#             subprocess.run([
#                 'pyinstaller',
#                 '--name=GoogleScraper',
#                 '--windowed',
#                 '--add-data=CrawlV2.py;.',  # Dùng ; cho Windows
#                 '--add-data=ChromeDriver;ChromeDriver',
#                 '--hidden-import=selenium',
#                 '--hidden-import=tkinter',
#                 '--hidden-import=concurrent.futures',
#                 '--clean',
#                 'main.py'
#             ], check=True)
        
#         # Tạo thư mục phân phối
#         os.makedirs('dist/release/windows', exist_ok=True)
        
#         # Nén thành file zip
#         shutil.make_archive(
#             'dist/release/windows/GoogleScraper-windows',
#             'zip',
#             'dist/GoogleScraper'
#         )
#         print("Windows build completed successfully!")
#     except subprocess.CalledProcessError as e:
#         print(f"Error building for Windows: {e}")

# def build_macos():
#     """Build cho macOS"""
#     print("Building for macOS...")
#     subprocess.run([
#         'pyinstaller',
#         '--name=GoogleScraper',
#         '--windowed',
#         '--add-data=CrawlV2.py:.',
#         '--add-data=ChromeDriver:ChromeDriver',
#         '--hidden-import=selenium',
#         '--hidden-import=tkinter',
#         '--hidden-import=concurrent.futures',
#         '--clean',
#         'main.py'
#     ], check=True)
    
#     # Tạo thư mục phân phối
#     os.makedirs('dist/release/macos', exist_ok=True)
    
#     # # Copy README và LICENSE
#     # shutil.copy('README.md', 'dist/GoogleScraper/')
#     # shutil.copy('LICENSE', 'dist/GoogleScraper/')
    
#     # Nén thành file tar.gz
#     subprocess.run([
#         'tar', 
#         '-czf', 
#         'dist/release/macos/GoogleScraper-macos.tar.gz',
#         '-C', 'dist/GoogleScraper',
#         '.'
#     ], check=True)

def main():
    # Tạo thư mục release
    os.makedirs('dist/release', exist_ok=True)
    
    # Build cho cả 3 hệ điều hành
    # clean_build_dirs()
    # build_windows()
    
    clean_build_dirs()
    build_linux()
    
    # clean_build_dirs()
    # build_macos()
    
    print("\nBuild completed! Files are in dist/release/")

if __name__ == "__main__":
    main()
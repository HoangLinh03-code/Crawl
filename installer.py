import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
import tempfile

def get_install_path():
    """Xác định đường dẫn cài đặt dựa trên hệ điều hành"""
    system = platform.system()
    home = str(Path.home())
    
    if system == 'Windows':
        return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'GoogleScraper')
    elif system == 'Darwin':  # macOS
        return os.path.join(home, 'Applications', 'GoogleScraper')
    else:  # Linux
        return os.path.join(home, '.local', 'bin', 'GoogleScraper')

def create_shortcut():
    """Tạo shortcut dựa trên hệ điều hành"""
    system = platform.system()
    install_path = get_install_path()
    
    if system == 'Windows':
        # Tạo shortcut trên Windows
        import winshell
        desktop = winshell.desktop()
        path = os.path.join(desktop, "GoogleScraper.lnk")
        target = os.path.join(install_path, "GoogleScraper.exe")
        winshell.CreateShortcut(path, target)
        
    elif system == 'Darwin':  # macOS
        # Không cần tạo shortcut trên macOS vì đã ở Applications
        pass
        
    else:  # Linux
        # Tạo .desktop file cho Linux
        desktop_file = """[Desktop Entry]
Name=GoogleScraper
Exec={}/GoogleScraper
Type=Application
Categories=Utility;
""".format(install_path)
        
        desktop_path = os.path.expanduser('~/.local/share/applications/googlescraper.desktop')
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        os.chmod(desktop_path, 0o755)

def main():
    """Hàm cài đặt chính"""
    print("Installing GoogleScraper...")
    
    # Xác định đường dẫn cài đặt
    install_path = get_install_path()
    
    # Tạo thư mục cài đặt nếu chưa tồn tại
    os.makedirs(install_path, exist_ok=True)
    
    # Copy các file cần thiết
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for item in os.listdir(current_dir):
        if item not in ['.git', '__pycache__', 'build', 'dist']:
            src = os.path.join(current_dir, item)
            dst = os.path.join(install_path, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    
    # Tạo shortcut
    create_shortcut()
    
    print(f"\nInstallation completed!")
    print(f"GoogleScraper has been installed to: {install_path}")
    print("\nYou can now launch GoogleScraper from your applications menu.")

if __name__ == "__main__":
    main()
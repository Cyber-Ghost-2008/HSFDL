import os
import subprocess
import sys
import shutil
import zipfile
import requests

def install_dependencies():
    print("Installing dependencies...")
    try:
        import pip
    except ImportError:
        print("Pip not found. Installing pip...")
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        import pip
    
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def download_ffmpeg_windows():
    print("Downloading ffmpeg for Windows... Please Wait Few Minuts...")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_zip_path = os.path.join(os.getenv('TEMP'), 'ffmpeg.zip')
    ffmpeg_extract_path = os.path.join(os.getenv('TEMP'), 'ffmpeg')

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(ffmpeg_zip_path, 'wb') as file:
            file.write(response.content)
        print("ffmpeg downloaded successfully.")
    except requests.RequestException as e:
        print(f"Failed to download ffmpeg: {e}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_extract_path)
        print("ffmpeg extracted successfully.")
    except zipfile.BadZipFile as e:
        print(f"Failed to extract ffmpeg: {e}")
        sys.exit(1)

    for root, dirs, files in os.walk(ffmpeg_extract_path):
        if 'ffmpeg.exe' in files:
            return os.path.join(root, 'ffmpeg.exe')

    return None

def download_ffmpeg_linux():
    print("Installing ffmpeg for Linux...")
    try:
        subprocess.check_call(['sudo', 'apt', 'install', '-y', 'ffmpeg'])
        print("ffmpeg installed successfully.")
        return shutil.which('ffmpeg')
    except subprocess.CalledProcessError as e:
        print(f"Failed to install ffmpeg: {e}")
        return None

def download_ffmpeg_mac():
    print("Installing ffmpeg for macOS...")
    try:
        subprocess.check_call(['/bin/bash', '-c', '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'])
        subprocess.check_call(['brew', 'install', 'ffmpeg'])
        print("ffmpeg installed successfully.")
        return shutil.which('ffmpeg')
    except subprocess.CalledProcessError as e:
        print(f"Failed to install ffmpeg: {e}")
        return None

def copy_to_paths(ffmpeg_path):
    print("Copying ffmpeg to system paths...")
    paths = [
        os.path.join(os.getenv('SystemRoot'), 'System32'),
        os.path.join(os.getenv('SystemRoot'), 'SysWOW64'),
        os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Microsoft', 'WindowsApps')
    ]

    for path in paths:
        try:
            shutil.copy(ffmpeg_path, path)
            print(f"Copied ffmpeg to {path}")
        except Exception as e:
            print(f"Failed to copy ffmpeg to {path}: {e}")

if __name__ == "__main__":
    install_dependencies()
    
    ffmpeg_path = None
    if sys.platform.startswith('win'):
        ffmpeg_path = download_ffmpeg_windows()
        if ffmpeg_path:
            copy_to_paths(ffmpeg_path)
        else:
            print("Failed to locate ffmpeg executable.")
    elif sys.platform.startswith('linux'):
        ffmpeg_path = download_ffmpeg_linux()
    elif sys.platform.startswith('darwin'):  # macOS
        ffmpeg_path = download_ffmpeg_mac()
    
    if not ffmpeg_path:
        print("Failed to install ffmpeg. Please install it manually.")
    else:
        print("ffmpeg installed successfully.")

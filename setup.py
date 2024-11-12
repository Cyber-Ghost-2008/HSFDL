import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import shutil

# Define the required packages for main.py
REQUIRED_PACKAGES = ["yt-dlp", "tqdm"]

# Detect if running on Termux
def is_termux():
    return "com.termux" in os.getenv("PREFIX", "")

# Download and install ffmpeg if not present
def install_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ffmpeg is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ffmpeg not found. Installing ffmpeg...")

        system = platform.system().lower()
        ffmpeg_url = None

        if is_termux():
            # Use Termux's package manager for ffmpeg
            subprocess.run(['pkg', 'install', '-y', 'ffmpeg'], check=True)
            print("ffmpeg installed via Termux's package manager.")
        elif system == "darwin":  # macOS
            try:
                subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                print("ffmpeg installed via Homebrew.")
            except FileNotFoundError:
                print("Homebrew not found. Please install Homebrew or install ffmpeg manually.")
                sys.exit(1)
        elif system == "windows":
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            ffmpeg_zip = "ffmpeg-release-essentials.zip"
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)

            # Extract to Program Files or a directory in PATH
            extract_path = os.path.join("C:\\", "ffmpeg")
            if not os.path.exists(extract_path):
                os.makedirs(extract_path)
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(ffmpeg_zip)

            # Add to PATH
            ffmpeg_bin_path = os.path.join(extract_path, "bin")
            if ffmpeg_bin_path not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
                print(f"ffmpeg installed to {ffmpeg_bin_path} and added to PATH.")

        elif system == "linux":
            ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
            ffmpeg_archive = "ffmpeg.tar.xz"
            urllib.request.urlretrieve(ffmpeg_url, ffmpeg_archive)

            # Extract and move to /usr/local/bin
            extract_path = "/usr/local/bin"
            with tarfile.open(ffmpeg_archive, 'r:xz') as tar_ref:
                tar_ref.extractall(extract_path)
            os.remove(ffmpeg_archive)
            print("ffmpeg installed and added to PATH.")
        else:
            print("Unsupported OS. Please install ffmpeg manually.")
            sys.exit(1)

# Install Python dependencies
def install_requirements():
    print("Installing Python requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])  # Update pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", *REQUIRED_PACKAGES])

def main():
    print("Setting up the environment for main.py...")

    # Check and install ffmpeg if necessary
    install_ffmpeg()

    # Install required Python packages
    install_requirements()

    print("Setup complete. You can now run main.py.")

if __name__ == "__main__":
    main()

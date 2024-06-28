import subprocess
import sys
import os
import time
from yt_dlp import YoutubeDL
from tqdm import tqdm

# ANSI color codes for terminal output
C_CYAN = '\033[96m'       # Light Cyan
C_GREEN = '\033[92m'      # Light Green
C_YELLOW = '\033[93m'     # Light Yellow
C_RED = '\033[91m'        # Light Red
C_BLUE = '\033[94m'       # Light Blue
C_MAGENTA = '\033[95m'    # Light Magenta
C_WHITE = '\033[97m'      # Light White

C_DARK_CYAN = '\033[36m'      # Dark Cyan
C_DARK_GREEN = '\033[32m'     # Dark Green
C_DARK_YELLOW = '\033[33m'    # Dark Yellow
C_DARK_RED = '\033[31m'       # Dark Red
C_DARK_BLUE = '\033[34m'      # Dark Blue
C_DARK_MAGENTA = '\033[35m'   # Dark Magenta
C_GRAY = '\033[90m'           # Dark Gray
C_LIGHT_GRAY = '\033[37m'     # Light Gray

C_RESET = '\033[0m'        # Reset to default color


# Function to locate or install ffmpeg based on the operating system
def locate_or_install_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{C_YELLOW}ffmpeg not found. Installing ffmpeg...{C_RESET}")
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
            else:
                print(f"{C_RED}Unsupported OS: {sys.platform}. Please install ffmpeg manually.{C_RESET}")
        except subprocess.CalledProcessError:
            print(f"{C_RED}Failed to install ffmpeg. Please install it manually.{C_RESET}")

# Function to generate output template based on URL and file extension
def get_output_template(url, file_ext):
    save_path = os.path.expanduser('~/Downloads/')  # Replace with your desired save path
    return os.path.join(save_path, f'%(title)s.{file_ext}')

# Function to print video information before download
def print_video_info(url, file_format, ydl_opts):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            file_name = ydl.prepare_filename(info_dict)
            file_type = 'mp4' if file_format == 1 else 'mp3' if file_format == 2 else 'original format'
            file_size = info_dict.get('filesize', 'Unknown')
            print(f"{C_BLUE}File Name: {file_name}")
            print(f"File Type: {file_type}")
            print(f"Source URL: {url}")
            print(f"File Size: {file_size} bytes")
            print(f"Save Path: {os.path.dirname(file_name)}{C_RESET}")
            return file_name, file_size
    except Exception as e:
        print(f"{C_RED}Error fetching video information: {e}{C_RESET}")
        return None, None

# Function to download video(s) based on the provided URL and format
def download_video(url, file_format):
    devnull = open(os.devnull, 'w')
    try:
        subprocess.run(['youtube-dl', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{C_YELLOW}youtube-dl not found. Installing youtube-dl...{C_RESET}")
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "youtube-dl"], stdout=devnull, stderr=devnull)

    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "youtube-dl"], stdout=devnull, stderr=devnull)

    locate_or_install_ffmpeg()

    file_ext = 'mp4' if file_format == 1 else 'mp3' if file_format == 2 else '%(ext)s'

    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best' if file_format == 1 else 'bestaudio/best',
        'outtmpl': get_output_template(url, file_ext),
        'noplaylist': True,
        'playliststart': 1,
        'playlistend': 999,
        'progress_hooks': [my_hook],
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '32', '-s', '32', '--split=16', '--min-split-size=1M', '--max-connection-per-server=16'],  # Adjust values for optimal performance
        'cachedir': False,
        'nocheckcertificate': True,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'extractor-args': 'youtube:player_client=web',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        file_name, file_size = print_video_info(url, file_format, ydl_opts)
        if file_name and file_size:
            with tqdm(total=file_size if file_size != 'Unknown' else 100, unit='B', unit_scale=True, desc="Downloading", colour='yellow', bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            print(f"\n{C_GREEN}Downloaded video(s) from: {url}{C_RESET}")
        else:
            print(f"{C_RED}Failed to fetch video information. Aborting download.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}Error downloading video(s): {e}{C_RESET}")
    finally:
        sys.exit()

# Function to display progress bar for download
def my_hook(d):
    global pbar
    if d['status'] == 'finished':
        pbar.close()
        print(f"\n{C_GREEN}Download completed{C_RESET}")
    elif d['status'] == 'error':
        print(f"{C_RED}Error during download: {d.get('error_message')}{C_RESET}")

if __name__ == "__main__":
    pbar = None

    # ASCII art with color changes
    while True:
        try:
            ascii_art = f""" {C_RED}
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*##*@@@@@@@@****%@@@%*++++#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    .%@@@@@%    *@*.        -@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-      #@@@@#    *+   .*#*:   :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-       +@@@%    *=   =@@@#   .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    .   -@@#    *@-   :--   :%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    @=   .%#    *@*:        =%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    @@*    -    *:   :*#*-    +@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    @@@%.            #@@@@     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    @@@@@-      :    .+#*-    :*.  :%@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@-    @@@@@@+     **.          +@:    +@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@*===+@@@@@@@#====%@@#+=----+#@@@%=--*@@@@@@@@@@@@@@@@@@@@@@@@
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
                                                     ___________________☺___________________                
                                                            ||                    ||
                                                    ♥ ************************************** ♥
                                                    ♥ *                                    * ♥
                                                    ♥ * {C_RESET} {C_GREEN}    HIGH SPEED FILE DOWNLOADER {C_RESET}  {C_RED} * ♥
                                                    ♥ *                                    * ♥
                                                    ♥ ************************************** ♥
    {C_RESET}
            """

            # Clear the terminal based on the OS
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')

            print(ascii_art)

            video_url = input(f"{C_DARK_YELLOW}Enter the video URL or playlist URL: ")
            print(f"{C_BLUE}Choose your file format:")
            print("1. mp4")
            print("2. mp3")
            print("3. Original file format")
            file_format = int(input(f"{C_DARK_YELLOW}Enter your choice: "))

            download_video(video_url, file_format)

        except ValueError:
            print("Invalid input. Please enter a number.")

        # Delay for 0.5 seconds before restarting
        time.sleep(0.5)

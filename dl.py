import subprocess
import sys
import os
from yt_dlp import YoutubeDL
from tqdm import tqdm
from rich.console import Console
import asyncio

# ANSI color codes
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_RESET = '\033[0m'

console = Console()

# ASCII Art
ascii_art = f"""
{C_RED}                                            
                                            
                              ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓██████████████▓▒░ ░▒▓██████▓▒░  
                              ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                              ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                              ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░ 
                              ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                              ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                              ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
                                                                                
                                                                                
                                                  ___________________☺__________________
                                                        ||                    ||
                                                ♥ ************************************** ♥
                                                ♥ *                                    * ♥
                                                ♥ *     HIGH SPEED FILE DOWNLOADER     * ♥
                                                ♥ *                                    * ♥
                                                ♥ ************************************** ♥
    {C_RESET}
"""

# Function to locate or install ffmpeg based on the operating system
def locate_or_install_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(f"[yellow]ffmpeg not found. Installing ffmpeg...[/yellow]")
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
            elif sys.platform == 'win32':
                subprocess.run(['winget', 'install', 'ffmpeg'], check=True)
        except subprocess.CalledProcessError:
            console.print(f"[red]Failed to install ffmpeg. Please install it manually.[/red]")

# Function to download video(s) asynchronously
async def download_video(url, file_format, quality=None):
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "yt-dlp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    locate_or_install_ffmpeg()

    file_ext = 'mp4' if file_format == 1 else 'mp3' if file_format == 2 else '%(ext)s'
    
    # Ensure only one progress bar is managed
    global pbar
    pbar = None

    ydl_opts = {
        'format': quality if file_format == 1 else 'bestaudio/best',
        'outtmpl': get_output_template(url, file_ext),
        'noplaylist': True,
        'progress_hooks': [my_hook],
        'quiet': True,
        'noprogress': True  # Disable internal progress indicator
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])  # Run download in a thread to avoid blocking
        console.print(f"\n[green]Downloaded video(s) from: {url}[/green]")
    except Exception as e:
        console.print(f"[red]Error downloading video(s): {e}[/red]")
        if 'Requested format is not available' in str(e):
            console.print(f"[yellow]Requested format is not available. Listing available formats for the URL: {url}[/yellow]")
            list_formats(url)
            new_quality = input("Choose a new quality from the available formats (enter the format code): ").strip()
            await download_video(url, file_format, new_quality)

# Function to list available formats for a given URL
def list_formats(url):
    with YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [info])
        console.print(f"\nAvailable formats for: {url}")
        for f in formats:
            console.print(f"format: {f['format_id']}, ext: {f['ext']}, resolution: {f.get('resolution', 'N/A')}, note: {f.get('format_note', 'N/A')}")

# Function to generate output template based on URL and file extension
def get_output_template(url, file_ext):
    save_path = os.path.expanduser('~/Downloads/')  # Replace with your desired save path
    return os.path.join(save_path, f'%(title)s.{file_ext}')

# Function to display progress bar for download
def my_hook(d):
    global pbar
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] is not None:
            if pbar is None:
                pbar = tqdm(total=d['total_bytes'], unit='B', unit_scale=True, desc=f"{C_YELLOW}Downloading{C_RESET}")
            pbar.update(d['downloaded_bytes'] - pbar.n)
        else:
            if pbar is None:
                pbar = tqdm(unit='B', unit_scale=True, desc=f"{C_YELLOW}Downloading{C_RESET}")
            pbar.update(d['downloaded_bytes'] - pbar.n)
    elif d['status'] == 'finished':
        if pbar is not None:
            pbar.close()
            pbar = None
        console.print(f"\n[green]Download completed[/green]")

def main():
    print(ascii_art)

    url = input("Enter the video URL or playlist URL: ").strip()
    format_options = ["mp4", "mp3", "Original file format"]

    for idx, fmt in enumerate(format_options):
        print(f"{idx + 1}. {fmt}")
    file_format = int(input("Choose your file format (enter the number): "))

    asyncio.run(download_video(url, file_format))

if __name__ == "__main__":
    pbar = None
    main()

import subprocess
import sys
import os
from yt_dlp import YoutubeDL
import asyncio
from tqdm import tqdm

# Check requirements
def check_requirements():
    try:
        import yt_dlp
        import tqdm
    except ImportError:
        print("Please install the requirements by executing 'python3 setup.py'")
        sys.exit(1)

# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Please install ffmpeg for this program to run properly.")
        sys.exit(1)

# Asynchronous video download function
async def download_video(url, file_format, quality=None):
    check_requirements()
    check_ffmpeg()

    file_ext = 'mp4' if file_format == 1 else 'mp3' if file_format == 2 else '%(ext)s'
    ydl_opts = {
        'format': quality if file_format == 1 else 'bestaudio/best',
        'outtmpl': get_output_template(file_ext),
        'noplaylist': True,
        'quiet': True,
        'noprogress': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        print(f"\nDownloaded video from: {url}")
    except Exception as e:
        print(f"Error downloading video: {e}")
        if 'Requested format is not available' in str(e):
            list_formats(url)
            new_quality = input("Choose a new quality from the available formats (enter the format code): ").strip()
            await download_video(url, file_format, new_quality)

# List available formats for URL
def list_formats(url):
    with YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [info])
        print(f"\nAvailable formats for: {url}")
        for f in formats:
            print(f"format: {f['format_id']}, ext: {f['ext']}, resolution: {f.get('resolution', 'N/A')}, note: {f.get('format_note', 'N/A')}")

# Generate output path
def get_output_template(file_ext):
    save_path = os.path.expanduser('~/Downloads')  # Default download location
    return os.path.join(save_path, f'%(title)s.{file_ext}')

# Main function
def main():
    url = input("Enter the video URL or playlist URL: ").strip()
    format_options = ["mp4", "mp3", "Original file format"]

    for idx, fmt in enumerate(format_options):
        print(f"{idx + 1}. {fmt}")
    file_format = int(input("Choose your file format (enter the number): "))

    asyncio.run(download_video(url, file_format))

if __name__ == "__main__":
    main()

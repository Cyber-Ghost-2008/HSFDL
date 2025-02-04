import sys, os, subprocess
from yt_dlp import YoutubeDL
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QProgressBar, QFileDialog, QMenuBar, QHBoxLayout)

# Dependency Check
def check_dependencies():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Install ffmpeg to run this program.")
        sys.exit(1)

# Download Thread
class DownloadThread(QThread):
    progress = pyqtSignal(int, float, float, str, float)  # Progress %, Downloaded MB, ETA, File Name, File Size
    finished = pyqtSignal(str)

    def __init__(self, url, file_format, quality, download_dir):
        super().__init__()
        self.url, self.file_format, self.quality, self.download_dir = url, file_format, quality, download_dir

    def run(self):
        check_dependencies()
        file_ext = 'mp4' if self.file_format == 'MP4' else 'mp3' if self.file_format == 'MP3' else '%(ext)s'
        output = os.path.join(self.download_dir, '%(title)s.' + file_ext)

        ydl_opts = {
            'format': f"bestvideo[ext=mp4]+bestaudio/best" if file_ext == 'mp4' and self.quality else "bestaudio/best",
            'outtmpl': output, 'noplaylist': True, 'quiet': True, 'progress_hooks': [self.hook],
            'ffmpeg_location': 'ffmpeg.exe',  # Path to ffmpeg
            'http_chunk_size': 1024 * 512  # Speed boost
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(self.url, download=False)
                file_size = result.get('filesize', 0) / 1e6  # Size in MB
                file_name = result.get('title', 'Unknown')

                ydl.download([self.url])

            self.finished.emit("Download Complete!")
        except Exception as e:
            self.finished.emit(f"Error: {e}")

    def hook(self, d):
        percent = 0
        downloaded = 0
        eta = 0.0
        file_name = ''
        file_size = 0

        if d['status'] == 'downloading':
            percent = d.get('percent', 0) * 100
            downloaded = d.get('downloaded_bytes', 0) / 1e6  # Convert bytes to MB
            eta = d.get('eta', 0) if d.get('eta', 0) is not None else 0.0  # Ensure eta is a valid float
            file_name = d.get('filename', 'Unknown')  # Get file name
            file_size = d.get('total_bytes', 0) / 1e6  # Size in MB

        # Emitting signal to update GUI
        self.progress.emit(int(percent), round(downloaded, 2), eta, file_name, file_size)

# Main UI
class FileDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.download_dir, self.theme = os.path.expanduser('~/Downloads'), 'dark'
        self.initUI()

    def initUI(self):
        self.setWindowTitle("High Speed File Downloader © Menula Geeneth")
        self.setGeometry(100, 100, 500, 400)
        self.apply_theme()

        layout = QVBoxLayout()
        menu_bar = QMenuBar(self)
        settings_menu = menu_bar.addMenu("Settings")

        theme_action, dir_action = QAction("Toggle Theme", self), QAction("Set Download Directory", self)
        theme_action.triggered.connect(self.toggle_theme), dir_action.triggered.connect(self.set_download_directory)
        settings_menu.addActions([theme_action, dir_action])
        layout.setMenuBar(menu_bar)

        self.title = QLabel("High Speed File Downloader", self)
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.url_input = QLineEdit(self, placeholderText="Enter the URL...")
        layout.addWidget(self.url_input)

        self.format_selector = QComboBox(self)
        self.format_selector.addItems(["MP4", "MP3", "Other"])
        self.format_selector.currentIndexChanged.connect(self.toggle_quality_selection)
        layout.addWidget(self.format_selector)

        self.quality_selector = QComboBox(self)
        self.quality_selector.addItems(["360p", "480p", "720p", "1080p", "Highest"])
        layout.addWidget(self.quality_selector)

        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Waiting for input...")
        layout.addWidget(self.status_label)

        self.download_info = QLabel("")
        layout.addWidget(self.download_info)

        self.setLayout(layout)
        self.toggle_quality_selection()

    def toggle_quality_selection(self):
        self.quality_selector.setVisible(self.format_selector.currentText() == "MP4")

    def start_download(self):
        url, file_format, quality = self.url_input.text(), self.format_selector.currentText(), self.quality_selector.currentText()
        if not url:
            self.status_label.setText("Please enter a valid URL!")
            return

        self.status_label.setText("Downloading...")
        self.progress_bar.setValue(0)

        self.download_thread = DownloadThread(url, file_format, quality if file_format == "MP4" else None, self.download_dir)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_complete)
        self.download_thread.start()

    def update_progress(self, percent, downloaded, eta, file_name, file_size):
        # Updating progress bar
        self.progress_bar.setValue(percent)

        # Update the download info label with file name, size, and progress info
        self.download_info.setText(f"File: {file_name}\nSize: {file_size:.2f} MB\nDownloaded: {downloaded} MB | ETA: {eta}s")

    def download_complete(self, message):
        self.progress_bar.setValue(100)
        self.status_label.setText(message)

    def set_download_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if dir_path: self.download_dir = dir_path

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet("background-color: #121212; color: white;" if self.theme == 'dark' else "background-color: white; color: black;")

# Run App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileDownloader()
    window.show()
    sys.exit(app.exec())

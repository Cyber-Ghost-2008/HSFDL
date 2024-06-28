import os
import subprocess
import sys

def install_dependencies():
    # Install pip if not already installed
    try:
        import pip
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

    # Install dependencies from requirements.txt
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
except subprocess.CalledProcessError as e:
    print(f"Failed to upgrade pip: {e}")


def add_to_path():
    # Get the directory where the current Python executable is located
    python_scripts_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
    
    # Get the current PATH environment variable
    current_path = os.environ.get('PATH', '')

    # Add new paths to the PATH environment variable if not already present
    if python_scripts_dir not in current_path:
        current_path += os.pathsep + python_scripts_dir

    # Set the updated PATH environment variable
    os.environ['PATH'] = current_path

    # Add paths to the user environment variables (permanent change)
    if os.name == 'nt':  # Windows
        subprocess.run(['setx', 'PATH', current_path], check=True)
    else:  # macOS/Linux
        with open(os.path.expanduser('~/.bashrc'), 'a') as bashrc:
            bashrc.write(f'\nexport PATH="{current_path}"\n')
        # Source the .bashrc to apply changes immediately (for the current session)
        subprocess.run(['source ~/.bashrc'], shell=True, check=True)

if __name__ == "__main__":
    install_dependencies()
    add_to_path()

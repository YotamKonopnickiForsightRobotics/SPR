import tkinter as tk
from tkinter import ttk
import paramiko
import os
import re
from datetime import datetime
import zipfile

# ==============================
# Configuration Constants
# ==============================

# SSH connection settings
SSH_HOST = "192.168.16.225"
SSH_PORT = 22
SSH_USERNAME = "lab1"
SSH_PASSWORD = "rubyruby"

# Local paths
LOCAL_ZIP_PATH = "SPR.zip"
LOCAL_DESCRIPTION_FILENAME = "description.txt"

# Remote command/file paths
REMOTE_LAST_VC_PATH_FILE = "/opt/fs_data/last_vc_run_path.txt"
REMOTE_VC_LOG_FILENAME = "VC.txt"
REMOTE_RUN_SUBDIR = "/run"
REMOTE_LOG_SUBDIR = "/run/log"
REMOTE_RECORDINGS_SUBDIR = "recordings"
REMOTE_ZIP_NAME = "SPR.zip"

# Directories to copy from the remote machine
dirs_to_copy = [
    "Camera_Rig_register_points", "config", "Face_Reconstruction_log", "Left_register_points", "Limbus",
    "Microscope", "registration_log", "registrations", "Right_register_points", "Speculum_log",
    "Tool_detection_log", "tool_tip_detection", "Tracking", "Tracking_to_microscope", "VPP_log_left",
    "VPP_log_right"
]

# Files to copy from the remote machine
files_to_copy = [
    "aruco_config_json", "Augmentation.stdout.txt", "cataract_tools_oryom_fim_toolset.json",
    "Microscope.stdout.txt", "rc_sys_ts_sync.log", "renderer_process.stdout.txt", "RKS.stdout.txt",
    "VisionComputer.global.ini", "VisionComputer.local.ini", "VPP.log"
]



def get_path_to_last_pcap(client, recordings_path):
    """
    Extracts and returns paths to the 5 most recent .pcap files from a recordings directory on a remote machine.
    """
    all_pcaps = ssh_run_command(client, f"cd {recordings_path} && ls")

    matches = re.findall(r'([^\s]+?\.pcap)(\d+)', all_pcaps)

    # Convert to tuples: (full_filename, number as int)
    files_with_numbers = [(f"{name}{num}", int(num)) for name, num in matches]

    # Sort by number descending
    files_with_numbers.sort(key=lambda x: x[1], reverse=True)

    # Take top 5 filenames
    top_5_files = [name for name, _ in files_with_numbers[:5]]

    for i in range(0, min(5, len(top_5_files))):
        top_5_files[i] = f"{recordings_path}/{top_5_files[i]}"

    return top_5_files



def build_files_string(files_lists):
    """
    Receives a list of lists of file paths and returns a single space-separated string of all paths.
    """
    files_string = ""
    for file_list in files_lists:
        for file_path in file_list:
            files_string += f"{file_path} "
    return files_string



def get_newest(strings):
    """
    Given a list of strings that contain date-time patterns, returns the string with the most recent timestamp.
    """
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"

    timestamps = []

    for s in strings:
        match = re.search(pattern, s)
        if match:
            ts = datetime.strptime(match.group(), "%Y-%m-%d_%H-%M-%S")
            timestamps.append((ts, s))  # keep original string

    # Get the most recent
    latest_ts, latest_str = max(timestamps)
    return latest_str



def save_and_quit():
    """
    Saves the user-entered description text into description.txt and closes the GUI window.
    """
    text = text_box.get("1.0", tk.END).strip()
    with open(LOCAL_DESCRIPTION_FILENAME, "w", encoding="utf-8") as f:
        f.write(text)
    root.destroy()



def ssh_run_command(client, command):
    """
    Runs a shell command over an existing SSH connection and returns stdout or stderr output.
    """
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()

    return output if output else error



def start_gui_window():
    """
    Starts the GUI main loop (for entering description).
    """
    root.mainloop()



def copy_remote_file_to_local(ssh_client, remote_path, local_path):
    """
    Copies a file from the remote machine to the local one using an existing SSH connection.
    """
    sftp = ssh_client.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()



def add_description_to_zip():
    """
    Appends the description.txt file into the existing ZIP file and then deletes it from the local system.
    """
    with zipfile.ZipFile(LOCAL_ZIP_PATH, "a") as zip_ref:
        zip_ref.write(LOCAL_DESCRIPTION_FILENAME, arcname=LOCAL_DESCRIPTION_FILENAME)
    os.remove(LOCAL_DESCRIPTION_FILENAME)



def zip_log_files():
    """
    Establishes SSH connection, determines current run folder, finds relevant files,
    zips them remotely, copies the ZIP file to local machine, then deletes the remote ZIP.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT)

    current_version_dir = ssh_run_command(client, "cat /opt/fs_data/last_vc_run_path.txt")

    VCLog_path = current_version_dir[:-1] + REMOTE_RUN_SUBDIR + "/" + REMOTE_VC_LOG_FILENAME
    current_version_log_dir = current_version_dir[:-1] + REMOTE_LOG_SUBDIR

    runs_str = ssh_run_command(client, f"cd {current_version_log_dir} && ls")
    runs = runs_str.split("\n")

    current_run_dir = current_version_log_dir + "/" + get_newest(runs)
    print("VCLog path:", VCLog_path)

    zip_path = current_run_dir + "/" + REMOTE_ZIP_NAME
    print("Zip path:", zip_path)
    recordings_path = current_run_dir + "/" + REMOTE_RECORDINGS_SUBDIR

    last_5_pcap_files = get_path_to_last_pcap(client, recordings_path)
    print("last_5_pcap_files:", last_5_pcap_files)

    files_in_log_dir = ssh_run_command(client, f"cd {current_run_dir} && ls")

    paths_to_files_to_copy = []
    paths_to_dirs_to_copy = []

    for file in files_to_copy:
        if file in files_in_log_dir:
            paths_to_files_to_copy.append(f"{current_run_dir}/{file}")
    paths_to_files_to_copy.append(VCLog_path)

    for dir in dirs_to_copy:
        if dir in files_in_log_dir:
            paths_to_dirs_to_copy.append(f"{current_run_dir}/{dir}")

    print("paths_to_files_to_copy:", paths_to_files_to_copy)
    print("paths_to_dirs_to_copy:", paths_to_dirs_to_copy)

    str_of_all_files_to_copy = build_files_string((paths_to_files_to_copy, paths_to_dirs_to_copy, last_5_pcap_files))

    print("str_of_all_files_to_copy:", str_of_all_files_to_copy)

    print("started zipping")
    ssh_run_command(client, f"zip -r {zip_path} {str_of_all_files_to_copy}")
    print("finished zipping")

    print("started copying")
    copy_remote_file_to_local(client, zip_path, LOCAL_ZIP_PATH)
    print("finished copying")
    ssh_run_command(client, f"rm {zip_path}")

    client.close()



def main():
    """
    Launches the GUI, then handles the remote zipping and downloading of logs, then adds local description to the zip.
    """
    start_gui_window()
    zip_log_files()
    add_description_to_zip()


# Set up GUI window
root = tk.Tk()
root.title("Enter Description")
root.geometry("600x400")  # Wider and taller window

# Frame to contain everything
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True, fill="both")

# Label
tk.Label(frame, text="Enter your description:", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 5))

# Text box
text_box = tk.Text(frame, height=12, width=60, font=("Segoe UI", 12))
text_box.pack(fill="both", expand=True)

# Save button
enter_button = tk.Button(frame, text="Save and Close", command=save_and_quit, font=("Segoe UI", 10))
enter_button.pack(pady=(10, 0))



if __name__ == "__main__":
    main()

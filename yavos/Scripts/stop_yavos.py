import os, psutil

def get_pids_by_command(command_substring):
    """
    Finds PIDs of processes whose command line contains the given substring.
    """
    pids = []
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            pid = proc.info['pid']
            if cmdline and any(command_substring in arg for arg in cmdline):
                pids.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return pids


commands_to_find = [
        "recognizer.sh",
        "recognizer.py",
        "arecord",
        "stt.py",
        "media.py",
        "tts.py",
        "MsgBus.py",
        "run_config_server", 
        "http.server",
        "audio_out_bus.py",
        ]

for command_to_find in commands_to_find:
    found_pids = get_pids_by_command(command_to_find)

    if found_pids:
        #print(f"PIDs for processes running '{command_to_find}': {found_pids}")
        print(f"kill {command_to_find} - {found_pids[0]}")
        cmd = f"kill {found_pids[0]}"
        #print(cmd)
        os.system(cmd)
    else:
        print(f"No processes found running '{command_to_find}'.")

os.system("killall python")


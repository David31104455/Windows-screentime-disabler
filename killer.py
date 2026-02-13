import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import winreg

# Global reference to the child process
child_process = None

def get_child_script_path():
    """Get absolute path to child_script.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "child_script.py")

def start_script():
    """Starts the process-killing script as a subprocess"""
    global child_process
    script_path = get_child_script_path()
    
    if not os.path.exists(script_path):
        messagebox.showerror("Error", f"Could not find {script_path}\nPlease ensure child_script.py is in the same directory.")
        return

    if child_process is None:
        try:
            # Use pythonw.exe to run without a console window
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(python_exe):
                python_exe = sys.executable # Fallback if pythonw not found
                
            # Start the child process
            child_process = subprocess.Popen([python_exe, script_path], shell=False)
            
            start_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            status_label.config(text="Status: RUNNING", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start child script: {e}")

def stop_script():
    """Stops the process-killing subprocess"""
    global child_process
    if child_process:
        try:
            child_process.terminate()
            child_process = None
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            status_label.config(text="Status: STOPPED", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop process: {e}")

def add_to_startup():
    """Adds the child_script.py to Windows Startup, effectively registering the child program"""
    try:
        script_path = get_child_script_path()
        if not os.path.exists(script_path):
             messagebox.showerror("Error", f"Could not find {script_path}")
             return

        startup_name = "KillWpcUapApp"
        key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Use pythonw to run silently in background on startup
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
            
        command = f'"{python_exe}" "{script_path}"'

        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, startup_name, 0, winreg.REG_SZ, command)

        messagebox.showinfo("Success", f"Child script added to startup.\nIt will run automatically on boot.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add to startup: {e}")

def remove_from_startup():
    """Removes the script from Windows Startup"""
    try:
        startup_name = "KillWpcUapApp"
        key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, startup_name)

        messagebox.showinfo("Success", "Script removed from startup.")
    except FileNotFoundError:
        messagebox.showwarning("Warning", "Script is not in startup.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove from startup: {e}")

# GUI Setup
root = tk.Tk()
root.title("Screentime Killer Controller")
root.geometry("350x280")

# Styling
title_label = tk.Label(root, text="Process Killer Control", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=10)

status_label = tk.Label(root, text="Status: STOPPED", fg="red", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=5)

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

start_button = tk.Button(frame_controls, text="Start Killing Service", command=start_script, width=20, bg="#e1e1e1")
start_button.pack(pady=5)

stop_button = tk.Button(frame_controls, text="Stop Killing Service", command=stop_script, state=tk.DISABLED, width=20, bg="#e1e1e1")
stop_button.pack(pady=5)

tk.Label(root, text="---------------- Start on Boot ----------------").pack(pady=5)

frame_boot = tk.Frame(root)
frame_boot.pack(pady=5)

startup_button = tk.Button(frame_boot, text="Enable Boot Start", command=add_to_startup, width=18)
startup_button.grid(row=0, column=0, padx=5)

remove_startup_button = tk.Button(frame_boot, text="Disable Boot Start", command=remove_from_startup, width=18)
remove_startup_button.grid(row=0, column=1, padx=5)

root.mainloop()

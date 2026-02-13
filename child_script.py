import ctypes
import time
import sys
import os
from ctypes import wintypes

# Windows API Constants
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400
SYNCHRONIZE = 0x00100000
TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

def get_process_id_by_name(process_name):
    """Finds the Process ID (PID) of a running process by name."""
    snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == -1:
        return None

    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

    if not ctypes.windll.kernel32.Process32First(snapshot, ctypes.byref(entry)):
        ctypes.windll.kernel32.CloseHandle(snapshot)
        return None

    pid = None
    while True:
        try:
            exe_file = entry.szExeFile.decode('utf-8')
        except UnicodeDecodeError:
            exe_file = "" # Skip decode errors
            
        if exe_file.lower() == process_name.lower():
            pid = entry.th32ProcessID
            break
        if not ctypes.windll.kernel32.Process32Next(snapshot, ctypes.byref(entry)):
            break

    ctypes.windll.kernel32.CloseHandle(snapshot)
    return pid

def kill_process_by_pid(pid):
    """Terminates a process given its PID."""
    if pid is None:
        return False
        
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not handle:
        return False
        
    success = ctypes.windll.kernel32.TerminateProcess(handle, 1)
    ctypes.windll.kernel32.CloseHandle(handle)
    return success != 0

def main():
    target_process = "WpcUapApp.exe"
    # High frequency loop
    while True:
        pid = get_process_id_by_name(target_process)
        if pid:
            kill_process_by_pid(pid)
        # Sleep for 1ms to prevent 100% CPU usage but maintain high responsiveness
        time.sleep(0.001)

if __name__ == "__main__":
    main()

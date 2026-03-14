import customtkinter as ctk
import subprocess
import os
import ctypes
import tempfile
import winshell
import socket
import requests
import speedtest
import threading
from tkinter import messagebox

# App Preferences
username = os.getlogin()
app = ctk.CTk()
app.geometry("310x310")
app.title(f"Quick-CMD ({username})")
app.resizable(width=False, height=False)
ctk.set_appearance_mode("system")


# App functions
def open_cmd():
    home_dir = os.path.expanduser("~")
    subprocess.Popen(
        "cmd.exe",
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=home_dir,  # start directory
    )


def open_cmd_admin():
    home_dir = os.path.expanduser("~")
    ctypes.windll.shell32.ShellExecuteW(  # needed to run as admin
        None,  # hwnd
        "runas",  # run as admin
        "cmd.exe",  # file
        None,  # parameters
        home_dir,  # start option
        1,  # show window normal
    )


def open_task_manager():
    subprocess.Popen("taskmgr")


def open_device_manager():
    subprocess.Popen("devmgmt.msc", shell=True)


def open_registry():
    ctypes.windll.shell32.ShellExecuteW(
        None,  # hwnd
        "runas",  # verb: run as admin
        "regedit.exe",  # file to run
        None,  # parameters
        None,  # working directory
        1,  # show window normally
    )


def open_control_panel():
    subprocess.run("control appwiz.cpl", shell=True)


def disk_cleanup():
    subprocess.Popen("cleanmgr")


def del_temp_files():
    def safe_delete_folder(path):
        if not os.path.exists(path):
            return
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # Skip files in use
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.rmdir(dir_path)
                except Exception:
                    pass  # Skip directories in use

    # User temp folder
    user_temp = tempfile.gettempdir()
    safe_delete_folder(user_temp)

    # System temp folder
    system_temp = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
    safe_delete_folder(system_temp)

    # Show when it finished
    messagebox.showinfo(
        "Cleanup Complete", "The temporary files have been deleted successfully."
    )


def del_trash_files():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=True, sound=False)
        messagebox.showinfo(
            "Cleanup Complete", "Your Recycle Bin have been cleared successfully."
        )
    except Exception as e:
        error_message = "The cleanup failed"
        print(f"{error_message}, Error details: {e}")
        messagebox.showerror("Error", "Your Recycle Bin is already empty.")


import os
import shutil
from tkinter import messagebox


def clear_browser_cache():
    try:
        user = os.getlogin()

        # Browser cache locations
        browsers = {
            "Chrome": rf"C:\Users\{user}\AppData\Local\Google\Chrome\User Data\Default\Cache",
            "Edge": rf"C:\Users\{user}\AppData\Local\Microsoft\Edge\User Data\Default\Cache",
            "Firefox": rf"C:\Users\{user}\AppData\Roaming\Mozilla\Firefox\Profiles",
        }

        # Function to safely delete folder contents
        def safe_delete_folder(path):
            if not os.path.exists(path):
                return
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass

        # Clear Chrome and Edge cache
        for browser, path in browsers.items():
            if browser == "Firefox":
                # Firefox has multiple profiles; clear Cache subfolder in each
                if os.path.exists(path):
                    profiles = os.listdir(path)
                    for profile in profiles:
                        cache_path = os.path.join(path, profile, "cache2")
                        safe_delete_folder(cache_path)
            else:
                safe_delete_folder(path)

        messagebox.showinfo("Cleanup Complete", "Browser cache cleared successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear browser cache:\n{e}")


def show_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    public_ip_address = requests.get("https://api.ipify.org").text

    print("Your local IP is: ", ip_address)
    print("Your public IP is:", public_ip_address)
    messagebox.showinfo(
        "IP Addresses", f"Local IP: {ip_address} \nPublic IP: {public_ip_address}"
    )


def internet_speedtest():
    # New window
    speed_window = ctk.CTkToplevel(app)
    speed_window.geometry("260x285")
    speed_window.title("Internet Speed Test")
    speed_window.resizable(width=False, height=False)
    speed_window.transient(app)

    # New UI
    title = ctk.CTkLabel(
        speed_window, text="Internet Speed Test", font=("Segoe UI", 24, "bold")
    )
    title.pack(pady=15)

    download_label = ctk.CTkLabel(
        speed_window, text="Download: -", font=("Segoe UI", 16)
    )
    download_label.pack(pady=5)

    upload_label = ctk.CTkLabel(speed_window, text="Upload: -", font=("Segoe UI", 16))
    upload_label.pack(pady=5)

    ping_label = ctk.CTkLabel(speed_window, text="Ping: -", font=("Segoe UI", 16))
    ping_label.pack(pady=5)

    status_label = ctk.CTkLabel(speed_window, text="Press Start", text_color="#717171")
    status_label.pack(pady=10)

    # Speed Test Logic
    def run_test():
        try:
            # Disable button and gray it out
            start_button.configure(state="disabled", fg_color="gray")

            # Clear previous results
            download_label.configure(text="Download: -")
            upload_label.configure(text="Upload: -")
            ping_label.configure(text="Ping: -")

            status_label.configure(text="Testing internet speed...")

            # Using speedtest-cli
            st = speedtest.Speedtest()

            # Get best server (avoids 403)
            st.get_best_server()

            # Download and upload speeds
            download = st.download() / 1_000_000  # Convert to Mbps
            upload = st.upload() / 1_000_000  # Convert to Mbps

            ping = st.results.ping

            # Update labels with integer numbers
            download_label.configure(text=f"Download: {int(download)} Mbps")
            upload_label.configure(text=f"Upload: {int(upload)} Mbps")
            ping_label.configure(text=f"Ping: {int(ping)} ms")

            status_label.configure(text="Test completed")

        except speedtest.ConfigRetrievalError:
            status_label.configure(text="Server config error")
            download_label.configure(text="Download: -")
            upload_label.configure(text="Upload: -")
            ping_label.configure(text="Ping: -")
        except speedtest.NoMatchedServers:
            status_label.configure(text="No server available")
        except speedtest.SpeedtestException as e:
            status_label.configure(text="Speed test failed")
            download_label.configure(text="Download: -")
            upload_label.configure(text="Upload: -")
            ping_label.configure(text="Ping: -")
            print("Speedtest error:", e)
        finally:
            # Re-enable button and reset color
            start_button.configure(state="normal", fg_color="#1f6aa5")

    def start_test():
        threading.Thread(target=run_test, daemon=True).start()

    # Start Button
    start_button = ctk.CTkButton(
        speed_window,
        text="Start Speed Test",
        command=start_test,
        width=230,
        fg_color="#1f6aa5",
    )
    start_button.pack(pady=15)


# App Title
label = ctk.CTkLabel(app, text="Quick-CMD", fg_color="transparent", font=("Arial", 26))
label.grid(row=0, column=0, columnspan=3, pady=10)

# Button Preferences
button_padx = 5
button_pady = 5

# App Frame
button_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#2a2a2a", border_width=1)
button_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

# App Buttons
cmd_button = ctk.CTkButton(button_frame, text="Terminal", command=open_cmd)
cmd_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)

cmd_admin_button = ctk.CTkButton(
    button_frame, text="Terminal (Admin)", command=open_cmd_admin
)
cmd_admin_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)

reg_button = ctk.CTkButton(button_frame, text="Registry", command=open_registry)
reg_button.grid(row=1, column=0, padx=button_padx, pady=button_pady)

del_app_button = ctk.CTkButton(
    button_frame, text="Delete Apps", command=open_control_panel
)
del_app_button.grid(row=1, column=1, padx=button_padx, pady=button_pady)

devicemgr_button = ctk.CTkButton(
    button_frame, text="Device Manager", command=open_device_manager
)
devicemgr_button.grid(row=2, column=0, padx=button_padx, pady=button_pady)

taskmgr_button = ctk.CTkButton(
    button_frame, text="Task Manager", command=open_task_manager
)
taskmgr_button.grid(row=2, column=1, padx=button_padx, pady=button_pady)

# App frame for Files
file_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#2a2a2a", border_width=1)
file_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

# App Buttons for Files
del_temp_button = ctk.CTkButton(
    file_frame, text="Clear Temp Files", command=del_temp_files
)
del_temp_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)

del_trash_button = ctk.CTkButton(
    file_frame, text="Clear Recycle Bin", command=del_trash_files
)
del_trash_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)

disk_cleanup_button = ctk.CTkButton(
    file_frame, text="Disk Cleanup", command=disk_cleanup
)
disk_cleanup_button.grid(row=1, column=0, padx=button_padx, pady=button_pady)

clear_browser_cache_button = ctk.CTkButton(
    file_frame, text="Cear Browser cache", command=clear_browser_cache
)
clear_browser_cache_button.grid(row=1, column=1, padx=button_padx, pady=button_pady)

# App frame for Network
network_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#2a2a2a", border_width=1)
network_frame.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

# App button for Network
show_ip_button = ctk.CTkButton(network_frame, text="Show IP", command=show_ip)
show_ip_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)

speed_test_button = ctk.CTkButton(
    network_frame, text="Speed Test", command=internet_speedtest
)
speed_test_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)

# Run App
app.mainloop()

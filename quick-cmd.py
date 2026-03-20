# ---- Stuff for the working PyInstaller (.exe) ----
# python -m PyInstaller --onefile --noconsole --clean --name Quick-CMD --icon=media/logo/logo.ico --hidden-import=speedtest --hidden-import=winshell --hidden-import=requests --collect-all customtkinter --collect-all CTkColorPicker --add-data "media/logo/logo.ico;media/logo" quick-cmd.py
import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ---- Libary imports ----
import customtkinter as ctk
import subprocess
import ctypes
import tempfile
import winshell
import winsound
import webbrowser
import socket
import requests
import speedtest
import threading
from CTkColorPicker import AskColor
from tkinter import messagebox, Tk
import json

# ---- Json setting file stuff ----
APP_NAME = "Quick-CMD"

# AppData\Roaming path for persistent settings
appdata_path = os.path.join(os.environ.get("APPDATA"), APP_NAME)
os.makedirs(appdata_path, exist_ok=True)  # create folder if it doesn't exist

# Full path to settings.json
SETTINGS_FILE = os.path.join(appdata_path, "settings.json")


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Load settings at start
settings_data = load_settings()

# Accent color defaults and utilities
DEFAULT_ACCENT_COLOR = "#1f6aa5"


def darker_color(hex_color, factor=0.8):
    try:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return DEFAULT_ACCENT_COLOR


def contrast_color(hex_color):
    try:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # luminance formula
        lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#000000" if lum > 0.5 else "#ffffff"
    except Exception:
        return "#ffffff"


accent_color = settings_data.get("accent_color", DEFAULT_ACCENT_COLOR)
accent_hover_color = darker_color(accent_color)
accent_checkmark_color = contrast_color(accent_color)

accent_buttons = []
accent_checkboxes = []
accent_optionmenus = []


def register_accent_button(button):
    try:
        button.configure(fg_color=accent_color, hover_color=accent_hover_color)
    except Exception:
        pass
    accent_buttons.append(button)


def register_accent_checkbox(checkbox):
    try:
        checkbox.configure(
            fg_color=accent_color,
            hover_color=accent_hover_color,
            checkmark_color=accent_checkmark_color,
        )
    except Exception:
        pass
    accent_checkboxes.append(checkbox)


def register_accent_optionmenu(optionmenu):
    try:
        optionmenu.configure(
            button_color=accent_color,
            button_hover_color=accent_hover_color,
            fg_color=accent_color,
        )
    except Exception:
        pass
    accent_optionmenus.append(optionmenu)


def apply_accent_color(color, save=True):
    global accent_color, accent_hover_color, accent_checkmark_color
    accent_color = color or DEFAULT_ACCENT_COLOR
    accent_hover_color = darker_color(accent_color)
    accent_checkmark_color = contrast_color(accent_color)

    if save:
        settings_data["accent_color"] = accent_color
        save_settings(settings_data)

    for btn in accent_buttons:
        try:
            btn.configure(fg_color=accent_color, hover_color=accent_hover_color)
        except Exception:
            pass

    for chk in accent_checkboxes:
        try:
            chk.configure(
                fg_color=accent_color,
                hover_color=accent_hover_color,
                checkmark_color=accent_checkmark_color,
            )
        except Exception:
            pass

    for opt in accent_optionmenus:
        try:
            opt.configure(
                button_color=accent_color,
                button_hover_color=accent_hover_color,
                fg_color=accent_color,
            )
        except Exception:
            pass


# ---- Update System ----
downloaded_version = "v2.2"


def parse_version(v):
    return tuple(map(int, v.lstrip("v").split(".")))


def check_update():
    try:
        url = f"https://api.github.com/repos/Mahito994/Quick-CMD/releases/latest"
        response = requests.get(url, timeout=3)  # add timeout to prevent freeze
        if response.status_code != 200:
            return
        latest_release = response.json()
        if parse_version(latest_release["tag_name"]) > parse_version(
            downloaded_version
        ):
            root = Tk()
            root.withdraw()  # hide main window
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            result = messagebox.askyesno(
                "Update Available",
                f"A new update ({latest_release['tag_name']}) is available!\n\nDo you want to open the release page?",
            )
            if result:
                webbrowser.open(latest_release["html_url"])
            root.destroy()
    except Exception:
        # silently fail if no internet or request fails
        pass


# Start the update check in a separate thread
threading.Thread(target=check_update, daemon=True).start()

# ---- App Setup ----
username = os.getlogin()
app = ctk.CTk()
app.geometry("310x358")
app.title(f"Quick-CMD ({username})")
app.iconbitmap(resource_path("media/logo/logo.ico"))
app.resizable(width=False, height=False)
ctk.set_appearance_mode(settings_data.get("theme", "system"))

# Show Username loader
if not settings_data.get("show_username", True):
    app.title("Quick-CMD")


# ---- App functions ----
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
    try:
        # Better local IP detection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        public_ip = requests.get("https://api.ipify.org", timeout=3).text
        messagebox.showinfo(
            "IP Addresses", f"Local IP: {local_ip}\nPublic IP: {public_ip}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get IP addresses:\n{e}")


def internet_speedtest():
    # New window
    speed_window = ctk.CTk()
    speed_window.geometry("260x285")
    speed_window.title("Speedtest")
    speed_window.resizable(width=False, height=False)
    speed_window.iconbitmap(resource_path("media/logo/logo.ico"))

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
            st.get_servers()
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
            start_button.configure(
                state="normal", fg_color=accent_color, hover_color=accent_hover_color
            )

    def start_test():
        threading.Thread(target=run_test, daemon=True).start()

    # Start Button
    start_button = ctk.CTkButton(
        speed_window,
        text="Start Speed Test",
        command=start_test,
        width=230,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    start_button.pack(pady=15)
    register_accent_button(start_button)

    speed_window.mainloop()


def closing_app():
    try:
        app.quit()
        app.destroy()
    except:
        pass


def update_special_buttons():
    mode = ctk.get_appearance_mode()

    if mode == "Light":
        fg = "#c7c7c7"  # button background
        hover = "#b0b0b0"
        text_color = "#000000"  # dark text for light mode
    else:
        fg = "#474747"  # dark gray background
        hover = "#373737"
        text_color = "#dce4ee"  # dark text for dark mode

    try:
        exit_button.configure(fg_color=fg, hover_color=hover, text_color=text_color)
        settings_button.configure(fg_color=fg, hover_color=hover, text_color=text_color)
    except:
        pass


def apply_theme(theme):
    ctk.set_appearance_mode(theme)

    color = "#e0e0e0" if ctk.get_appearance_mode() == "Light" else "#2a2a2a"

    try:
        button_frame.configure(fg_color=color)
        file_frame.configure(fg_color=color)
        network_frame.configure(fg_color=color)
        settings_frame.configure(fg_color=color)
    except:
        pass


def settings_menu():
    # Settings window
    setting_app = ctk.CTk()
    setting_app.geometry("420x260")
    setting_app.title("Settings")
    setting_app.resizable(width=False, height=False)
    setting_app.iconbitmap(resource_path("media/logo/logo.ico"))

    # Main grid
    setting_app.grid_columnconfigure((0, 1), weight=1)
    setting_app.grid_rowconfigure(0, weight=1)

    # --- Functions ---
    def update_title():  # Update app title based on checkbox state
        if settings_data.get("show_username", True):
            app.title(f"Quick-CMD ({username})")
        else:
            app.title("Quick-CMD")

    def toggle_username():  # Live update title and saves it
        settings_data["show_username"] = username_var.get()
        save_settings(settings_data)
        update_title()

    def toggle_theme(*args):  # Live update theme and saves it
        update_special_buttons()
        theme = theme_var.get().lower()
        ctk.set_appearance_mode(theme)
        settings_data["theme"] = theme
        save_settings(settings_data)

        # Update frame colors dynamically
        color = "#e0e0e0" if theme == "light" else "#2a2a2a"
        try:
            button_frame.configure(fg_color=color)
            file_frame.configure(fg_color=color)
            network_frame.configure(fg_color=color)
            settings_frame.configure(fg_color=color)
        except:
            pass

    def setting_reset():  # Reset theme and username to default
        theme_var.set("System")
        username_var.set(True)
        settings_data["theme"] = "system"
        settings_data["show_username"] = True
        save_settings(settings_data)
        toggle_theme()
        toggle_username()
        apply_accent_color(DEFAULT_ACCENT_COLOR)

    def setting_close():
        setting_app.destroy()

    # --- Scrollable Theme Frame ---
    theme_frame = ctk.CTkScrollableFrame(
        setting_app, label_text="Theme", width=200, height=200
    )
    theme_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    theme_frame.grid_columnconfigure(0, weight=1)

    current_theme = settings_data.get("theme", "system").capitalize()
    theme_var = ctk.StringVar(value=current_theme)
    # Live update on change
    theme_var.trace_add("write", toggle_theme)

    def choose_accent_color():
        try:
            picker = AskColor(
                initial_color=accent_color,
                title="Choose Accent Color",
                button_color=accent_color,
                button_hover_color=accent_hover_color,
            )
            selected = picker.get()
            if selected:
                hex_val = selected
                apply_accent_color(hex_val)
                accent_entry.delete(0, "end")
                accent_entry.insert(0, hex_val)
        except Exception:
            pass

    theme_dropdown = ctk.CTkOptionMenu(
        theme_frame,
        values=["System", "Light", "Dark"],
        variable=theme_var,
        button_color=accent_color,
        button_hover_color=accent_hover_color,
    )
    theme_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    register_accent_optionmenu(theme_dropdown)

    def apply_entry_color():
        hex_val = accent_entry.get().strip()
        if not hex_val.startswith("#"):
            hex_val = "#" + hex_val
        if len(hex_val) == 7 and all(
            c in "0123456789abcdefABCDEF" for c in hex_val[1:]
        ):
            apply_accent_color(hex_val)
        else:
            messagebox.showerror(
                "Invalid color", "Please enter a valid hex color like #1f6aa5"
            )

    accent_entry = ctk.CTkEntry(theme_frame, placeholder_text="#1f6aa5")
    accent_entry.grid(row=2, column=0, padx=10, pady=(0, 6), sticky="ew")
    accent_entry.insert(0, accent_color)

    accent_apply_button = ctk.CTkButton(
        theme_frame,
        text="Set Hex Color",
        command=apply_entry_color,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    accent_apply_button.grid(row=3, column=0, padx=10, pady=2, sticky="ew")
    register_accent_button(accent_apply_button)

    accent_button = ctk.CTkButton(
        theme_frame,
        text="Pick Accent Color",
        command=choose_accent_color,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    accent_button.grid(row=4, column=0, padx=10, pady=2, sticky="ew")
    register_accent_button(accent_button)

    # --- Scrollable Options Frame ---
    options_frame = ctk.CTkScrollableFrame(
        setting_app, label_text="Options", width=200, height=200
    )
    options_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    options_frame.grid_columnconfigure(0, weight=1)

    username_var = ctk.BooleanVar(value=settings_data.get("show_username", True))
    username_checkbox = ctk.CTkCheckBox(
        options_frame,
        text="Show Username",
        variable=username_var,
        command=toggle_username,
        fg_color=accent_color,
        hover_color=accent_hover_color,
        checkmark_color=accent_color,
    )
    username_checkbox.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")
    register_accent_checkbox(username_checkbox)

    def show_app_version():
        messagebox.showinfo(
            "App Version", f"You currently have version {downloaded_version} installed."
        )

    version_button = ctk.CTkButton(
        options_frame,
        text="Show App Version",
        command=show_app_version,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    version_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
    register_accent_button(version_button)

    # --- Buttons ---
    save_button = ctk.CTkButton(
        setting_app,
        text="Save/Close",
        command=setting_close,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    save_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
    register_accent_button(save_button)

    reset_button = ctk.CTkButton(
        setting_app,
        text="Reset",
        command=setting_reset,
        fg_color=accent_color,
        hover_color=accent_hover_color,
    )
    reset_button.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
    register_accent_button(reset_button)

    setting_app.mainloop()


# ---- App Title ----
label = ctk.CTkLabel(app, text="Quick-CMD", fg_color="transparent", font=("Arial", 26))
label.grid(row=0, column=0, columnspan=3, pady=10)


# ---- App Frams ----
def get_frame_color():
    return "#e0e0e0" if ctk.get_appearance_mode() == "Light" else "#2a2a2a"


button_frame = ctk.CTkFrame(  # Frame for Shortcuts
    app, corner_radius=10, fg_color=get_frame_color(), border_width=1
)
button_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

file_frame = ctk.CTkFrame(  # Frame for Files
    app, corner_radius=10, fg_color=get_frame_color(), border_width=1
)
file_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

network_frame = ctk.CTkFrame(  # Frame for Network
    app, corner_radius=10, fg_color=get_frame_color(), border_width=1
)
network_frame.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

settings_frame = ctk.CTkFrame(  # Frame for Settings
    app, corner_radius=10, fg_color=get_frame_color(), border_width=1
)
settings_frame.grid(row=4, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

# ---- App Buttons ----
button_padx = 5
button_pady = 5

# App Buttons for Shortcuts
cmd_button = ctk.CTkButton(button_frame, text="Terminal", command=open_cmd)
cmd_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)
register_accent_button(cmd_button)

cmd_admin_button = ctk.CTkButton(
    button_frame, text="Terminal (Admin)", command=open_cmd_admin
)
cmd_admin_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)
register_accent_button(cmd_admin_button)

reg_button = ctk.CTkButton(button_frame, text="Registry", command=open_registry)
reg_button.grid(row=1, column=0, padx=button_padx, pady=button_pady)
register_accent_button(reg_button)

del_app_button = ctk.CTkButton(
    button_frame, text="Delete Apps", command=open_control_panel
)
del_app_button.grid(row=1, column=1, padx=button_padx, pady=button_pady)
register_accent_button(del_app_button)

devicemgr_button = ctk.CTkButton(
    button_frame, text="Device Manager", command=open_device_manager
)
devicemgr_button.grid(row=2, column=0, padx=button_padx, pady=button_pady)
register_accent_button(devicemgr_button)

taskmgr_button = ctk.CTkButton(
    button_frame, text="Task Manager", command=open_task_manager
)
taskmgr_button.grid(row=2, column=1, padx=button_padx, pady=button_pady)
register_accent_button(taskmgr_button)

# App Buttons for Files
del_temp_button = ctk.CTkButton(
    file_frame, text="Clear Temp Files", command=del_temp_files
)
del_temp_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)
register_accent_button(del_temp_button)

del_trash_button = ctk.CTkButton(
    file_frame, text="Clear Recycle Bin", command=del_trash_files
)
del_trash_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)
register_accent_button(del_trash_button)

disk_cleanup_button = ctk.CTkButton(
    file_frame, text="Disk Cleanup", command=disk_cleanup
)
disk_cleanup_button.grid(row=1, column=0, padx=button_padx, pady=button_pady)
register_accent_button(disk_cleanup_button)

clear_browser_cache_button = ctk.CTkButton(
    file_frame, text="Cear Browser cache", command=clear_browser_cache
)
clear_browser_cache_button.grid(row=1, column=1, padx=button_padx, pady=button_pady)
register_accent_button(clear_browser_cache_button)

# App Buttons for Network
show_ip_button = ctk.CTkButton(network_frame, text="Show IP", command=show_ip)
show_ip_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)
register_accent_button(show_ip_button)

speed_test_button = ctk.CTkButton(
    network_frame, text="Speed Test", command=internet_speedtest
)
speed_test_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)
register_accent_button(speed_test_button)

# App Buttons for Settings
exit_button = ctk.CTkButton(
    settings_frame,
    text="Exit",
    fg_color="#474747",
    hover_color="#373737",
    command=closing_app,
)
exit_button.grid(row=0, column=0, padx=button_padx, pady=button_pady)

settings_button = ctk.CTkButton(
    settings_frame,
    text="Settings",
    fg_color="#474747",
    hover_color="#373737",
    command=settings_menu,
)
settings_button.grid(row=0, column=1, padx=button_padx, pady=button_pady)

# apply accent color to existing widgets
apply_accent_color(accent_color, save=False)
update_special_buttons()

# ---- Dynamic Theme Polling System ----
current_mode = ctk.get_appearance_mode()


def poll_appearance_mode():
    global current_mode

    if not app.winfo_exists():
        return

    new_mode = ctk.get_appearance_mode()

    if new_mode != current_mode:
        current_mode = new_mode
        color = "#e0e0e0" if new_mode == "Light" else "#2a2a2a"

        try:
            button_frame.configure(fg_color=color)
            file_frame.configure(fg_color=color)
            network_frame.configure(fg_color=color)
            settings_frame.configure(fg_color=color)
        except:
            pass

        update_special_buttons()

    try:
        app.after(500, poll_appearance_mode)
    except RuntimeError:
        pass


poll_appearance_mode()

# Run App
app.mainloop()

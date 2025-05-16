import tkinter as tk
from tkinter import ttk, messagebox
from pypresence import Presence
import time
import pystray
from PIL import Image
import threading
import sys

class DiscordRPCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord RPC Manager")
        self.root.geometry("500x500")
        self.root.configure(bg="#36393F")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Initialize Discord RPC
        self.rpc = None
        self.connected = False
        self.tray_icon = None
        self.tray_thread = None

        # Last session data
        self.last_session = {
            "client_id": "",
            "details": "",
            "state": "",
            "large_image": "",
            "large_text": "",
            "small_image": "",
            "small_text": ""
        }

        # Styling
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Discord-inspired colors
        bg_color = "#36393F"
        entry_bg = "#40444B"
        button_bg = "#5865F2"
        button_hover = "#4752C4"
        text_color = "#FFFFFF"
        accent_color = "#5865F2"

        style.configure(".", 
                      background=bg_color, 
                      foreground=text_color, 
                      font=("Segoe UI", 10))
        
        style.configure("TLabel", 
                      background=bg_color, 
                      foreground=text_color,
                      font=("Segoe UI", 9))
        
        style.configure("TButton", 
                      background=button_bg,
                      foreground=text_color,
                      padding=8,
                      font=("Segoe UI", 9, "bold"),
                      borderwidth=0,
                      focuscolor=bg_color)
        
        style.map("TButton",
                background=[("active", button_hover), ("disabled", "#4E5058")],
                foreground=[("active", text_color)])
        
        style.configure("TEntry", 
                      fieldbackground=entry_bg,
                      foreground=text_color,
                      insertbackground=text_color,
                      borderwidth=1,
                      relief="flat",
                      padding=5,
                      font=("Segoe UI", 9))

        # Main frame
        main_frame = ttk.Frame(self.root, padding=(20, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.label = ttk.Label(header_frame, 
                            text="DISCORD RPC MANAGER", 
                            font=("Segoe UI", 14, "bold"),
                            foreground=accent_color)
        self.label.pack(side=tk.LEFT)

        # Form section
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Left column
        left_col = ttk.Frame(form_frame, padding=(0, 0, 10, 0))
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right column
        right_col = ttk.Frame(form_frame, padding=(10, 0, 0, 0))
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Form fields with last session values
        self.create_form_field(left_col, "Client ID:", "client_id_entry", self.last_session["client_id"])
        self.create_form_field(left_col, "Details:", "details_entry", self.last_session["details"])
        self.create_form_field(left_col, "State:", "state_entry", self.last_session["state"])
        
        self.create_form_field(right_col, "Large image (key):", "large_image_entry", self.last_session["large_image"])
        self.create_form_field(right_col, "Large image text:", "large_text_entry", self.last_session["large_text"])
        self.create_form_field(right_col, "Small image (key):", "small_image_entry", self.last_session["small_image"])
        self.create_form_field(right_col, "Small image text:", "small_text_entry", self.last_session["small_text"])

        # Action button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        self.activate_button = ttk.Button(button_frame, 
                                      text="ACTIVATE RPC", 
                                      command=self.activate_rpc)
        self.activate_button.pack(fill=tk.X)

        # Animations
        self.animate_header()
        self.setup_button_hover_effects()

    def create_form_field(self, parent, label_text, entry_name, default_value=""):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 12))
        
        label = ttk.Label(frame, text=label_text)
        label.pack(anchor=tk.W, pady=(0, 3))
        
        entry_var = tk.StringVar(value=default_value)
        entry = ttk.Entry(frame, textvariable=entry_var)
        entry.pack(fill=tk.X)
        setattr(self, entry_name, entry_var)

    def save_current_session(self):
        """Save current form values to memory"""
        self.last_session = {
            "client_id": self.client_id_entry.get(),
            "details": self.details_entry.get(),
            "state": self.state_entry.get(),
            "large_image": self.large_image_entry.get(),
            "large_text": self.large_text_entry.get(),
            "small_image": self.small_image_entry.get(),
            "small_text": self.small_text_entry.get()
        }

    def create_tray_icon(self):
        try:
            image = Image.new('RGB', (16, 16), color='#5865F2')
            menu = (
                pystray.MenuItem('Show', self.restore_from_tray),
                pystray.MenuItem('Exit', self.quit_app)
            )
            self.tray_icon = pystray.Icon("Discord RPC", image, "Discord RPC Manager", menu)
            self.tray_icon.run()
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            self.root.deiconify()

    def minimize_to_tray(self):
        self.save_current_session()
        self.root.withdraw()
        if not self.tray_thread or not self.tray_thread.is_alive():
            self.tray_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
            self.tray_thread.start()

    def restore_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.save_current_session()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.close)

    def animate_header(self):
        current_color = self.label.cget("foreground")
        new_color = "#FFFFFF" if current_color == "#5865F2" else "#5865F2"
        self.label.configure(foreground=new_color)
        self.root.after(1500, self.animate_header)

    def setup_button_hover_effects(self):
        self.activate_button.bind("<Enter>", lambda e: self.activate_button.state(['pressed']))
        self.activate_button.bind("<Leave>", lambda e: self.activate_button.state(['!pressed']))

    def connect_to_discord(self):
        client_id = self.client_id_entry.get()
        if not client_id:
            messagebox.showerror("Error", "Please enter Client ID!", parent=self.root)
            return False

        try:
            if not self.connected:
                self.rpc = Presence(client_id)
                self.rpc.connect()
                self.connected = True
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Discord: {e}", parent=self.root)
            return False

    def activate_rpc(self):
        if not self.connect_to_discord():
            return

        details = self.details_entry.get()
        state = self.state_entry.get()
        large_image = self.large_image_entry.get()
        large_text = self.large_text_entry.get()
        small_image = self.small_image_entry.get()
        small_text = self.small_text_entry.get()

        if not details or not state:
            messagebox.showerror("Error", "Please fill 'Details' and 'State' fields!", parent=self.root)
            return

        self.rpc.update(
            details=details,
            state=state,
            large_image=large_image if large_image else None,
            large_text=large_text if large_text else None,
            small_image=small_image if small_image else None,
            small_text=small_text if small_text else None
        )
        messagebox.showinfo("Success", "RPC has been activated!", parent=self.root)

    def close(self):
        if self.rpc:
            self.rpc.close()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordRPCApp(root)
    root.mainloop()

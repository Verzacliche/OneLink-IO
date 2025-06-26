import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import yt_dlp
import threading
from PIL import Image, ImageTk

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and PyInstaller."""
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_ffmpeg_path():
    """Returns the path to FFmpeg, checking if it's running in a bundled app or installed."""
    if getattr(sys, '_MEIPASS', False):
        return os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', 'ffmpeg.exe')
    else:
        ffmpeg_install_path = r"C:\Program Files (x86)\OneLink IO\ffmpeg\bin\ffmpeg.exe"
        if os.path.exists(ffmpeg_install_path):
            return ffmpeg_install_path
        else:
            return None  

def download_audio(link, folder, format_choice, organize_playlist):
    """Download audio and organize playlists if required."""
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'progress_hooks': [progress_hook]}) as ydl:
            info = ydl.extract_info(link, download=False)
            is_playlist = 'entries' in info
            playlist_title = info.get('title') if is_playlist else None

            # Filter out hidden or unavailable songs
            if is_playlist:
                entries = [
                    entry for entry in info['entries']
                    if entry and not entry.get('is_unavailable')
                ]
                if not entries:
                    messagebox.showinfo("Download Complete", "No downloadable songs in the playlist.")
                    return
                info['entries'] = entries
            else:
                if info.get('is_unavailable'):
                    messagebox.showinfo("Download Skipped", "The song is unavailable.")
                    return

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching link info: {e}")
        return

    # Get FFmpeg path for postprocessing
    ffmpeg_path = get_ffmpeg_path()

    # Set download options
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_choice,
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True
            },
        ],
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
    }

    if organize_playlist and is_playlist:
        folder_name = os.path.join(folder, playlist_title)
        os.makedirs(folder_name, exist_ok=True)
        ydl_opts['outtmpl'] = os.path.join(folder_name, '%(title)s.%(ext)s')
    elif not organize_playlist:
        ydl_opts['noplaylist'] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            messagebox.showinfo("Download Complete", f"Song/Playlist saved in {folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Error encountered during download: {e}")

def progress_hook(d):
    """Progress hook function to update progress in GUI."""
    if d['status'] == 'downloading':

        progress = f"Downloading: {d['downloaded_bytes'] / d['total_bytes'] * 100:.2f}%"
        progress_label.config(text=progress)


def browse_folder():
    folder = filedialog.askdirectory(title="Select Download Folder")
    if folder:
        download_path.set(folder)

def download_audio_thread(link, folder, format_choice, organize_playlist, progress_label):
    """This function will run in a separate thread to prevent the GUI from freezing."""
    try:
        download_audio(link, folder, format_choice, organize_playlist)
        progress_label.config(text="Download Complete!")
    except Exception as e:
        progress_label.config(text="Error during download")
        messagebox.showerror("Error", f"Error encountered during download: {e}")

def start_download():
    link = link_entry.get()
    folder = download_path.get()
    format_choice = "wav" if format_var.get() == 1 else "mp3" if format_var.get() == 2 else "flac"
    organize_playlist = organize_var.get() == 1

    if not link:
        messagebox.showwarning("Error", "Please enter a valid Spotify/Youtube Music link.")
        return
    if not folder:
        messagebox.showwarning("Error", "Please select a download folder.")
        return

    progress_label.config(text="Initializing download...")
    
    # Start the download in a separate thread
    threading.Thread(
        target=download_audio_thread,
        args=(link, folder, format_choice, organize_playlist, progress_label),
        daemon=True
    ).start()

def toggle_settings():
    if settings_frame.winfo_ismapped():
        settings_frame.place_forget()
        frame.place(relx=0.5, rely=0.5, anchor="center")
        settings_button.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
    else:
        frame.place_forget()
        settings_frame.place(relx=0.5, rely=0.5, anchor="center")

        settings_button.grid_forget()

def back_to_main():
    settings_frame.place_forget()
    frame.place(relx=0.5, rely=0.5, anchor="center")

    settings_button.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

    settings_frame.place_forget()
    frame.place(relx=0.5, rely=0.5, anchor="center")
    settings_button.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))


def update_bg(event):
    new_width = root.winfo_width()
    new_height = root.winfo_height()

    if new_width < 2 or new_height < 2:
        return  

    resized = bg_image.resize((new_width, new_height), Image.LANCZOS)
    new_img = ImageTk.PhotoImage(resized)

    bg_label.config(image=new_img)
    bg_label.image = new_img  # Prevent garbage collection


# Create GUI
root = tk.Tk()
root.title("OneLink IO")
root.geometry("1280x720")
style = ttk.Style()
style.configure("TButton",
    background="#89F07C",
    foreground="white",
    font=("Bahnschrift SemiLight", 12),
    padding=6)

style.configure("Custom.TEntry",
    padding=5,
    relief="flat",
    font=("Bahnschrift SemiLight", 10))

# Set custom icon
try:
    icon_path = resource_path("OneLinkIO.ico")
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Warning: Unable to load icon. {e}")

# Set background
bg_image_path = resource_path("OneLink IO BG.png")
try:
    bg_image = Image.open(bg_image_path)
except Exception as e:
    messagebox.showerror("Error", f"Failed to load background image: {e}")
    root.quit()

tk_bg_image = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=tk_bg_image)
bg_label.place(relwidth=1, relheight=1)


# Main Frame
style.configure("Modern.TFrame",
    background="white",
    relief="ridge",
    borderwidth=2)

frame = ttk.Frame(root, padding=30, style="Modern.TFrame")
frame.place(relx=0.5, rely=0.5, anchor="center")


# Link Entry
ttk.Label(frame, text="Enter Youtube & YT Music Links Here", style="Custom.TLabel") \
    .grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))


# Entry + Paste layout frame
entry_frame = tk.Frame(frame, bg="white", bd=0, highlightthickness=0)
entry_frame.grid(row=2, column=0, columnspan=2, pady=5)

# Entry widget
link_entry = ttk.Entry(entry_frame, width=44, style="Custom.TEntry", font=("Bahnschrift SemiLight", 10))
link_entry.pack(side=tk.LEFT, padx=(0, 6), ipady=4)


def paste_from_clipboard():
    try:
        link_entry.delete(0, tk.END)
        link_entry.insert(0, root.clipboard_get())
    except tk.TclError:
        pass 

# Paste button
paste_button = ttk.Button(entry_frame, text="Paste", command=paste_from_clipboard, style="Small.TButton")
paste_button.pack(side=tk.LEFT)

# Format 
format_var = tk.IntVar(value=1)

ttk.Label(frame, text="Select Audio Format", style="Custom.TLabel") \
    .grid(row=3, column=0, columnspan=2, sticky="n", pady=(10, 5))

format_frame = tk.Frame(frame, bg="white")
format_frame.grid(row=4, column=0, columnspan=2)

tk.Radiobutton(format_frame, text="WAV", variable=format_var, value=1,
               bg="white", font=("Bahnschrift SemiLight", 10)) \
    .pack(side=tk.LEFT, padx=5)

tk.Radiobutton(format_frame, text="MP3", variable=format_var, value=2,
               bg="white", font=("Bahnschrift SemiLight", 10)) \
    .pack(side=tk.LEFT, padx=5)

tk.Radiobutton(format_frame, text="FLAC", variable=format_var, value=3,
               bg="white", font=("Bahnschrift SemiLight", 10)) \
    .pack(side=tk.LEFT, padx=5)

# Settings Frame
settings_frame = ttk.Frame(root, padding=20, style="Modern.TFrame")


# Playlist Organization
organize_var = tk.IntVar(value=1)
tk.Checkbutton(settings_frame, text="Download Playlists as Folders", variable=organize_var, bg="white", font=("Bahnschrift SemiLight", 10)) \
    .grid(row=0, column=0, columnspan=2, pady=5)

# Download Path Entry
download_path = tk.StringVar()
tk.Label(settings_frame, text="Set your Download Folder", bg="white", font=("Bahnschrift SemiLight", 12)) \
    .grid(row=1, column=0, columnspan=2, sticky="n", pady=5)

path_entry = ttk.Entry(settings_frame, textvariable=download_path, width=40, style="Custom.TEntry", font=("Bahnschrift SemiLight", 10))
path_entry.grid(row=2, column=0, columnspan=2, pady=5, sticky="n")

browse_button = ttk.Button(settings_frame, text="Browse", command=browse_folder, style="Small.TButton")
browse_button.grid(row=3, column=0, columnspan=2, pady=5)

back_button = ttk.Button(settings_frame, text="Back", command=back_to_main, style="Small.TButton")
back_button.grid(row=4, column=0, columnspan=2, pady=5)

download_button = ttk.Button(frame, text="Convert & Download", command=start_download, style="TButton")
download_button.grid(row=6, column=0, columnspan=2, pady=10)

settings_button = ttk.Button(frame, text="Settings", command=toggle_settings, style="Settings.TButton")
settings_button.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))

# Credit Text
credit_label = tk.Label(root, text="OneLink IO © 2024 by Verzacliche", bg="white", fg="black", font=("Bahnschrift SemiLight", 10, "italic"))
credit_label.place(relx=0.5, rely=0.9, anchor="center")

# Progress Label
progress_label = tk.Label(frame, text="Ready to download", bg="white", font=("Bahnschrift SemiLight", 10))
progress_label.grid(row=7, column=0, columnspan=2, pady=(0, 5), sticky="n")

root.mainloop()
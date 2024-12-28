import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import yt_dlp
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
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            is_playlist = 'entries' in info
            playlist_title = info.get('title') if is_playlist else None
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching link info: {e}")
        return

    # Get FFmpeg path for postprocessing
    ffmpeg_path = get_ffmpeg_path()

    # Set download options
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'quiet': False,
        'ffmpeg_location': ffmpeg_path,  # Explicitly set the ffmpeg location here
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format_choice,
        }],
    }

    if organize_playlist:
        if is_playlist:
            # Create a folder for the playlist and organize downloaded files into that folder
            folder_name = os.path.join(folder, playlist_title)
            os.makedirs(folder_name, exist_ok=True)
            ydl_opts['outtmpl'] = os.path.join(folder_name, '%(title)s.%(ext)s')
        else:
            # If the link is not a playlist but organize_playlist is ON, download without creating subfolders
            ydl_opts['outtmpl'] = os.path.join(folder, '%(title)s.%(ext)s')
    else:
        # If organize_playlist is OFF, just download all audio to the main folder
        ydl_opts['noplaylist'] = True  # Ensures that no playlists are downloaded in this case
        ydl_opts['outtmpl'] = os.path.join(folder, '%(title)s.%(ext)s')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            messagebox.showinfo("Download Complete", f"Song/Playlist saved in {folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Error encountered during download: {e}")

def browse_folder():
    folder = filedialog.askdirectory(title="Select Download Folder")
    if folder:
        download_path.set(folder)

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
    download_audio(link, folder, format_choice, organize_playlist)

def toggle_settings():
    if settings_frame.winfo_ismapped():
        settings_frame.place_forget()
        frame.place(relx=0.5, rely=0.5, anchor="center")
        settings_button.place(x=10, y=10, anchor="nw")
    else:
        frame.place_forget()
        settings_frame.place(relx=0.5, rely=0.5, anchor="center")
        settings_button.place_forget()

def back_to_main():
    settings_frame.place_forget()
    frame.place(relx=0.5, rely=0.5, anchor="center")
    settings_button.place(x=10, y=10, anchor="nw")

def update_bg(event):
    new_width = root.winfo_width()
    new_height = root.winfo_height()
    resized_bg = bg_image.resize((new_width, new_height), Image.ANTIALIAS)
    tk_bg_image = ImageTk.PhotoImage(resized_bg)
    bg_label.config(image=tk_bg_image)
    bg_label.image = tk_bg_image

# Create GUI
root = tk.Tk()
root.title("OneLink IO")
root.geometry("1280x720")

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
root.bind("<Configure>", update_bg)


# Canvas for frame
canvas = tk.Canvas(root, width=550, height=400, bg="white", bd=0, highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor="center")

# Draw border lines
border_color = "#545454"
line_thickness = 2

# Top border
canvas.create_line(0, 0, 550, 0, fill=border_color, width=line_thickness)
# Left border
canvas.create_line(0, 0, 0, 400, fill=border_color, width=line_thickness)
# Right border
canvas.create_line(550, 0, 550, 400, fill=border_color, width=line_thickness)
# Bottom border
canvas.create_line(0, 400, 550, 400, fill=border_color, width=line_thickness)

# Draw corners (top-left, top-right, bottom-left, bottom-right)
corner_size = 15
canvas.create_line(0, 0, corner_size, 0, fill=border_color, width=line_thickness)
canvas.create_line(0, 0, 0, corner_size, fill=border_color, width=line_thickness)

canvas.create_line(550, 0, 550 - corner_size, 0, fill=border_color, width=line_thickness)
canvas.create_line(550, 0, 550, corner_size, fill=border_color, width=line_thickness)

canvas.create_line(0, 400, corner_size, 400, fill=border_color, width=line_thickness)
canvas.create_line(0, 400, 0, 400 - corner_size, fill=border_color, width=line_thickness)

canvas.create_line(550, 400, 550 - corner_size, 400, fill=border_color, width=line_thickness)
canvas.create_line(550, 400, 550, 400 - corner_size, fill=border_color, width=line_thickness)

# Frame for the form
frame = tk.Frame(canvas, bg="white", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Link Entry
tk.Label(frame, text="Enter Link", bg="white", font=("Arial", 12)) \
    .grid(row=0, column=0, columnspan=2, sticky="n", pady=5)

link_entry = tk.Entry(frame, width=40, font=("Arial", 10))
link_entry.grid(row=1, column=0, columnspan=2, pady=5, sticky="n")

# Format Choice
format_var = tk.IntVar(value=1)
tk.Label(frame, text="Select Audio Format", bg="white", font=("Arial", 12)) \
    .grid(row=2, column=0, columnspan=2, sticky="n", pady=5)

tk.Radiobutton(frame, text="WAV", variable=format_var, value=1, bg="white", font=("Arial", 10)) \
    .grid(row=3, column=0, sticky="e", padx=5)

tk.Radiobutton(frame, text="MP3", variable=format_var, value=2, bg="white", font=("Arial", 10)) \
    .grid(row=3, column=1, sticky="w", padx=5)

tk.Radiobutton(frame, text="FLAC", variable=format_var, value=3, bg="white", font=("Arial", 10)) \
    .grid(row=4, column=0, columnspan=2, sticky="n", pady=5)

settings_button = tk.Button(canvas, text="Settings", command=toggle_settings, bg="#545454", fg="white", font=("Arial", 10))
settings_button.place(x=10, y=10, anchor="nw")

# Settings Frame
settings_frame = tk.Frame(canvas, bg="white", padx=20, pady=20)

# Playlist Organization
organize_var = tk.IntVar(value=1)
tk.Checkbutton(settings_frame, text="Download playlists as folders", variable=organize_var, bg="white", font=("Arial", 10)) \
    .grid(row=0, column=0, columnspan=2, pady=5)

# Download Path Entry
download_path = tk.StringVar()
tk.Label(settings_frame, text="Set your Download Folder", bg="white", font=("Arial", 12)) \
    .grid(row=1, column=0, columnspan=2, sticky="n", pady=5)

path_entry = tk.Entry(settings_frame, textvariable=download_path, width=40, font=("Arial", 10))
path_entry.grid(row=2, column=0, columnspan=2, pady=5, sticky="n")

browse_button = tk.Button(settings_frame, text="Browse", command=browse_folder, bg="#545454", fg="white", font=("Arial", 10))
browse_button.grid(row=3, column=0, columnspan=2, pady=5)

back_button = tk.Button(settings_frame, text="Back", command=back_to_main, bg="#545454", fg="white", font=("Arial", 10))
back_button.grid(row=4, column=0, columnspan=2, pady=5)

download_button = tk.Button(frame, text="Download", command=start_download, bg="#545454", fg="white", font=("Arial", 12), width=20)
download_button.grid(row=5, column=0, columnspan=2, pady=15)

# Credit Text
credit_label = tk.Label(root, text="OneLink IO © 2024 by Verzacliche (Carlo Lugatiman)", bg="white", fg="black", font=("Arial", 10, "italic"))
credit_label.place(relx=0.5, rely=0.9, anchor="center")

root.mainloop()

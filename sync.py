import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, scrolledtext
import time
import threading
from pprint import pprint

from compare import compare_folders, copy_data

def browse_folder1():
    folder1_path.set(filedialog.askdirectory())

def browse_folder2():
    folder2_path.set(filedialog.askdirectory())

progress_bar = None
popup = None

def sync():
    folder1 = folder1_path.get()
    folder2 = folder2_path.get()

    if folder1 and folder2:
        if folder1 == folder2:
            message_label.config(text="Please select different source and destination folders.", fg="red")
        else:
            compare_thread_finished = threading.Event()
            compare_result = None

            def run_compare_folders():
                nonlocal compare_result
                compare_result = compare_folders(folder1, folder2)
                # Signal that the thread has finished
                compare_thread_finished.set()

            # Create a thread to run the compare_folders function
            compare_thread = threading.Thread(target=run_compare_folders)
            compare_thread.daemon = True
            compare_thread.start()

            # Display a message while the compare_folders function is running
            message_label.config(text="Calculating resources, please wait...", fg="blue")
            root.update_idletasks()

            # Wait for the thread to finish
            compare_thread_finished.wait()

            to_sync, formatted_response = compare_result
            # pprint(to_sync)
            popup = create_popup(to_sync, formatted_response)

            # Grab focus to the pop-up window and wait for it to be closed
            popup.grab_set()
            popup.wait_window(popup)

            # Re-enable the buttons
            browse_button1.config(state=tk.NORMAL)
            browse_button2.config(state=tk.NORMAL)
            sync_button.config(state=tk.NORMAL, text="Re-Sync")  
    else:
        message_label.config(text="Please select both folders before syncing.", fg="red")  # Change text color to red


def create_popup(to_sync, formatted_response):
    # Create a pop-up window for the note
    global popup
    popup = tk.Toplevel(root)
    popup.title("Review")

    # Create a frame for the scrollable text
    text_frame = tk.Frame(popup)
    text_frame.pack(fill=tk.BOTH, expand=True)

    # Create a scrolled text widget for the text
    text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=60, height=10)
    text_widget.insert(tk.INSERT, formatted_response)
    text_widget.pack(fill=tk.BOTH, expand=True)

    # Create a frame for the buttons
    button_frame = tk.Frame(popup)
    button_frame.pack(fill=tk.BOTH)

    continue_button = tk.Button(button_frame, text="Continue", bg="#4CAF50", command=lambda: start_syncing(to_sync))
    cancel_button = tk.Button(button_frame, text="Cancel", bg="red", command=cancel)

    continue_button.pack(side=tk.RIGHT, padx=10, pady=10)
    cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

    return popup


def start_syncing(to_sync):
    global progress_bar
    global popup

    popup.destroy()

    if len(to_sync) == 0:
        return

    browse_button1.config(state=tk.DISABLED)
    browse_button2.config(state=tk.DISABLED)
    sync_button.config(state=tk.DISABLED)

    if not progress_bar:
        # Create a progress bar
        progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
        progress_bar.pack(pady=5)
    else:
        # Reset the progress bar to 0 before starting the progress update
        progress_bar["value"] = 0
        root.update_idletasks()

    # print(to_sync)

    message_label.config(text="Synchronizer Working it's magic...", fg="green")
    root.update_idletasks()
    data_size = sum([sum([val[2] for val in value]) for key, value in to_sync.items() if key!="Error"])
    data_copied = 0
    for part_data_copied in copy_data(to_sync):
        time.sleep(0.1)
        data_copied += part_data_copied
        progress_bar["value"] = data_copied // data_size * 100 
        root.update_idletasks()  # Update the GUI
    progress_bar["value"] = 100 
    root.update_idletasks()

    message_label.config(text="Sync Complete.", fg="green")

def cancel():
    popup.destroy()
    

# Create the main application window
root = tk.Tk()
root.title("Synchronizer")
root.geometry("500x200")  # Set window size to 500x200 pixels

# Define a color palette
root.configure(bg="#f0f0f0")  # Background color
text_color = "#333"  # Text color
button_bg = "#007acc"  # Button background color (for Browse buttons)
button_fg = "#ffffff"  # Button text color
sync_button_color = "#4CAF50"  # Green color for the "Sync" button

# Variables to store folder paths
folder1_path = tk.StringVar()
folder2_path = tk.StringVar()

# Frame for Folder 1
frame1 = tk.Frame(root, bg=root["bg"])
frame1.pack(fill=tk.X, padx=20, pady=(20, 5))

label_folder1 = tk.Label(frame1, text="Folder 1:", bg=frame1["bg"], fg=text_color)
label_folder1.pack(side=tk.LEFT)
entry_folder1 = tk.Entry(frame1, textvariable=folder1_path)
entry_folder1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

browse_button1 = tk.Button(frame1, text="Browse", fg=button_fg, bg=button_bg, command=browse_folder1)
browse_button1.pack(side=tk.RIGHT)

# Frame for Folder 2
frame2 = tk.Frame(root, bg=root["bg"])
frame2.pack(fill=tk.X, padx=20, pady=5)

label_folder2 = tk.Label(frame2, text="Folder 2:", bg=frame2["bg"], fg=text_color)
label_folder2.pack(side=tk.LEFT)
entry_folder2 = tk.Entry(frame2, textvariable=folder2_path)
entry_folder2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

browse_button2 = tk.Button(frame2, text="Browse", fg=button_fg, bg=button_bg, command=browse_folder2)
browse_button2.pack(side=tk.RIGHT)

# Frame for the "Sync" button and message
frame3 = tk.Frame(root, bg=root["bg"])
frame3.pack(fill=tk.X, padx=20, pady=5)

message_label = tk.Label(frame3, text="", bg=frame3["bg"], font=("bold"))  # Change text color to red
message_label.pack(side=tk.LEFT, padx=(0, 10))

sync_button = tk.Button(frame3, text="Sync", bg=sync_button_color, width=10, command=sync)
sync_button.pack(side=tk.RIGHT, pady=20)  # Make "Sync" button the same size as "Browse" buttons

# Suggestions for further UI improvements:
# 1. Add labels or tooltips to provide more context for users.
# 2. Use icons or graphics to make the UI more visually appealing.
# 3. Implement error handling and feedback messages for a better user experience.
# 4. Consider using a different layout manager (e.g., `grid` or `pack`) for more complex UIs.
# 5. Include an option to customize synchronization settings.
# 6. Provide progress indicators for long-running processes.
# 7. Add keyboard shortcuts for common actions.
# 8. Implement a menu bar for additional functionality.

# Start the GUI application
root.mainloop()
import tkinter as tk
from tkinter import ttk
from scripts import audio_steganography, image_steganography, text_steganography, video_steganography

# Function to create the main GUI window
def create_main_window():
    global root
    root = tk.Tk()
    root.title("Steganography Tool")

    # Calculate the position to center the window
    window_width = 1000
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Add a title label
    title_label = tk.Label(root, text="Steganography Tool", font=("Helvetica", 24), bg="#f0f0f0")
    title_label.pack(pady=10)

    # Frame for buttons
    btn_frame = tk.Frame(root, bg="#f0f0f0")
    btn_frame.pack(pady=20)

    # Add buttons with improved styling
    btn_image = ttk.Button(btn_frame, text="Image Steganography", command=lambda:image_steganography.img_steg(root), style="Custom.TButton")
    btn_image.grid(row=0, column=0, padx=10, pady=5)

    btn_text = ttk.Button(btn_frame, text="Text Steganography", command=lambda:text_steganography.txt_steg(root), style="Custom.TButton")
    btn_text.grid(row=0, column=2, padx=10, pady=5)

    btn_audio = ttk.Button(btn_frame, text="Audio Steganography", command=lambda:audio_steganography.aud_steg(root), style="Custom.TButton")
    btn_audio.grid(row=0, column=3, padx=10, pady=5)

    btn_audio = ttk.Button(btn_frame, text="Video Steganography", command=lambda:video_steganography.video_steg(root), style="Custom.TButton")
    btn_audio.grid(row=0, column=4, padx=10, pady=5)

    btn_exit = ttk.Button(root, text="Exit", command=root.quit, style="Custom.TButton")
    btn_exit.pack(pady=10)

    # Custom style for buttons
    style = ttk.Style()
    style.configure("Custom.TButton", foreground="black", background="#007bff", font=("Helvetica", 12), width=17)

    root.mainloop()

# Main function to create the GUI and run the application
def main():
    create_main_window()


if __name__ == "__main__":
    main()

import os
from tkinter import filedialog, simpledialog, messagebox, Toplevel, Text, Scrollbar, Label, ttk
from scripts import common
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Function to encode text data
def encode_txt_data(root, file_path, data):
    payload = common.read_message_from_file()
    if not payload:
        messagebox.showerror("Error", "Data entered to be encoded is empty")
        return

    # Check if the payload text is too large to be encoded
    if len(payload) * 2 > len(data):
        messagebox.showerror("Error", "Payload text is too large to be encoded in the cover text")
        return

    filename = simpledialog.askstring("Input", "Enter the filename to save (without extension):")
    if not filename:
        messagebox.showerror("Error", "No file name provided")
        return
    original_directory = os.path.dirname(file_path)
    nameoffile = os.path.join(original_directory, filename + '.txt')

    # Convert the payload to binary
    binary_payload = ''.join(format(ord(c), '08b') for c in payload)

    # Insert zero-width spaces into the cover text to represent the binary payload
    hidden_data = ""
    zero_width_chars = ["\u200B", "\u200C", "\u200D", "\uFEFF"]
    for i in range(0, len(binary_payload), 2):
    # Check if the index is within the valid range of the data string
        if i // 2 < len(data):
            hidden_data += data[i // 2] + zero_width_chars[int(binary_payload[i:i+2], 2)]
        else:
            hidden_data += zero_width_chars[int(binary_payload[i:i+2], 2)]
    # Append any remaining characters from data
    hidden_data += data[len(hidden_data) // 2:]

    with open(nameoffile, 'w', encoding='utf-8') as file:
        file.write(hidden_data)
    messagebox.showinfo("Success", f"Encoded the data successfully in the text file and the file is saved as {nameoffile}")
    show_comparison_page(root, file_path, nameoffile)


# Function to decode text data
def decode_txt_data(data):
    # Extract the binary payload from the zero-width spaces
    binary_payload = ""
    zero_width_chars = ["\u200B", "\u200C", "\u200D", "\uFEFF"]
    for c in data:
        if c in zero_width_chars:
            binary_payload
            binary_payload += format(zero_width_chars.index(c), '02b')

    # Convert the binary payload to text
    decoded_data = ""
    for i in range(0, len(binary_payload), 8):
        byte = binary_payload[i:i+8]
        decoded_data += chr(int(byte, 2))

    if decoded_data:
        print(decoded_data)
        # Create a new Tkinter window
        window = tk.Toplevel()
        window.title("Decoded Data")

        # Create a scrolled text area to display the decoded data
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
        text_area.insert(tk.END, decoded_data)
        text_area.configure(state='disabled')
        text_area.pack(expand=True, fill='both')
    else:
        messagebox.showerror("Error", "No hidden data found")

# Function to handle text steganography operations
def txt_steg(root):
    operation = simpledialog.askinteger("Input", "Enter the Choice: 1- Encode, 2- Decode" , parent=root)
    if operation == 1:
        messagebox.showinfo("Info", "Please select the text file to be encoded.")
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return
        with open(file_path, 'r') as file:
            data = file.read()
            encode_txt_data(root, file_path, data)
    elif operation == 2:
        messagebox.showinfo("Info", "Please select the text file to be decoded.")
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            decode_txt_data(data)
    elif operation == 3:
        return
    else:
        messagebox.showerror("Error", "Incorrect Choice")


def show_comparison_page(root, original_path, encoded_path):
    comp_window = Toplevel(root)
    comp_window.title("Text Comparison")

    # Read the original text file
    try:
        with open(original_path, 'r', encoding='utf-8') as file:
            original_text = file.read()
        print(f"Original Text:\n{original_text}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the original file: {e}")
        return

    # Read the encoded text file
    try:
        with open(encoded_path, 'r', encoding='utf-8') as file:
            encoded_text = file.read()

        # Create a version of encoded_text with placeholders
        zero_width_chars = ["\u200B", "\u200C", "\u200D", "\uFEFF"]
        placeholders = ["<sp>", "<nj>", "<wj>", "<bom>"]
        visible_encoded_text = encoded_text
        for zwc, ph in zip(zero_width_chars, placeholders):
            visible_encoded_text = visible_encoded_text.replace(zwc, ph)
        print(f"Encoded Text with placeholders:\n{visible_encoded_text}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the encoded file: {e}")
        return

    # Create the labels for each section
    original_label = Label(comp_window, text="Original Text")
    original_label.grid(row=0, column=0, padx=10, pady=10)
    encoded_label = Label(comp_window, text="Encoded Text (Invisible Zero-Width Characters)")
    encoded_label.grid(row=0, column=1, padx=10, pady=10)
    visible_encoded_label = Label(comp_window, text="Encoded Text (Visible Zero-Width Characters)")
    visible_encoded_label.grid(row=0, column=2, padx=10, pady=10)

    # Create text widgets for each section
    original_text_widget = Text(comp_window, wrap='word', width=40, height=25)
    original_text_widget.insert('1.0', original_text)
    original_text_widget.configure(state='disabled')
    original_text_widget.grid(row=1, column=0, padx=10, pady=10)

    encoded_text_widget = Text(comp_window, wrap='word', width=40, height=25)
    encoded_text_widget.insert('1.0', encoded_text)
    encoded_text_widget.configure(state='disabled')
    encoded_text_widget.grid(row=1, column=1, padx=10, pady=10)

    visible_encoded_text_widget = Text(comp_window, wrap='word', width=40, height=25)
    visible_encoded_text_widget.insert('1.0', visible_encoded_text)
    visible_encoded_text_widget.configure(state='disabled')
    visible_encoded_text_widget.grid(row=1, column=2, padx=10, pady=10)

    # Add scrollbars for each text widget
    original_scrollbar = Scrollbar(comp_window, command=original_text_widget.yview)
    original_text_widget.config(yscrollcommand=original_scrollbar.set)
    original_scrollbar.grid(row=1, column=0, sticky='nse', padx=(0, 10))

    encoded_scrollbar = Scrollbar(comp_window, command=encoded_text_widget.yview)
    encoded_text_widget.config(yscrollcommand=encoded_scrollbar.set)
    encoded_scrollbar.grid(row=1, column=1, sticky='nse', padx=(0, 10))

    visible_encoded_scrollbar = Scrollbar(comp_window, command=visible_encoded_text_widget.yview)
    visible_encoded_text_widget.config(yscrollcommand=visible_encoded_scrollbar.set)
    visible_encoded_scrollbar.grid(row=1, column=2, sticky='nse', padx=(0, 10))

     # Add "Back to Menu" button
    back_button = ttk.Button(comp_window, text="Back to Menu", command=comp_window.destroy, style="Custom.TButton")
    back_button.grid(row=2, column=0, columnspan=3, pady=20)


    # Configure row and column weights for proper resizing
    comp_window.grid_rowconfigure(1, weight=1)
    comp_window.grid_columnconfigure(0, weight=1)
    comp_window.grid_columnconfigure(1, weight=1)
    comp_window.grid_columnconfigure(2, weight=1)

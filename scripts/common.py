from tkinter import filedialog, messagebox

# Function to read message from a text file
def read_message_from_file():
    messagebox.showinfo("Info", "Please select the text payload file.")
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not file_path:
        messagebox.showerror("Error", "No file selected")
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    return data

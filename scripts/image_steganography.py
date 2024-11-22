import cv2
import numpy as np
import os
from tkinter import filedialog, simpledialog, messagebox, Toplevel, Label, Button
from PIL import Image, ImageTk
from scripts import common

# Function to convert a message to binary
def msg_to_binary(msg, num_bits=8):
    if isinstance(msg, str):
        result = ''.join([format(ord(i), f"0{num_bits}b") for i in msg])
    elif isinstance(msg, bytes) or isinstance(msg, np.ndarray):
        result = [format(i, f"0{num_bits}b") for i in msg]
    elif isinstance(msg, int) or isinstance(msg, np.uint8):
        result = format(msg, f"0{num_bits}b")
    else:
        raise TypeError("Input type is not supported in this function")
    return result

# Function to encode image data
def encode_img_data(root, img, num_lsb, original_file_path):
    # get payload file
    messagebox.showinfo("Information", "Please select the payload file. Can support png, jpg, txt, pdf, docx, mp4.")
    payload_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    if not payload_path:
        messagebox.showerror("Error", "No payload file selected")
        return
    
    # Read payload data
    with open(payload_path, 'rb') as payload_file:
        payload_data = payload_file.read()

    # checking if there is enough bytes to store payload
    no_of_bytes = (img.shape[0] * img.shape[1] * 3) // (8 // num_lsb)
    if len(payload_data) > no_of_bytes:
        messagebox.showerror("Error", "Insufficient bytes Error, Need Bigger Image or give Less Data!")
        return        
    
    # selecting file name to save encoded image
    filename = simpledialog.askstring("Input", "Enter the filename to save (without extension):", parent=root)
    if not filename:
        messagebox.showerror("Error", "No file name provided")
        return
    nameoffile = os.path.join(os.getcwd(), filename + '.png')
    
    # Get file extension and prepare the header
    file_extension = os.path.splitext(payload_path)[1]
    if not file_extension:
        messagebox.showerror("Error", "File extension not found")
        return

    # Adding payload header into payload data
    header = file_extension.ljust(8, ' ').encode('utf-8')  # 8-byte header for file extension
    payload_data = header + payload_data

    payload_data += b'*^*^*'
    binary_data = ''.join(format(byte, '08b') for byte in payload_data)
    data_length = len(binary_data)

    #code block: pixel distrbutiom 
    key = simpledialog.askinteger("Input", "Enter random distributrion key: ", parent=root)
    np.random.seed(key)
    indices = np.random.permutation(img.shape[0] * img.shape[1])

    index_data = 0

    for idx in indices:
        if index_data >= data_length:
            break
        i, j = divmod(idx, img.shape[1])
        pixel = img[i, j]
        r, g, b = msg_to_binary(pixel)
        if index_data < data_length:
            img[i, j, 0] = int(r[:-num_lsb] + binary_data[index_data:index_data+num_lsb], 2)
            index_data += num_lsb
        if index_data < data_length:
            img[i, j, 1] = int(g[:-num_lsb] + binary_data[index_data:index_data+num_lsb], 2)
            index_data += num_lsb
        if index_data < data_length:
            img[i, j, 2] = int(b[:-num_lsb] + binary_data[index_data:index_data+num_lsb], 2)
            index_data += num_lsb

    cv2.imwrite(nameoffile, img)
    messagebox.showinfo("Success", f"Encoded the data successfully in the image and the image is saved as {nameoffile}")

    # Show the comparison page
    show_comparison_page(root, original_file_path, nameoffile)

# Function to decode image data
def decode_img_data(img, num_lsb):

    #code block: pixel distrbutiom 
    key = simpledialog.askinteger("Input", "Enter random distributrion key: ", parent=None)
    np.random.seed(key)
    indices = np.random.permutation(img.shape[0] * img.shape[1])
    
    data_binary = ""
    decoded_data = ""

    try:    
        print(len(indices))
        for idx in indices:
            i, j = divmod(idx, img.shape[1])
            pixel = img[i, j]
            r, g, b = msg_to_binary(pixel)
            data_binary += r[-num_lsb:]
            data_binary += g[-num_lsb:]
            data_binary += b[-num_lsb:]
            if len(data_binary) % 8 == 0:
                total_bytes = [data_binary[k: k+8] for k in range(0, len(data_binary), 8)]
                decoded_data = bytearray()
                for byte in total_bytes:
                    decoded_data.append(int(byte, 2))
                    if decoded_data[-5:] == b'*^*^*':
                        print("hit")
                        decoded_data = decoded_data[:-5]  # Remove delimiter
                        # messagebox.showinfo("Decoded Data", f"The Encoded data hidden in the image is: {decoded_data}")
                        # return
                        # Extract file extension from the header
                        header = decoded_data[:8].decode('utf-8').strip()
                        payload_data = decoded_data[8:]
                        print(header)
                        # Prompt for output file name and save the decoded data
                        messagebox.showinfo("Information", "Please input the output file name to save the decoded data.")
                        output_path = filedialog.asksaveasfilename(defaultextension=header, filetypes=[("All files", "*.*")])
                        if output_path:
                            with open(output_path, 'wb') as output_file:
                                output_file.write(payload_data)
                            messagebox.showinfo("Success", f"The encoded data has been saved as {output_path}")
                            return

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while decoding the data: {e}")
# Function to handle image steganography operations
def img_steg(root):
    operation = simpledialog.askinteger("Input", "Enter the Choice: 1- Encode, 2- Decode", parent=root)
    if operation in (1, 2):
        num_lsb = simpledialog.askinteger("Input", "Enter the number of LSBs to use (1-8):", minvalue=1, maxvalue=8, parent=root)
        if not num_lsb:
            messagebox.showerror("Error", "No number of LSBs provided")
            return

    if operation == 1:
        messagebox.showinfo("Info", "Please select the image file to be encoded.")
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return
        image = cv2.imread(file_path)
        encode_img_data(root, image, num_lsb, file_path)
    elif operation == 2:
        messagebox.showinfo("Info", "Please select the image file to be decoded.")
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return
        image = cv2.imread(file_path)
        decode_img_data(image, num_lsb)
    elif operation == 3:
        return
    else:
        messagebox.showerror("Error", "Incorrect Choice")

# Function to show the comparison page
def show_comparison_page(root, original_file_path, encoded_file_path):
    comp_window = Toplevel(root)
    comp_window.title("Image Comparison")

    original_img = Image.open(original_file_path)
    encoded_img = Image.open(encoded_file_path)

    original_img = original_img.resize((500, 500))
    encoded_img = encoded_img.resize((500, 500))

    original_img_tk = ImageTk.PhotoImage(original_img)
    encoded_img_tk = ImageTk.PhotoImage(encoded_img)

    original_label = Label(comp_window, text="Original Image")
    original_label.grid(row=0, column=0, padx=10, pady=10)
    encoded_label = Label(comp_window, text="Encoded Image")
    encoded_label.grid(row=0, column=1, padx=10, pady=10)

    original_img_label = Label(comp_window, image=original_img_tk)
    original_img_label.image = original_img_tk
    original_img_label.grid(row=1, column=0, padx=10, pady=10)

    encoded_img_label = Label(comp_window, image=encoded_img_tk)
    encoded_img_label.image = encoded_img_tk
    encoded_img_label.grid(row=1, column=1, padx=10, pady=10)

    # Add a Back to Menu button
    back_button = Button(comp_window, text="Back to Menu", command=comp_window.destroy)
    back_button.grid(row=2, column=0, columnspan=2, pady=10)


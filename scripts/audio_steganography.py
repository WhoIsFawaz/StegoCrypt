import wave
import os
from tkinter import filedialog, simpledialog, messagebox, Toplevel, Label, Button
import pygame

# Function to encode data into audio
def encode_audio_data(root, audio_path, payload_path, output_path, key):
    key -= 1  # Convert to 0-based index
    
    # Read audio file
    audio = wave.open(audio_path, 'rb')
    params = audio.getparams()
    audio_data = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    # Read payload data
    with open(payload_path, 'rb') as payload_file:
        payload_data = payload_file.read()

    # Get file extension and prepare the header
    file_extension = os.path.splitext(payload_path)[1]
    if not file_extension:
        messagebox.showerror("Error", "File extension not found")
        return

    header = file_extension.ljust(8, ' ').encode('utf-8')  # 8-byte header for file extension
    payload_data = header + payload_data

    # Add a delimiter to signify end of data
    payload_data += b'*^*^*'
    binary_data = ''.join(format(byte, '08b') for byte in payload_data)
    data_length = len(binary_data)

    # Check if the payload is too large to be encoded
    available_space = len(audio_data)  # 1 byte per byte
    if len(binary_data) > available_space:
        messagebox.showerror("Error", "Payload is too large to be encoded in the audio")
        return

    # Encode data into audio
    for i in range(data_length):
        audio_data[i] = (audio_data[i] & (0xFF ^ (1 << key))) | ((int(binary_data[i], 2) << key) & (1 << key))  # Use LSB method

    # Write the encoded audio data to a new file
    encoded_audio = wave.open(output_path, 'wb')
    encoded_audio.setparams(params)
    encoded_audio.writeframes(bytes(audio_data))
    encoded_audio.close()

    # Notify success
    messagebox.showinfo("Success", f"Data encoded successfully in audio and saved as {output_path}")
    show_comparison_page(root, audio_path, output_path)

# Function to decode data from audio
def decode_audio_data(audio_path, key):
    key -= 1  # Convert to 0-based index
    
    # Read encoded audio file
    audio = wave.open(audio_path, 'rb')
    audio_data = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    # Extract binary data
    binary_data = ''.join(str((byte >> key) & 1) for byte in audio_data)  # Use LSB method

    # Split binary data into bytes
    bytes_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = bytearray()

    for byte in bytes_data:
        decoded_data.append(int(byte, 2))
        if decoded_data[-5:] == b'*^*^*':
            decoded_data = decoded_data[:-5]  # Remove delimiter
            break

    # Extract file extension from the header
    header = decoded_data[:8].decode('utf-8').strip()
    payload_data = decoded_data[8:]

    # Prompt for output file name and save the decoded data
    messagebox.showinfo("Information", "Please input the output file name to save the decoded data.")
    output_path = filedialog.asksaveasfilename(defaultextension=header, filetypes=[("All files", "*.*")])
    if output_path:
        with open(output_path, 'wb') as output_file:
            output_file.write(payload_data)
        messagebox.showinfo("Success", f"The encoded data has been saved as {output_path}")
    else:
        messagebox.showerror("Error", "No output file selected")

# Function to handle audio steganography operations
def aud_steg(root):
    # Prompt user for operation choice
    operation = simpledialog.askinteger("Input", "Enter the Choice: 1- Encode, 2- Decode", parent=root)
    if operation in (1, 2):
        key = simpledialog.askinteger("Input", "Enter the number of LSBs to use (1-8):", minvalue=1, maxvalue=8, parent=root)
        if not key:
            messagebox.showerror("Error", "No key provided")
            return
        messagebox.showinfo("Information", "Please select the audio file for encoding / to decode data from.")
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return

    if operation == 1:
        # Prompt for payload file selection
        messagebox.showinfo("Information", "Please select the payload file.")
        payload_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if not payload_path:
            messagebox.showerror("Error", "No payload file selected")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Audio files", "*.wav")])
        if not output_path:
            messagebox.showerror("Error", "No output file selected")
            return
        encode_audio_data(root, file_path, payload_path, output_path, key)
    elif operation == 2:
        # Decode data from audio
        decode_audio_data(file_path, key)
    else:
        messagebox.showerror("Error", "Incorrect Choice")

def show_comparison_page(root, original_path, encoded_path):
    comp_window = Toplevel(root)
    comp_window.title("Audio Comparison")

    # Get basic info about the original and encoded audio files
    original_size = os.path.getsize(original_path)
    encoded_size = os.path.getsize(encoded_path)

    original_info = wave.open(original_path, 'rb').getparams()
    encoded_info = wave.open(encoded_path, 'rb').getparams()

    # Create labels to display file info
    original_label = Label(comp_window, text=f"Original Audio\nSize: {original_size} bytes\nParams: {original_info}")
    original_label.grid(row=0, column=0, padx=10, pady=10)
    encoded_label = Label(comp_window, text=f"Encoded Audio\nSize: {encoded_size} bytes\nParams: {encoded_info}")
    encoded_label.grid(row=0, column=1, padx=10, pady=10)

    # Add buttons to play the audio files
    play_original_button = Button(comp_window, text="Play Original", command=lambda: play_audio(original_path))
    play_original_button.grid(row=1, column=0, padx=10, pady=10)

    play_encoded_button = Button(comp_window, text="Play Encoded", command=lambda: play_audio(encoded_path))
    play_encoded_button.grid(row=1, column=1, padx=10, pady=10)

    # Add a Back to Menu button
    back_button = Button(comp_window, text="Back to Menu", command=comp_window.destroy)
    back_button.grid(row=2, column=0, columnspan=2, pady=10)

def play_audio(file_path):
    # Ensure the file exists
    if not os.path.isfile(file_path):
        messagebox.showerror("Error", f"The file {file_path} does not exist.")
        return

    # Initialize pygame mixer
    pygame.mixer.init()

    try:
        # Load and play the audio file
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to play the audio file: {e}")

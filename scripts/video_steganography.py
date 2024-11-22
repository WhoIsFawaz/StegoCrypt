import cv2
import threading
import os
from tkinter import filedialog, simpledialog, messagebox, Tk, Toplevel, Label, Button
from scripts import common

# Global variable to track if the video is playing
is_video_playing = False

# Function to encode data into video with variable LSB
def encode_video_data(video_path, payload_path, output_path, num_lsb, root):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open video file")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

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
    available_space = num_frames * frame_width * frame_height * 3 * num_lsb
    if data_length > available_space:
        messagebox.showerror("Error", "Payload is too large to be encoded in the video")
        return

    # Create a directory to save frames
    output_dir = os.path.splitext(output_path)[0]
    os.makedirs(output_dir, exist_ok=True)

    # Encode data into frames
    index = 0
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame for encoding
        for i in range(frame_height):
            for j in range(frame_width):
                pixel = list(frame[i, j])
                for k in range(3):  # Process B, G, R channels
                    if index < data_length:
                        pixel[k] = (pixel[k] & ~(2 ** num_lsb - 1)) | int(binary_data[index:index + num_lsb], 2)
                        index += num_lsb
                    frame[i, j] = tuple(pixel)

                if index >= data_length:
                    break
            if index >= data_length:
                break

        # Save frame as an image
        frame_path = os.path.join(output_dir, f'frame_{frame_count}.png')
        cv2.imwrite(frame_path, frame)

        frame_count += 1

    cap.release()

    if frame_count == 0:
        messagebox.showerror("Error", "No frames found in the video")
        return

    # Write the encoded frames back to video
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    for i in range(frame_count):
        frame_path = os.path.join(output_dir, f'frame_{i}.png')
        frame = cv2.imread(frame_path)
        if frame is not None:
            out.write(frame)
        else:
            print(f"Frame {frame_path} does not exist.")
    out.release()

    # Notify success
    messagebox.showinfo("Success", f"Data encoded successfully in video and saved as {output_path}")
    show_comparison_page(root, video_path, output_path)

# Function to extract binary data from a single frame
def extract_data_from_frame(frame, num_lsb):
    frame_height, frame_width, _ = frame.shape
    binary_data = ''

    for i in range(frame_height):
        for j in range(frame_width):
            pixel = frame[i, j]
            for k in range(3):  # Process B, G, R channels
                binary_data += format(pixel[k], '08b')[-num_lsb:]

    return binary_data

# Function to decode data from video with variable LSB
def decode_video_data(video_path, num_lsb):
    binary_data = ''

    frame_dir = os.path.splitext(video_path)[0]
    if not os.path.exists(frame_dir):
        messagebox.showerror("Error", "No frames directory found")
        return

    frame_files = sorted(os.listdir(frame_dir))

    try:
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            binary_data += extract_data_from_frame(frame, num_lsb)

            print(f"Processed frame: {frame_file}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while decoding the data: {e}")
        return

    # Split binary data into bytes
    try:
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
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while decoding the data: {e}")

# Function to play video using OpenCV in a separate thread
def play_video(file_path):
    global is_video_playing

    if not os.path.isfile(file_path):
        messagebox.showerror("Error", f"The file {file_path} does not exist.")
        return

    def play():
        global is_video_playing
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open video file")
            return

        is_video_playing = True
        while is_video_playing:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Video Playback', frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=play).start()

# Function to show comparison page with video playback buttons
def show_comparison_page(root, original_path, encoded_path):
    comp_window = Toplevel(root)
    comp_window.title("Video Comparison")

    original_size = os.path.getsize(original_path)
    encoded_size = os.path.getsize(encoded_path)

    original_label = Label(comp_window, text=f"Original Video\nSize: {original_size} bytes")
    original_label.grid(row=0, column=0, padx=10, pady=10)
    encoded_label = Label(comp_window, text=f"Encoded Video\nSize: {encoded_size} bytes")
    encoded_label.grid(row=0, column=1, padx=10, pady=10)

    play_original_button = Button(comp_window, text="Play Original", command=lambda: play_video(original_path))
    play_original_button.grid(row=1, column=0, padx=10, pady=10)

    play_encoded_button = Button(comp_window, text="Play Encoded", command=lambda: play_video(encoded_path))
    play_encoded_button.grid(row=1, column=1, padx=10, pady=10)

    back_button = Button(comp_window, text="Back to Menu", command=comp_window.destroy)
    back_button.grid(row=3, column=0, columnspan=2, pady=10)

# Function to handle video steganography operations
def video_steg(root):
    # Prompt user for operation choice
    operation = simpledialog.askinteger("Input", "Enter the Choice: 1- Encode, 2- Decode", parent=root)
    if operation in (1, 2):
        messagebox.showinfo("Information", "Please select the video file for encoding / to decode data from.")
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return
        num_lsb = simpledialog.askinteger("Input", "Enter the number of LSBs to use (1-8):", minvalue=1, maxvalue=8, parent=root)
        if not num_lsb:
            messagebox.showerror("Error", "No number of LSBs provided")
            return

    if operation == 1:
        # Prompt for payload file selection
        messagebox.showinfo("Information", "Please select the payload file. Can support png, jpg, txt, pdf, docx, mp4.")
        payload_path = filedialog.askopenfilename(filetypes=[("Supported files", "*.png;*.jpg;*.txt;*.pdf;*.docx;*.mp4")])

        if not payload_path:
            messagebox.showerror("Error", "No payload file selected")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Video files", "*.mp4")])
        if not output_path:
            messagebox.showerror("Error", "No output file selected")
            return
        encode_video_data(file_path, payload_path, output_path, num_lsb, root) 
    elif operation == 2:
        # Decode data from video
        decode_video_data(file_path, num_lsb)
    elif operation == 3:
        return
    else:
        messagebox.showerror("Error", "Incorrect Choice")

# Main function to run the application
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  
    video_steg(root)

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image
import numpy as np
import soundfile as sf
import os

# --- Image Steganography Functions ---
def hide_text_in_image(image_path, text, output_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    data = np.array(img)
    flat_data = data.flatten()
    
    # Convert text to binary
    binary_text = ''.join([format(ord(c), '08b') for c in text])
    binary_text += '1111111111111110'  # EOF marker
    
    if len(binary_text) > len(flat_data):
        raise ValueError('Text is too long to hide in this image.')
    
    for i in range(len(binary_text)):
        flat_data[i] = (flat_data[i] & 0xFE) | int(binary_text[i])
    
    new_data = flat_data.reshape(data.shape)
    new_img = Image.fromarray(new_data.astype('uint8'), 'RGB')
    new_img.save(output_path)

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    data = np.array(img)
    flat_data = data.flatten()
    bits = []
    for i in range(len(flat_data)):
        bits.append(str(flat_data[i] & 1))
    
    chars = []
    for i in range(0, len(bits), 8):
        byte = ''.join(bits[i:i+8])
        if byte == '11111111':
            # Check for EOF marker
            if ''.join(bits[i:i+16]) == '1111111111111110':
                break
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

# --- Audio Steganography Functions ---
def hide_text_in_audio(audio_path, text, output_path):
    data, samplerate = sf.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]  # Use only one channel
    data = np.array(data * 32767, dtype=np.int16)
    
    binary_text = ''.join([format(ord(c), '08b') for c in text])
    binary_text += '1111111111111110'  # EOF marker
    
    if len(binary_text) > len(data):
        raise ValueError('Text is too long to hide in this audio file.')
    
    for i in range(len(binary_text)):
        data[i] = (data[i] & ~1) | int(binary_text[i])
    
    data = data.astype(np.int16)
    sf.write(output_path, data / 32767.0, samplerate)

def extract_text_from_audio(audio_path):
    data, samplerate = sf.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]
    data = np.array(data * 32767, dtype=np.int16)
    bits = []
    for i in range(len(data)):
        bits.append(str(data[i] & 1))
    chars = []
    for i in range(0, len(bits), 8):
        byte = ''.join(bits[i:i+8])
        if byte == '11111111':
            if ''.join(bits[i:i+16]) == '1111111111111110':
                break
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

# --- GUI ---
class StegApp:
    def __init__(self, root):
        self.root = root
        root.title('Steganography Tool')
        root.geometry('400x300')
        
        self.mode = tk.StringVar(value='Image')
        tk.Label(root, text='Steganography Tool', font=('Arial', 16)).pack(pady=10)
        
        tk.Radiobutton(root, text='Image', variable=self.mode, value='Image').pack()
        tk.Radiobutton(root, text='Audio', variable=self.mode, value='Audio').pack()
        
        tk.Button(root, text='Hide Data', command=self.hide_data).pack(pady=10)
        tk.Button(root, text='Extract Data', command=self.extract_data).pack(pady=10)
        
    def hide_data(self):
        filetypes = [('Image Files', '*.png;*.bmp')] if self.mode.get() == 'Image' else [('WAV Audio', '*.wav')]
        input_path = filedialog.askopenfilename(title='Select file to hide data in', filetypes=filetypes)
        if not input_path:
            return
        text = simpledialog.askstring('Input', 'Enter text to hide:')
        if not text:
            return
        output_path = filedialog.asksaveasfilename(title='Save stego file as', defaultextension='.png' if self.mode.get() == 'Image' else '.wav')
        if not output_path:
            return
        try:
            if self.mode.get() == 'Image':
                hide_text_in_image(input_path, text, output_path)
            else:
                hide_text_in_audio(input_path, text, output_path)
            messagebox.showinfo('Success', f'Data hidden successfully in {os.path.basename(output_path)}')
        except Exception as e:
            messagebox.showerror('Error', str(e))
    
    def extract_data(self):
        filetypes = [('Image Files', '*.png;*.bmp')] if self.mode.get() == 'Image' else [('WAV Audio', '*.wav')]
        input_path = filedialog.askopenfilename(title='Select file to extract data from', filetypes=filetypes)
        if not input_path:
            return
        try:
            if self.mode.get() == 'Image':
                text = extract_text_from_image(input_path)
            else:
                text = extract_text_from_audio(input_path)
            messagebox.showinfo('Extracted Data', text)
        except Exception as e:
            messagebox.showerror('Error', str(e))

def main():
    root = tk.Tk()
    app = StegApp(root)
    root.mainloop()

if __name__ == '__main__':
    main() 

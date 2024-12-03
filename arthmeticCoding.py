import tkinter as tk
from tkinter import filedialog
from collections import OrderedDict
import struct
import decimal

################################ Global Variables ###########################################
CharsProb = {}
Ranges = {}

############################################ Get Probability #################################

def GetPropability(s):
    global CharsProb, Ranges
    CharsProb.clear()
    Ranges.clear()
    for char in s:
        CharsProb[char] = CharsProb.get(char, 0) + 1

    for key in CharsProb.keys():
        CharsProb[key] /= len(s)

    sortedDict = OrderedDict(sorted(CharsProb.items()))
    lowRange = 0

    for key, value in sortedDict.items():
        Ranges[key] = (lowRange, lowRange + value)
        lowRange += value

####################################### Compress ###################################

def compress(text):
    if len(text):
        low, high = 0, 1
        for char in text:
            nLow = low + (high - low) * Ranges[char][0]
            nHigh = low + (high - low) * Ranges[char][1]
            low, high = nLow, nHigh
        return (low + high) / 2
    else:
        return None

########################### Store in Binary File #############################

def StoreResultIntoFile(binary_filename, code, text_length):
    try:
        with open(binary_filename, "wb") as binaryFile:
            binaryFile.write(struct.pack('i', text_length))
            binaryFile.write(b'\n')
            binaryFile.write(struct.pack('f', code))
            binaryFile.write(b'\n')
            for key, value in CharsProb.items():
                binaryFile.write(struct.pack('=c f', key.encode('utf-8'), value))
        print(f"Compressed data saved to {binary_filename}")
    except Exception as e:
        print(f"Error writing compressed file: {e}")

####################################### Decompress ###################################


def Decompress(binary_filename, text_filename):
    try:
        with open(binary_filename, "rb") as binary_file:
            # Read the length of the original text
            length = struct.unpack('i', binary_file.read(4))[0]
            binary_file.read(1)  # Skip newline
            
            # Read the compressed value
            compressed_value = decimal.Decimal(struct.unpack('f', binary_file.read(4))[0])
            binary_file.read(1)  # Skip newline
            
            # Read the probability table
            probability_table = {}
            while True:
                packed_data = binary_file.read(5)  # 1 byte for char + 4 bytes for float
                if not packed_data or len(packed_data) < 5:
                    break
                char, prob = struct.unpack('=c f', packed_data)
                char = char.decode('utf-8')
                probability_table[char] = decimal.Decimal(prob)

            # Recreate ranges
            low_range = {}
            high_range = {}
            cumulative_value = decimal.Decimal(0)
            for char, prob in sorted(probability_table.items()):
                low_range[char] = cumulative_value
                high_range[char] = cumulative_value + prob
                cumulative_value += prob

            # Decode the text
            low = decimal.Decimal(0)
            high = decimal.Decimal(1)
            result = ""
            for _ in range(length):
                value = (compressed_value - low) / (high - low)
                for char, prob in sorted(probability_table.items()):
                    if low_range[char] <= value < high_range[char]:
                        result += char
                        new_low = low + (high - low) * low_range[char]
                        new_high = low + (high - low) * high_range[char]
                        low, high = new_low, new_high
                        break

        # Write the decoded text to the output file
        with open(text_filename, "w") as output_file:
            output_file.write(result)
        print(f"Decompressed content written to {text_filename}")
    except Exception as e:
        print(f"Error decompressing file: {e}")


####################################### File Pickers ###################################

def pick_file_compress():
    file_path = filedialog.askopenfilename(
        title="Select a File to Compress",
        filetypes=(("Text Files", ".txt"), ("All Files", ".*"))
    )
    if file_path:
        compress_entry.delete(0, tk.END)
        compress_entry.insert(0, file_path)
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
            GetPropability(file_content)
            code = compress(file_content)
            if code is not None:
                StoreResultIntoFile("compressed.bin", code, len(file_content))
                print("File successfully compressed.")
            else:
                print("Compression failed!")
        except Exception as e:
            print(f"Error reading file or compressing: {e}")

def pick_file_decompress():
    file_path = filedialog.askopenfilename(
        title="Select a File to Decompress",
        filetypes=(("Binary Files", ".bin"), ("All Files", ".*"))
    )
    if file_path:
        decompress_entry.delete(0, tk.END)
        decompress_entry.insert(0, file_path)
        Decompress(file_path, "decompressed.txt")

####################################### Tkinter GUI ###################################

# Create the main window
root = tk.Tk()
root.title("File Compression and Decompression")
root.geometry("600x200")

# Compress Section
compress_frame = tk.Frame(root)
compress_frame.pack(pady=10)

compress_button = tk.Button(compress_frame, text="Pick File to Compress", command=pick_file_compress)
compress_button.pack(side="left", padx=5)

compress_entry = tk.Entry(compress_frame, width=50)
compress_entry.pack(side="left", padx=5)

# Decompress Section
decompress_frame = tk.Frame(root)
decompress_frame.pack(pady=10)

decompress_button = tk.Button(decompress_frame, text="Pick File to Decompress", command=pick_file_decompress)
decompress_button.pack(side="left", padx=5)

decompress_entry = tk.Entry(decompress_frame, width=50)
decompress_entry.pack(side="left", padx=5)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.destroy, bg="red", fg="white")
exit_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()

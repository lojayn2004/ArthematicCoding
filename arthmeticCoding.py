import tkinter as tk
from tkinter import filedialog
from collections import OrderedDict
import struct
from decimal import Decimal, getcontext

getcontext().prec = 1500
################################ Global Variables ###########################################
CharsProb = {}
Ranges = {}
stringToBeCompressed = ""

############################################ Get Probability #################################

def GetPropability(s):
    global CharsProb
    global Ranges
    for i in range(len(s)):
        if s[i] not in CharsProb:
            CharsProb[s[i]] = Decimal(1)
            continue
        CharsProb[s[i]] += 1

    for key in CharsProb.keys():
        CharsProb[key] = CharsProb[key] / len(s)
    sortedDict = OrderedDict(sorted(CharsProb.items()))
    lowRange = Decimal(0)

    for key, value in sortedDict.items():
        Ranges[key] = (lowRange, lowRange + value)
        lowRange += value


####################################### Compress ###################################

def compress(text):
    if len(text):
        low = Decimal(0)
        high = Decimal(1)
        for i in range(len(text)):
            nLow = low + (high - low) * Decimal(Ranges[text[i]][0])
            nHigh = low + (high - low) * Decimal(Ranges[text[i]][1])
            low, high = nLow, nHigh
        return (low + high) / 2
    else:
        return None


########################### Store in Binary File #############################

def StoreResultIntoFile(binary_filename, code, text_length):
    global CharsProb
    try:
        # Writing to the binary file
        with open(binary_filename, "wb") as binaryFile:
            binaryFile.write(struct.pack('i', text_length))
            binaryFile.write((str(code) + '\n').encode('utf-8'))
            
            for key, value in CharsProb.items():
                binaryFile.write(struct.pack('=c', key.encode('utf-8')))
                binaryFile.write((str(value) + '\n').encode('utf-8'))

    except Exception as e:
        print(f"Error writing files: {e}")

    try: 
        text_filename = "output_txt.txt"
        with open(text_filename, "w") as textFile:
             textFile.write(f"Text Length: {text_length}\n")
             textFile.write(f"Code: {code}\n")
             textFile.write("Character Probabilities:\n")
             for key, value in CharsProb.items():
                 textFile.write(f"{key}: {value}\n")
    except Exception as e:
            pass


####################################### Decompress ###################################


def Decompresse(binary_filename, text_filename):
    with open(binary_filename, "rb") as binary_file:
        length = struct.unpack('i', binary_file.read(4))[0]
        compressed_value = Decimal(binary_file.readline().strip().decode('utf-8'))
        probability_table = {}
        while True:
            key = binary_file.read(1)
            if not key:
                break
            key = key.decode('utf-8')
            value = Decimal(binary_file.readline().strip().decode('utf-8'))
            probability_table[key] = value

        chars = sorted(probability_table)
        low_range = {}
        high_range = {}
        cumulative_value = Decimal(0)
        for char in chars:
            low_range[char] = cumulative_value
            high_range[char] = cumulative_value + probability_table[char]
            cumulative_value += probability_table[char]

        low = Decimal(0)
        high = Decimal(1)
        result = ""
        for x in range(length):
            value = (compressed_value - low) / (high - low)
            for ch in chars:
                if low_range[ch] <= value < high_range[ch]:
                    result += ch
                    nLow = low + (high - low) * low_range[ch]
                    nHigh = low + (high - low) * high_range[ch]
                    low = nLow
                    high = nHigh
                    break

    # Output the decompressed string
    with open("decompressed.txt", "w") as output_file:
        output_file.write(result)
    print(f"Decompressed data saved to decompressed.txt")


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
                print("File successfully compressed.\n")
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
        Decompresse(file_path, "decompressed.txt")
        print(f"File successfully decompressed.")

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

# Arthematic Coding

This project implements a file compression and decompression tool using arithmetic coding. The compression algorithm leverages `Decimal` with up to 100-digit precision, enabling high accuracy in handling probabilities and ranges. The tool features a user-friendly GUI built with Tkinter for selecting files to compress or decompress.

---

## Features

- **High Precision Compression**: Handles probabilities and ranges with up to 100 digits after the decimal point for improved accuracy.
- **GUI Integration**: Provides a Tkinter-based graphical interface for ease of use.
- **Custom File Handling**: Supports storing results in binary files and recreating decompressed files.
- **Error Handling**: Ensures smooth operations with informative error messages for exceptional cases.

---

## How It Works

### Compression
1. **Probability Calculation**: Computes character probabilities from the input text.
2. **Range Assignment**: Assigns ranges for each character based on their probabilities.
3. **Arithmetic Encoding**: Generates a compressed value by iteratively narrowing the range.

### Decompression
1. **Probability Reconstruction**: Recreates the probability table from the binary file.
2. **Range Reconstruction**: Rebuilds character ranges using probabilities.
3. **Decoding**: Iteratively decodes the compressed value back to the original text.

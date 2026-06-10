#!/usr/bin/env python3
"""
Script to convert .png to base64 encoded text file.

This script reads the PNG image from Resources,
converts it to base64 encoding, and saves the result
to Resources as txt file.
"""

import base64
import os

def convert_png_to_base64(input_path: str, output_path: str) -> None:
    """
    Convert a PNG image to base64 encoded text file.
    
    Args:
        input_path: Path to the input PNG file
        output_path: Path to the output base64 text file
    """
    # Read the binary PNG file
    with open(input_path, 'rb') as f:
        png_data = f.read()
    
    # Encode to base64
    base64_data = base64.b64encode(png_data).decode('utf-8')
    
    # Write to output file
    with open(output_path, 'w') as f:
        f.write(base64_data)
    
    print(f"Successfully converted '{input_path}' to base64")
    print(f"Output saved to: '{output_path}'")
    print(f"Base64 string length: {len(base64_data)} characters")
    
def input_file() -> str:
    """Gets the name of the input file to be converted."""
    file_name = input("Enter the name of the PNG file to convert (without extension): ")
    
    return file_name.strip() + ".png"
    
def output_file() -> str:
    """Gets the name of the file to be output on Resources/"""
    file_name = input("Enter the name of the output file (without extension): ")
    
    return file_name.strip() + ".txt"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_path = os.path.join(script_dir, 'Resources', input_file())
    output_path = os.path.join(script_dir, 'Resources', output_file())

    convert_png_to_base64(input_path, output_path)

if __name__ == '__main__':
    main()

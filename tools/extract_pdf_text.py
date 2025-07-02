#!/usr/bin/env python3
import os
import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from {pdf_path}: {str(e)}"

def main():
    current_dir = Path(".")
    pdf_files = list(current_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in current directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        print(f"\n{'='*50}")
        print(f"Extracting text from: {pdf_file.name}")
        print(f"{'='*50}")
        
        text = extract_text_from_pdf(pdf_file)
        
        # Save extracted text to a txt file
        output_file = pdf_file.with_suffix('.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Text saved to: {output_file.name}")
        print(f"Preview (first 500 characters):")
        print(text[:500] + "..." if len(text) > 500 else text)

if __name__ == "__main__":
    main()
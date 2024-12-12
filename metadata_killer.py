#!/usr/bin/env python3
import os
import sys
from PIL import Image, ExifTags
from PyPDF2 import PdfReader, PdfWriter
import shutil
from datetime import datetime, timedelta
import argparse
from pathlib import Path
import random
import piexif
import time

def generate_random_date():
    """Generate a random date between 2000 and 2020."""
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2010, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_days)

def clean_image_metadata(input_path, output_path):
    """Remove all metadata from image files and add confusion."""
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Remove all EXIF data
            data = list(img.getdata())
            new_img = Image.new(img.mode, img.size)
            new_img.putdata(data)
            
            # Create blank EXIF data with random dates
            random_date = generate_random_date()
            zeroth_ifd = {
                piexif.ImageIFD.Make: b"Unknown",
                piexif.ImageIFD.Model: b"Unknown",
                piexif.ImageIFD.Software: b"Unknown",
                piexif.ImageIFD.DateTime: random_date.strftime("%Y:%m:%d %H:%M:%S").encode()
            }
            
            exif_dict = {"0th": zeroth_ifd, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            exif_bytes = piexif.dump(exif_dict)
            
            # Save with minimal metadata and random date
            if img.format == 'JPEG':
                new_img.save(output_path, format=img.format, exif=exif_bytes, quality='keep')
            else:
                new_img.save(output_path, format=img.format)
            
            # Additional obfuscation: Modify file timestamps
            random_timestamp = time.mktime(random_date.timetuple())
            os.utime(output_path, (random_timestamp, random_timestamp))
            
        return True
    except Exception as e:
        print(f"Error processing image {input_path}: {str(e)}")
        return False

def clean_pdf_metadata(input_path, output_path):
    """Remove all metadata from PDF files and add confusion."""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy pages with additional processing
        for page in reader.pages:
            # Remove any form fields or annotations
            if '/Annots' in page:
                del page['/Annots']
            writer.add_page(page)
        
        # Create completely empty metadata
        writer.add_metadata({
            '/Creator': '',
            '/Producer': '',
            '/Title': '',
            '/Author': '',
            '/Subject': '',
            '/Keywords': '',
            '/CreationDate': '',
            '/ModDate': ''
        })
        
        # Save the new PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        # Additional obfuscation: Modify file timestamps
        random_date = generate_random_date()
        random_timestamp = time.mktime(random_date.timetuple())
        os.utime(output_path, (random_timestamp, random_timestamp))
        
        return True
    except Exception as e:
        print(f"Error processing PDF {input_path}: {str(e)}")
        return False

def process_file(input_path):
    """Process a single file and remove its metadata with enhanced obfuscation."""
    try:
        # Get file extension and create output filename with random component
        file_path = Path(input_path)
        extension = file_path.suffix.lower()
        random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"clean_{random_string}_{file_path.stem}_{timestamp}{extension}"
        output_path = os.path.join(file_path.parent, output_filename)

        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            success = clean_image_metadata(input_path, output_path)
        elif extension == '.pdf':
            success = clean_pdf_metadata(input_path, output_path)
        else:
            print(f"Unsupported file type: {extension}")
            return False

        if success:
            print(f"Successfully processed: {input_path}")
            print(f"Clean file saved as: {output_path}")
            
            # Additional file attribute cleaning
            try:
                # Remove or modify file attributes
                os.chmod(output_path, 0o644)  # Basic read/write permissions
            except:
                pass
                
        return success

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Enhanced Metadata Killer - Thoroughly remove and obfuscate metadata")
    parser.add_argument("files", nargs='+', help="Files to process")
    args = parser.parse_args()

    print("Enhanced Metadata Killer - Starting thorough metadata removal...")
    for file_path in args.files:
        if os.path.exists(file_path):
            process_file(file_path)
        else:
            print(f"File not found: {file_path}")
    print("Processing complete. Files have been cleaned and obfuscated.")

if __name__ == "__main__":
    main() 
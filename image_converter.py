import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os

class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Format Converter")
        
        # Variables
        self.source_path = tk.StringVar()
        self.target_format = tk.StringVar(value="PNG")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Source file selection
        ttk.Label(main_frame, text="Source Image:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.source_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Target format selection
        ttk.Label(main_frame, text="Convert to:").grid(row=1, column=0, sticky=tk.W)
        formats = ["PNG", "WEBP", "JPEG", "GIF"]
        format_combo = ttk.Combobox(main_frame, textvariable=self.target_format, values=formats, state="readonly")
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Convert button
        ttk.Button(main_frame, text="Convert Image", command=self.convert_image).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=300)
        status_label.grid(row=3, column=0, columnspan=3, pady=5)

    def browse_file(self):
        filetypes = (
            ('Image files', '*.png;*.jpg;*.jpeg;*.webp;*.gif'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(
            title='Select an image',
            filetypes=filetypes
        )
        if filename:
            self.source_path.set(filename)

    def convert_image(self):
        try:
            source_path = self.source_path.get()
            if not source_path:
                messagebox.showerror("Error", "Please select a source image")
                return

            # Open the source image
            with Image.open(source_path) as img:
                # Get the directory and filename without extension
                directory = os.path.dirname(source_path)
                filename = os.path.splitext(os.path.basename(source_path))[0]
                
                # Prepare target format and path
                target_format = self.target_format.get().lower()
                if target_format == 'jpeg':
                    # Convert to RGB if saving as JPEG
                    img = img.convert('RGB')
                
                # Create target path
                target_path = os.path.join(directory, f"{filename}_converted.{target_format}")
                
                # Save with optimal settings based on format
                if target_format == 'webp':
                    img.save(target_path, format=target_format, quality=90, method=6)
                elif target_format == 'jpeg':
                    img.save(target_path, format=target_format, quality=90, optimize=True)
                elif target_format == 'png':
                    img.save(target_path, format=target_format, optimize=True)
                else:
                    img.save(target_path, format=target_format)
                
                self.status_var.set(f"Successfully converted!\nSaved as: {target_path}")
                
                # Ask if user wants to open the containing folder
                if messagebox.askyesno("Success", "Would you like to open the containing folder?"):
                    os.startfile(directory)

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
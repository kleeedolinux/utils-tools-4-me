import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
import sys
import threading

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Converter")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input folder selection
        ttk.Label(main_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output folder selection
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Format selection
        ttk.Label(main_frame, text="Target Format:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="jpg")
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, sticky=tk.W)
        formats = [("JPEG", "jpg"), ("PNG", "png"), ("WebP", "webp")]
        for i, (text, value) in enumerate(formats):
            ttk.Radiobutton(format_frame, text=text, value=value, variable=self.format_var).grid(row=0, column=i, padx=10)
        
        # Size inputs
        size_frame = ttk.LabelFrame(main_frame, text="Image Size (pixels)", padding="5")
        size_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5)
        self.width_var = tk.StringVar(value="800")
        ttk.Entry(size_frame, textvariable=self.width_var, width=10).grid(row=0, column=1)
        
        ttk.Label(size_frame, text="Height:").grid(row=0, column=2, padx=5)
        self.height_var = tk.StringVar(value="600")
        ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=0, column=3)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3)
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert Images", command=self.start_conversion)
        self.convert_btn.grid(row=6, column=0, columnspan=3, pady=10)
    
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
    
    def validate_inputs(self):
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select input folder!")
            return False
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select output folder!")
            return False
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Width and height must be positive numbers!")
            return False
        return True
    
    def start_conversion(self):
        if not self.validate_inputs():
            return
        
        # Disable convert button during conversion
        self.convert_btn.state(['disabled'])
        self.status_var.set("Converting...")
        self.progress_var.set(0)
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self.convert_images)
        thread.daemon = True
        thread.start()
    
    def convert_images(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()
        target_format = self.format_var.get()
        width = int(self.width_var.get())
        height = int(self.height_var.get())
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Supported formats
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        
        # Get total number of images
        image_files = [f for f in os.listdir(input_folder) 
                      if os.path.splitext(f)[1].lower() in supported_formats]
        total_images = len(image_files)
        
        if total_images == 0:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No images found in input folder!"))
            self.root.after(0, self.reset_ui)
            return
        
        converted = 0
        for filename in image_files:
            try:
                # Open and convert image
                with Image.open(os.path.join(input_folder, filename)) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'P') and target_format.lower() in ['jpg', 'jpeg']:
                        img = img.convert('RGB')
                    
                    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                    new_filename = os.path.splitext(filename)[0] + '.' + target_format
                    
                    # Handle format-specific saving
                    save_format = 'JPEG' if target_format.lower() in ['jpg', 'jpeg'] else target_format.upper()
                    save_kwargs = {}
                    
                    if save_format == 'JPEG':
                        save_kwargs['quality'] = 95
                    elif save_format == 'PNG':
                        save_kwargs['optimize'] = True
                    elif save_format == 'WEBP':
                        save_kwargs['quality'] = 95
                        save_kwargs['method'] = 6
                    
                    resized_img.save(
                        os.path.join(output_folder, new_filename),
                        save_format,
                        **save_kwargs
                    )
                    converted += 1
                    
                    # Update progress
                    progress = (converted / total_images) * 100
                    self.progress_var.set(progress)
                    self.status_var.set(f"Converting: {converted}/{total_images}")
            
            except Exception as e:
                print(f"Error converting {filename}: {str(e)}")
                self.status_var.set(f"Error converting {filename}")
        
        # Show completion message and reset UI
        self.root.after(0, lambda: messagebox.showinfo("Success", 
            f"Conversion complete!\nConverted {converted} out of {total_images} images."))
        self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        self.convert_btn.state(['!disabled'])
        self.status_var.set("Ready")
        self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = ImageConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pydub import AudioSegment
import os

class AudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Format Converter")
        
        # Variables
        self.source_path = tk.StringVar()
        self.target_format = tk.StringVar(value="MP3")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Source file selection
        ttk.Label(main_frame, text="Source Audio:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.source_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Target format selection
        ttk.Label(main_frame, text="Convert to:").grid(row=1, column=0, sticky=tk.W)
        formats = ["MP3", "WAV", "OGG", "FLAC", "M4A"]
        format_combo = ttk.Combobox(main_frame, textvariable=self.target_format, 
                                  values=formats, state="readonly")
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Quality frame
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding="5")
        quality_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Bitrate selection
        self.bitrate_var = tk.StringVar(value="192")
        ttk.Label(quality_frame, text="Bitrate (kbps):").grid(row=0, column=0, padx=5)
        bitrates = ["128", "192", "256", "320"]
        ttk.Combobox(quality_frame, textvariable=self.bitrate_var, values=bitrates, 
                    state="readonly", width=10).grid(row=0, column=1, padx=5)
        
        # Convert button
        ttk.Button(main_frame, text="Convert Audio", command=self.convert_audio).grid(
            row=3, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=300)
        status_label.grid(row=4, column=0, columnspan=3, pady=5)

    def browse_file(self):
        filetypes = (
            ('Audio files', '*.mp3;*.wav;*.ogg;*.flac;*.m4a'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(
            title='Select audio file',
            filetypes=filetypes
        )
        if filename:
            self.source_path.set(filename)

    def convert_audio(self):
        try:
            source_path = self.source_path.get()
            if not source_path:
                messagebox.showerror("Error", "Please select a source audio file")
                return

            # Get source format
            source_format = os.path.splitext(source_path)[1][1:].lower()
            
            # Load the audio file
            audio = AudioSegment.from_file(source_path, format=source_format)
            
            # Get target settings
            target_format = self.target_format.get().lower()
            bitrate = f"{self.bitrate_var.get()}k"
            
            # Create target path
            directory = os.path.dirname(source_path)
            filename = os.path.splitext(os.path.basename(source_path))[0]
            target_path = os.path.join(directory, f"{filename}_converted.{target_format}")
            
            # Export with specified format and quality
            audio.export(
                target_path,
                format=target_format,
                bitrate=bitrate,
                tags={'converted_by': 'Audio Converter'}
            )
            
            self.status_var.set(f"Successfully converted!\nSaved as: {target_path}")
            
            if messagebox.askyesno("Success", "Would you like to open the containing folder?"):
                os.startfile(directory)

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def main():
    root = tk.Tk()
    app = AudioConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
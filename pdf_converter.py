import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from docx import Document
from pdf2docx import Converter
from docx2pdf import convert
import os

class PDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF/Word Converter")
        
        # Variables
        self.source_path = tk.StringVar()
        self.conversion_type = tk.StringVar(value="PDF to Word")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Source file selection
        ttk.Label(main_frame, text="Source File:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.source_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Conversion type selection
        ttk.Label(main_frame, text="Convert:").grid(row=1, column=0, sticky=tk.W)
        conversion_types = ["PDF to Word", "Word to PDF"]
        type_combo = ttk.Combobox(main_frame, textvariable=self.conversion_type, 
                                 values=conversion_types, state="readonly")
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        type_combo.bind('<<ComboboxSelected>>', self.update_file_types)
        
        # Convert button
        ttk.Button(main_frame, text="Convert", command=self.convert_file).grid(
            row=2, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=300)
        status_label.grid(row=3, column=0, columnspan=3, pady=5)

    def update_file_types(self, event=None):
        self.source_path.set("")  # Clear the current path

    def browse_file(self):
        if self.conversion_type.get() == "PDF to Word":
            filetypes = [('PDF files', '*.pdf')]
        else:
            filetypes = [('Word files', '*.docx')]
        
        filename = filedialog.askopenfilename(
            title='Select file',
            filetypes=filetypes
        )
        if filename:
            self.source_path.set(filename)

    def convert_file(self):
        try:
            source_path = self.source_path.get()
            if not source_path:
                messagebox.showerror("Error", "Please select a source file")
                return

            directory = os.path.dirname(source_path)
            filename = os.path.splitext(os.path.basename(source_path))[0]

            if self.conversion_type.get() == "PDF to Word":
                # Convert PDF to Word
                target_path = os.path.join(directory, f"{filename}_converted.docx")
                cv = Converter(source_path)
                cv.convert(target_path)
                cv.close()
            else:
                # Convert Word to PDF
                target_path = os.path.join(directory, f"{filename}_converted.pdf")
                convert(source_path, target_path)

            self.status_var.set(f"Successfully converted!\nSaved as: {target_path}")
            
            if messagebox.askyesno("Success", "Would you like to open the containing folder?"):
                os.startfile(directory)

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def main():
    root = tk.Tk()
    app = PDFConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os

class LatexConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX/Plain Text Converter")
        
        # Variables
        self.source_path = tk.StringVar()
        self.conversion_mode = tk.StringVar(value="LaTeX to Plain")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Conversion mode selection
        ttk.Label(main_frame, text="Conversion Mode:").grid(row=0, column=0, sticky=tk.W)
        modes = ["LaTeX to Plain", "Plain to LaTeX"]
        mode_combo = ttk.Combobox(main_frame, textvariable=self.conversion_mode, 
                                values=modes, state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        mode_combo.bind('<<ComboboxSelected>>', self.update_labels)
        
        # Source file selection
        ttk.Label(main_frame, text="Source File:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.source_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=1, column=2, padx=5)
        
        # Text areas
        self.input_label = ttk.Label(main_frame, text="LaTeX Input:")
        self.input_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10,0))
        self.input_text = tk.Text(main_frame, height=10, width=50)
        self.input_text.grid(row=3, column=0, columnspan=3, pady=5)
        
        self.output_label = ttk.Label(main_frame, text="Plain Text Output:")
        self.output_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10,0))
        self.output_text = tk.Text(main_frame, height=10, width=50)
        self.output_text.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(buttons_frame, text="Convert", command=self.convert_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save Output", command=self.save_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=300)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def update_labels(self, event=None):
        if self.conversion_mode.get() == "LaTeX to Plain":
            self.input_label.config(text="LaTeX Input:")
            self.output_label.config(text="Plain Text Output:")
        else:
            self.input_label.config(text="Plain Text Input:")
            self.output_label.config(text="LaTeX Output:")

    def browse_file(self):
        if self.conversion_mode.get() == "LaTeX to Plain":
            filetypes = (('LaTeX files', '*.tex'), ('All files', '*.*'))
        else:
            filetypes = (('Text files', '*.txt'), ('All files', '*.*'))
            
        filename = filedialog.askopenfilename(
            title='Select file',
            filetypes=filetypes
        )
        if filename:
            self.source_path.set(filename)
            self.load_file(filename)

    def load_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

    def convert_text(self):
        try:
            input_text = self.input_text.get('1.0', tk.END)
            
            if self.conversion_mode.get() == "LaTeX to Plain":
                output_text = self.latex_to_plain(input_text)
            else:
                output_text = self.plain_to_latex(input_text)
            
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', output_text)
            
            self.status_var.set("Conversion successful!")
        except Exception as e:
            self.status_var.set(f"Error during conversion: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")

    def plain_to_latex(self, plain_text):
        # Add document structure
        latex_text = "\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\n\\begin{document}\n\n"
        
        # Convert headers
        lines = plain_text.split('\n')
        in_list = False
        list_type = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    latex_text += "\\end{" + list_type + "}\n"
                    in_list = False
                latex_text += "\n"
                continue
            
            # Handle headers
            if line.startswith('# '):
                latex_text += "\\section{" + line[2:] + "}\n"
            elif line.startswith('## '):
                latex_text += "\\subsection{" + line[3:] + "}\n"
            elif line.startswith('### '):
                latex_text += "\\subsubsection{" + line[4:] + "}\n"
            
            # Handle lists
            elif line.startswith('• ') or line.startswith('* '):
                if not in_list or list_type != "itemize":
                    if in_list:
                        latex_text += "\\end{" + list_type + "}\n"
                    latex_text += "\\begin{itemize}\n"
                    in_list = True
                    list_type = "itemize"
                latex_text += "\\item " + line[2:] + "\n"
            
            elif re.match(r'^\d+\.\s', line):
                if not in_list or list_type != "enumerate":
                    if in_list:
                        latex_text += "\\end{" + list_type + "}\n"
                    latex_text += "\\begin{enumerate}\n"
                    in_list = True
                    list_type = "enumerate"
                item_text = re.sub(r'^\d+\.\s', '', line)
                latex_text += "\\item " + item_text + "\n"
            
            # Handle basic formatting
            else:
                # Convert bold
                line = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', line)
                # Convert italic
                line = re.sub(r'\*(.*?)\*', r'\\textit{\1}', line)
                # Convert underline
                line = re.sub(r'_(.*?)_', r'\\underline{\1}', line)
                
                # Handle special characters
                special_chars = ['&', '%', '$', '#', '_', '{', '}']
                for char in special_chars:
                    line = line.replace(char, '\\' + char)
                
                latex_text += line + " \\\\\n"
        
        # Close any open lists
        if in_list:
            latex_text += "\\end{" + list_type + "}\n"
        
        # Close document
        latex_text += "\n\\end{document}"
        
        return latex_text

    def save_output(self):
        try:
            if self.conversion_mode.get() == "LaTeX to Plain":
                default_ext = '.txt'
                filetypes = (('Text files', '*.txt'), ('All files', '*.*'))
            else:
                default_ext = '.tex'
                filetypes = (('LaTeX files', '*.tex'), ('All files', '*.*'))
                
            filename = filedialog.asksaveasfilename(
                title='Save output',
                defaultextension=default_ext,
                filetypes=filetypes
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.output_text.get('1.0', tk.END))
                self.status_var.set(f"Saved as: {filename}")
        except Exception as e:
            self.status_var.set(f"Error saving file: {str(e)}")
            messagebox.showerror("Error", f"Save failed: {str(e)}")

    def latex_to_plain(self, latex_text):
        # Remove comments
        latex_text = re.sub(r'%.*$', '', latex_text, flags=re.MULTILINE)
        
        # Remove document class and packages
        latex_text = re.sub(r'\\documentclass.*?\n', '', latex_text)
        latex_text = re.sub(r'\\usepackage.*?\n', '', latex_text)
        
        # Remove document environment
        latex_text = re.sub(r'\\begin{document}', '', latex_text)
        latex_text = re.sub(r'\\end{document}', '', latex_text)
        
        # Handle sections
        latex_text = re.sub(r'\\section\*?{(.*?)}', r'\n\n# \1\n', latex_text)
        latex_text = re.sub(r'\\subsection\*?{(.*?)}', r'\n\n## \1\n', latex_text)
        latex_text = re.sub(r'\\subsubsection\*?{(.*?)}', r'\n\n### \1\n', latex_text)
        
        # Handle basic formatting
        latex_text = re.sub(r'\\textbf{(.*?)}', r'**\1**', latex_text)
        latex_text = re.sub(r'\\textit{(.*?)}', r'*\1*', latex_text)
        latex_text = re.sub(r'\\emph{(.*?)}', r'*\1*', latex_text)
        latex_text = re.sub(r'\\underline{(.*?)}', r'_\1_', latex_text)
        
        # Handle environments
        latex_text = re.sub(r'\\begin{itemize}(.*?)\\end{itemize}', 
                          lambda m: self.convert_list(m.group(1)), 
                          latex_text, flags=re.DOTALL)
        latex_text = re.sub(r'\\begin{enumerate}(.*?)\\end{enumerate}', 
                          lambda m: self.convert_numbered_list(m.group(1)), 
                          latex_text, flags=re.DOTALL)
        
        # Handle special characters
        replacements = {
            '~': ' ',
            '\\&': '&',
            '\\%': '%',
            '\\$': '$',
            '\\_': '_',
            '\\{': '{',
            '\\}': '}',
            '\\\\': '\n',
            '``': '"',
            "''": '"'
        }
        for latex, plain in replacements.items():
            latex_text = latex_text.replace(latex, plain)
        
        # Clean up multiple newlines and spaces
        latex_text = re.sub(r'\n{3,}', '\n\n', latex_text)
        latex_text = re.sub(r' +', ' ', latex_text)
        
        return latex_text.strip()

    def convert_list(self, list_content):
        items = re.findall(r'\\item\s*(.*?)(?=\\item|\s*$)', list_content, re.DOTALL)
        return '\n'.join(f'• {item.strip()}' for item in items)

    def convert_numbered_list(self, list_content):
        items = re.findall(r'\\item\s*(.*?)(?=\\item|\s*$)', list_content, re.DOTALL)
        return '\n'.join(f'{i+1}. {item.strip()}' for i, item in enumerate(items))

    def clear_all(self):
        self.input_text.delete('1.0', tk.END)
        self.output_text.delete('1.0', tk.END)
        self.source_path.set("")
        self.status_var.set("")

def main():
    root = tk.Tk()
    app = LatexConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
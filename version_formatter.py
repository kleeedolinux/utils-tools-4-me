import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import json

class VersionFormatter:
    def __init__(self, root):
        self.root = root
        self.root.title("Version Format Generator")
        
        # Variables
        self.version_type = tk.StringVar(value="Alpha")
        self.alpha_var = tk.StringVar()
        self.revision_var = tk.StringVar(value="1")
        self.result_var = tk.StringVar()
        
        # Semantic version variables
        self.major_var = tk.StringVar(value="1")
        self.minor_var = tk.StringVar(value="0")
        self.patch_var = tk.StringVar(value="0")
        self.update_name_var = tk.StringVar()
        
        # Changelog variables
        self.changes = {
            "Added": [],
            "Removed": [],
            "Changed": [],
            "Fixed": [],
            "Security": []
        }
        
        # Add text format option
        self.save_as_text = tk.BooleanVar(value=True)
        
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Version tab
        version_frame = ttk.Frame(notebook, padding="10")
        notebook.add(version_frame, text="Version")
        
        # Version type selection
        ttk.Label(version_frame, text="Version Type:").grid(row=0, column=0, sticky=tk.W)
        version_types = ["Alpha", "Snapshot", "Official"]
        type_combo = ttk.Combobox(version_frame, textvariable=self.version_type, 
                                 values=version_types, state="readonly")
        type_combo.grid(row=0, column=1, padx=5, pady=5)
        type_combo.bind('<<ComboboxSelected>>', self.update_version_fields)
        
        # Version fields frame
        self.version_fields_frame = ttk.Frame(version_frame)
        self.version_fields_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.show_alpha_fields()  # Default view
        
        # Generate button
        ttk.Button(version_frame, text="Generate Version", 
                  command=self.generate_version).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Result display
        ttk.Label(version_frame, text="Generated Version:").grid(row=3, column=0, sticky=tk.W)
        result_label = ttk.Label(version_frame, textvariable=self.result_var, 
                               font=('Arial', 12, 'bold'))
        result_label.grid(row=3, column=1, padx=5, pady=5)
        
        # Changelog tab
        changelog_frame = ttk.Frame(notebook, padding="10")
        notebook.add(changelog_frame, text="Changelog")
        
        # Add format selection
        format_frame = ttk.Frame(changelog_frame)
        format_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        ttk.Checkbutton(format_frame, text="Also save as text file", 
                       variable=self.save_as_text).pack(side=tk.LEFT)
        
        # Changelog categories
        categories = ["Added", "Removed", "Changed", "Fixed", "Security"]
        for i, category in enumerate(categories):
            ttk.Label(changelog_frame, text=f"{category}:").grid(row=i*2+1, column=0, sticky=tk.W)
            text = tk.Text(changelog_frame, height=3, width=40)
            text.grid(row=i*2+2, column=0, columnspan=2, pady=(0, 10))
            text.tag_configure('bullet', lmargin1=20, lmargin2=20)
            setattr(self, f"{category.lower()}_text", text)
        
        # Save changelog button
        ttk.Button(changelog_frame, text="Save Changelog", 
                  command=self.save_changelog).grid(row=len(categories)*2+2, column=0, columnspan=2, pady=10)

    def update_version_fields(self, event=None):
        # Clear current fields
        for widget in self.version_fields_frame.winfo_children():
            widget.destroy()
        
        version_type = self.version_type.get()
        if version_type == "Alpha":
            self.show_alpha_fields()
        elif version_type == "Snapshot":
            self.show_snapshot_fields()
        else:  # Official
            self.show_official_fields()

    def show_alpha_fields(self):
        ttk.Label(self.version_fields_frame, text="Alpha number:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.alpha_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.version_fields_frame, text="Revision:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.revision_var).grid(row=1, column=1, padx=5, pady=5)

    def show_snapshot_fields(self):
        ttk.Label(self.version_fields_frame, text="Revision:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.revision_var).grid(row=0, column=1, padx=5, pady=5)

    def show_official_fields(self):
        ttk.Label(self.version_fields_frame, text="Major:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.major_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.version_fields_frame, text="Minor:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.minor_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.version_fields_frame, text="Patch:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.patch_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.version_fields_frame, text="Update Name:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(self.version_fields_frame, textvariable=self.update_name_var).grid(row=3, column=1, padx=5, pady=5)

    def get_current_week(self):
        return datetime.now().isocalendar()[1]

    def generate_version(self):
        try:
            version_type = self.version_type.get()
            current_year = datetime.now().year
            current_week = self.get_current_week()
            
            if version_type == "Alpha":
                alpha = self.alpha_var.get()
                revision = self.revision_var.get()
                version = f"{alpha}a{current_year}w{current_week:02d}-{revision}"
            
            elif version_type == "Snapshot":
                revision = self.revision_var.get()
                version = f"w{current_week:02d}y{current_year}_{revision}"
            
            else:  # Official
                major = self.major_var.get()
                minor = self.minor_var.get()
                patch = self.patch_var.get()
                update_name = self.update_name_var.get()
                version = f"{major}.{minor}.{patch}"
                if update_name:
                    version += f"-{update_name}"
            
            self.result_var.set(version)
            self.current_version = version
            
        except Exception as e:
            self.result_var.set("Error: Invalid input")
            messagebox.showerror("Error", str(e))

    def generate_text_changelog(self, changelog_entry):
        text_content = [
            f"# Changelog for version {changelog_entry['version']}",
            f"Date: {changelog_entry['date']}\n"
        ]
        
        for category in ["Added", "Removed", "Changed", "Fixed", "Security"]:
            if category in changelog_entry['changes'] and changelog_entry['changes'][category]:
                text_content.append(f"## {category}")
                for item in changelog_entry['changes'][category]:
                    text_content.append(f"- {item}")
                text_content.append("")  # Empty line between categories
        
        return "\n".join(text_content)

    def save_changelog(self):
        if not hasattr(self, 'current_version'):
            messagebox.showerror("Error", "Please generate a version first")
            return
            
        # Create changelog directory if it doesn't exist
        os.makedirs("changelog", exist_ok=True)
        
        # Collect changes from text widgets
        changes = {}
        for category in ["Added", "Removed", "Changed", "Fixed", "Security"]:
            text_widget = getattr(self, f"{category.lower()}_text")
            content = text_widget.get("1.0", tk.END).strip()
            if content:
                changes[category] = [line.strip("• ").strip() for line in content.split('\n') if line.strip()]
        
        if not any(changes.values()):
            messagebox.showinfo("Info", "No changes to save")
            return
        
        # Create changelog entry
        changelog_entry = {
            "version": self.current_version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "changes": changes
        }
        
        # Save JSON format
        json_filename = os.path.join("changelog", f"changelog_{self.current_version}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(changelog_entry, f, indent=2)
        
        # Save text format if selected
        if self.save_as_text.get():
            text_content = self.generate_text_changelog(changelog_entry)
            text_filename = os.path.join("changelog", f"changelog_{self.current_version}.md")
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            messagebox.showinfo("Success", 
                              f"Changelog saved as:\n"
                              f"- {json_filename}\n"
                              f"- {text_filename}")
        else:
            messagebox.showinfo("Success", f"Changelog saved as: {json_filename}")
        
        # Clear text widgets
        for category in ["Added", "Removed", "Changed", "Fixed", "Security"]:
            text_widget = getattr(self, f"{category.lower()}_text")
            text_widget.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = VersionFormatter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
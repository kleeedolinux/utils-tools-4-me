import tkinter as tk
from tkinter import ttk
import time
import pystray
from PIL import Image, ImageDraw
from threading import Thread
import json
import os
from tkinter import messagebox

class PomodoroWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Pomodoro Timer")
        self.geometry("350x500")
        self.configure(bg='#f0f0f0')
        
        self.pomodoro_active = False
        self.remaining_time = 0
        self.is_break = False
        
        # Load or create default settings
        self.settings = {
            'work_time': 25,    # minutes
            'break_time': 5,    # minutes
            'long_break_time': 15,  # minutes
            'sessions_before_long_break': 4
        }
        self.current_session = 0
        self.load_settings()
        
        # Pomodoro Frame
        self.pomodoro_frame = tk.LabelFrame(self, text="Timer", bg='#f0f0f0', font=('Arial', 12))
        self.pomodoro_frame.pack(fill='x', padx=20, pady=10)
        
        # Session Label
        self.session_label = tk.Label(
            self.pomodoro_frame,
            text="Work Time",
            font=('Arial', 14),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.session_label.pack(pady=5)
        
        # Pomodoro Timer Display
        self.pomodoro_label = tk.Label(
            self.pomodoro_frame,
            text="25:00",
            font=('Arial', 48),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.pomodoro_label.pack(pady=10)
        
        # Pomodoro Controls Frame
        controls_frame = tk.Frame(self.pomodoro_frame, bg='#f0f0f0')
        controls_frame.pack(fill='x', padx=10)
        
        # Pomodoro Buttons
        self.start_btn = ttk.Button(
            controls_frame,
            text="Start",
            command=self.toggle_pomodoro
        )
        self.start_btn.pack(side='left', padx=5, pady=5, expand=True)
        
        self.reset_btn = ttk.Button(
            controls_frame,
            text="Reset",
            command=self.reset_pomodoro
        )
        self.reset_btn.pack(side='left', padx=5, pady=5, expand=True)
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self, text="Settings", bg='#f0f0f0', font=('Arial', 12))
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Work Time Setting
        tk.Label(settings_frame, text="Work Time (min):", bg='#f0f0f0').pack(anchor='w', padx=5)
        self.work_time_var = tk.StringVar(value=str(self.settings['work_time']))
        ttk.Entry(settings_frame, textvariable=self.work_time_var).pack(fill='x', padx=5, pady=2)
        
        # Break Time Setting
        tk.Label(settings_frame, text="Break Time (min):", bg='#f0f0f0').pack(anchor='w', padx=5)
        self.break_time_var = tk.StringVar(value=str(self.settings['break_time']))
        ttk.Entry(settings_frame, textvariable=self.break_time_var).pack(fill='x', padx=5, pady=2)
        
        # Long Break Time Setting
        tk.Label(settings_frame, text="Long Break Time (min):", bg='#f0f0f0').pack(anchor='w', padx=5)
        self.long_break_var = tk.StringVar(value=str(self.settings['long_break_time']))
        ttk.Entry(settings_frame, textvariable=self.long_break_var).pack(fill='x', padx=5, pady=2)
        
        # Sessions before long break Setting
        tk.Label(settings_frame, text="Sessions before long break:", bg='#f0f0f0').pack(anchor='w', padx=5)
        self.sessions_var = tk.StringVar(value=str(self.settings['sessions_before_long_break']))
        ttk.Entry(settings_frame, textvariable=self.sessions_var).pack(fill='x', padx=5, pady=2)
        
        # Save Settings Button
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Progress Frame
        progress_frame = tk.LabelFrame(self, text="Progress", bg='#f0f0f0', font=('Arial', 12))
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Session 0/4",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.progress_label.pack(pady=5)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Arial', 12))
        
        # Bind window close event to hide instead of destroy
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        
        self.update_progress_display()
        
    def load_settings(self):
        try:
            if os.path.exists('pomodoro_settings.json'):
                with open('pomodoro_settings.json', 'r') as f:
                    self.settings.update(json.load(f))
        except:
            pass
    
    def save_settings(self):
        try:
            self.settings['work_time'] = int(self.work_time_var.get())
            self.settings['break_time'] = int(self.break_time_var.get())
            self.settings['long_break_time'] = int(self.long_break_var.get())
            self.settings['sessions_before_long_break'] = int(self.sessions_var.get())
            
            with open('pomodoro_settings.json', 'w') as f:
                json.dump(self.settings, f)
            
            self.reset_pomodoro()
            messagebox.showinfo("Success", "Settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all settings.")
    
    def toggle_pomodoro(self):
        if not self.pomodoro_active:
            self.pomodoro_active = True
            self.start_btn.config(text="Pause")
            if not self.remaining_time:
                self.remaining_time = self.settings['work_time'] * 60
            self.update_pomodoro()
        else:
            self.pomodoro_active = False
            self.start_btn.config(text="Resume" if self.remaining_time else "Start")
    
    def reset_pomodoro(self):
        self.pomodoro_active = False
        self.is_break = False
        self.remaining_time = self.settings['work_time'] * 60
        self.start_btn.config(text="Start")
        self.session_label.config(text="Work Time")
        self.update_pomodoro_display()
    
    def update_pomodoro(self):
        if self.pomodoro_active and self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_pomodoro_display()
            self.after(1000, self.update_pomodoro)
        elif self.pomodoro_active:
            self.handle_pomodoro_completion()
    
    def handle_pomodoro_completion(self):
        if not self.is_break:
            self.current_session += 1
            if self.current_session >= self.settings['sessions_before_long_break']:
                self.remaining_time = self.settings['long_break_time'] * 60
                self.current_session = 0
                self.session_label.config(text="Long Break")
                messagebox.showinfo("Pomodoro", "Time for a long break!")
            else:
                self.remaining_time = self.settings['break_time'] * 60
                self.session_label.config(text="Short Break")
                messagebox.showinfo("Pomodoro", "Time for a break!")
            self.is_break = True
        else:
            self.remaining_time = self.settings['work_time'] * 60
            self.is_break = False
            self.session_label.config(text="Work Time")
            messagebox.showinfo("Pomodoro", "Break's over! Time to work!")
        
        self.pomodoro_active = False
        self.start_btn.config(text="Start")
        self.update_pomodoro_display()
        self.update_progress_display()
    
    def update_pomodoro_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.pomodoro_label.config(
            text=f"{minutes:02d}:{seconds:02d}",
            fg='#666666' if self.is_break else '#333333'
        )
    
    def update_progress_display(self):
        self.progress_label.config(
            text=f"Session {self.current_session}/{self.settings['sessions_before_long_break']}"
        )

class AnxietyFriendlyClock(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gentle Digital Clock")
        self.geometry("400x300")
        self.configure(bg='#f0f0f0')
        
        self.show_numbers = True
        
        # Create frame for the clock
        self.clock_frame = tk.Frame(self, bg='#f0f0f0')
        self.clock_frame.pack(expand=True)
        
        # Day label
        self.day_label = tk.Label(
            self.clock_frame,
            font=('Arial', 24),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.day_label.pack(pady=5)
        
        # Date label
        self.date_label = tk.Label(
            self.clock_frame,
            font=('Arial', 20),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.date_label.pack(pady=5)
        
        # Time label
        self.time_label = tk.Label(
            self.clock_frame,
            font=('Arial', 48),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.time_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(self, bg='#f0f0f0')
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        # Toggle button for clock
        self.toggle_btn = ttk.Button(
            buttons_frame,
            text="Hide All",
            command=self.toggle_numbers
        )
        self.toggle_btn.pack(side='left', padx=5, expand=True)
        
        # Pomodoro button
        self.pomodoro_btn = ttk.Button(
            buttons_frame,
            text="Pomodoro",
            command=self.toggle_pomodoro
        )
        self.pomodoro_btn.pack(side='left', padx=5, expand=True)
        
        # Create Pomodoro window (hidden initially)
        self.pomodoro_window = PomodoroWindow(self)
        self.pomodoro_window.withdraw()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Arial', 12))
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Bind window close event
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        self.update_clock()
    
    def toggle_pomodoro(self):
        if self.pomodoro_window.winfo_viewable():
            self.pomodoro_window.withdraw()
            self.pomodoro_btn.config(text="Pomodoro")
        else:
            self.pomodoro_window.deiconify()
            self.pomodoro_btn.config(text="Hide Pomodoro")
    
    def create_tray_icon(self):
        # Create a simple square icon
        icon_size = 64
        icon_image = Image.new('RGB', (icon_size, icon_size), color='white')
        draw = ImageDraw.Draw(icon_image)
        draw.ellipse([8, 8, icon_size-8, icon_size-8], fill='#666666')
        
        menu = (
            pystray.MenuItem("Show/Hide Clock", self.toggle_window),
            pystray.MenuItem("Show/Hide Pomodoro", self.toggle_pomodoro),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.icon = pystray.Icon("clock", icon_image, "Gentle Clock", menu)
        Thread(target=self.icon.run, daemon=True).start()
    
    def hide_window(self):
        self.withdraw()
        
    def show_window(self):
        self.deiconify()
        
    def toggle_window(self, icon=None, item=None):
        if self.winfo_viewable():
            self.hide_window()
        else:
            self.show_window()
            self.lift()
    
    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.quit()
    
    def toggle_numbers(self):
        self.show_numbers = not self.show_numbers
        self.toggle_btn.config(text="Show All" if not self.show_numbers else "Hide All")
        self.update_clock()
        
    def update_clock(self):
        # Get current time and date
        current_time = time.localtime()
        
        # Update day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if self.show_numbers:
            current_day = days[current_time.tm_wday]
            self.day_label.config(text=current_day)
        else:
            self.day_label.config(text="•••••••")
        
        # Update date
        if self.show_numbers:
            date_str = time.strftime("%d/%m/%Y", current_time)
            self.date_label.config(text=date_str)
        else:
            self.date_label.config(text="••/••/••••")
        
        # Update time
        if self.show_numbers:
            time_str = time.strftime("%H:%M:%S", current_time)
            self.time_label.config(text=time_str)
        else:
            self.time_label.config(text="••:••:••")
        
        # Update every second
        self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = AnxietyFriendlyClock()
    app.mainloop() 
import tkinter as tk
import time
import json
import os
import psutil
import threading
import winsound

"""
Developer: Lucas Chagas Ribeiro, 2025

MIT License

Copyright (c) 2025 Lucas Chagas Ribeiro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def get_cpu_usage():
    try:
        percpu_usage = psutil.cpu_percent(percpu=True, interval=0.1)
        total_usage = sum(percpu_usage)
        normalized_usage = min(total_usage / psutil.cpu_count(), 100)
        return normalized_usage
    except Exception as e:
        print(f"Erro ao obter uso de CPU: {e}")
        return 0.0

def get_ram_usage():
    try:
        memory = psutil.virtual_memory()
        return memory.percent, memory.total / (1024.0 ** 3), memory.used / (1024.0 ** 3)
    except Exception as e:
        print(f"Erro ao obter uso de RAM: {e}")
        return 0.0, 0.0, 0.0

def get_disk_usage():
    try:
        disk_io = psutil.disk_io_counters(perdisk=True)
        
        total_read_bytes = 0
        total_write_bytes = 0
        
        for disk in disk_io.values():
            total_read_bytes += disk.read_bytes
            total_write_bytes += disk.write_bytes

        if not hasattr(get_disk_usage, 'prev_total_read_bytes'):
            get_disk_usage.prev_total_read_bytes = total_read_bytes
            get_disk_usage.prev_total_write_bytes = total_write_bytes
            return 0.0, 0.0, 0.0, 0.0
        
        read_speed = (total_read_bytes - get_disk_usage.prev_total_read_bytes) / (1024.0 ** 2)
        write_speed = (total_write_bytes - get_disk_usage.prev_total_write_bytes) / (1024.0 ** 2)
        
        get_disk_usage.prev_total_read_bytes = total_read_bytes
        get_disk_usage.prev_total_write_bytes = total_write_bytes
        
        total_disk_size = 0
        used_disk_size = 0
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            total_disk_size += usage.total
            used_disk_size += usage.used
        
        return read_speed, write_speed, used_disk_size / (1024.0 ** 3), total_disk_size / (1024.0 ** 3)
    except Exception as e:
        print(f"Erro ao obter uso de disco: {e}")
        return 0.0, 0.0, 0.0, 0.0

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="00:00:00", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.config(font="Calibri, 7")
        self.insert(0, self.placeholder)
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

    def foc_in(self, e):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(bg='#1f1f1f')

    def foc_out(self, e):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(bg='#0f0f0f')

class SystemMonitor:
    def __init__(self, update_interval=1.0):
        self.cpu_usage = 0.0
        self.ram_usage = (0.0, 0.0, 0.0)
        self.disk_usage = (0.0, 0.0, 0.0, 0.0)
        self.update_interval = update_interval
        self.running = False
        self.thread = None
    
    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        while self.running:
            self.cpu_usage = get_cpu_usage()
            self.ram_usage = get_ram_usage()
            self.disk_usage = get_disk_usage()
            time.sleep(self.update_interval)
    
    def get_metrics(self):
        return {
            'cpu': self.cpu_usage,
            'ram': self.ram_usage,
            'disk': self.disk_usage
        }

class MinimalTimer:
    def __init__(self, root):
        self.root = root
        
        self.root.overrideredirect(True)
        
        self.root.attributes("-topmost", True) 
        self.root.resizable(False, False) 
        
        self.running = False
        self.seconds = 0
        self.after_id = None
        
        self.system_monitor = SystemMonitor(update_interval=1.0)
        self.system_monitor.start_monitoring()
        
        self.cpu_var = tk.StringVar(value="CPU: 0%")
        self.ram_var = tk.StringVar(value="RAM: 0%")
        self.disk_var = tk.StringVar(value="SSD: R 0.0 MB/s, W 0.0 MB/s, 0.0/0.0 GB")
        
        self.config_file = "mini_timer_config.json"
        self.load_config()
        
        self.create_widgets()
        
        self.position_window()
        
        self.update_system_metrics()
    
    def load_config(self):
        self.config = {"x": None, "y": None, "seconds": 0}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                    self.seconds = self.config.get("seconds", 0)
            except:
                pass
    
    def save_config(self):
        self.config["x"] = self.root.winfo_x()
        self.config["y"] = self.root.winfo_y()
        self.config["seconds"] = self.seconds
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f)
        except:
            pass
    
    def create_widgets(self):
        self.frame = tk.Frame(self.root, bd=1, relief=tk.FLAT, bg="#212121")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.border_frame = tk.Frame(self.frame, bg="#000000", height=2)
        self.border_frame.pack(side=tk.TOP, fill=tk.X)

        top_frame = tk.Frame(self.frame, bg="#212121")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        
        btn_style = {
            "font": ("Calibri", 8),
            "width": 3,
            "height": 0,
            "bd": 0,
            "highlightthickness": 0,
        }

        self.time_display = tk.Label(
            top_frame, 
            text="00:00:00",
            font=("Calibri", 8), 
            bg="#212121", 
            fg="#2ed573"
        )
        self.time_display.pack(side=tk.LEFT, padx=7)
        
        self.adjust_entry = PlaceholderEntry(top_frame, placeholder="00:00:00", width=8, bg='#0f0f0f', fg='#2ed573', justify='center')
        self.adjust_entry.pack(side=tk.LEFT)

        self.add_button = tk.Button(
            top_frame, 
            text="+", 
            command=self.add_time, 
            bg="#212121", 
            fg="#2ed573", 
            **btn_style
        )
        self.add_button.pack(side=tk.LEFT, padx=1)
        self.add_button.bind("<Enter>", lambda e: e.widget.config(bg="#2ed573", fg="#000000"))
        self.add_button.bind("<Leave>", lambda e: e.widget.config(bg="#212121", fg="#2ed573"))

        self.subtract_button = tk.Button(
            top_frame, 
            text="-", 
            command=self.subtract_time, 
            bg="#212121", 
            fg="#2ed573", 
            **btn_style
        )
        self.subtract_button.pack(side=tk.LEFT, padx=1)
        self.subtract_button.bind("<Enter>", lambda e: e.widget.config(bg="#2ed573", fg="#000000"))
        self.subtract_button.bind("<Leave>", lambda e: e.widget.config(bg="#212121", fg="#2ed573"))

        btn_frame = tk.Frame(top_frame, bg="#212121")
        btn_frame.pack(side=tk.RIGHT, padx=2)
        
        self.play_pause_button = tk.Button(
            btn_frame, 
            text="▶", 
            command=self.toggle_play_pause, 
            bg="#212121", 
            fg="#00a8e8", 
            **btn_style
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=1)
        self.play_pause_button.bind("<Enter>", lambda e: e.widget.config(bg="#00a8e8", fg="#000000"))
        self.play_pause_button.bind("<Leave>", lambda e: e.widget.config(bg="#212121", fg="#00a8e8"))
        
        self.reset_button = tk.Button(
            btn_frame, 
            text="⟲", 
            command=self.reset, 
            bg="#212121", 
            fg="#ffa502", 
            **btn_style
        )
        self.reset_button.pack(side=tk.LEFT, padx=1)
        self.reset_button.bind("<Enter>", lambda e: e.widget.config(bg="#ffa502", fg="#000000"))
        self.reset_button.bind("<Leave>", lambda e: e.widget.config(bg="#212121", fg="#ffa502"))

        self.exit_button = tk.Button(
            btn_frame, 
            text="X", 
            command=self.on_close, 
            bg="#212121", 
            fg="#ff4757", 
            **btn_style
        )
        self.exit_button.pack(side=tk.LEFT, padx=1)
        self.exit_button.bind("<Enter>", lambda e: e.widget.config(bg="#ff4757", fg="#000000"))
        self.exit_button.bind("<Leave>", lambda e: e.widget.config(bg="#212121", fg="#ff4757"))

        metrics_line_two = tk.Frame(self.frame, bg="#212121")
        metrics_line_two.pack(side=tk.TOP, fill=tk.X)

        cpu_ram_frame = tk.Frame(metrics_line_two, bg="#212121")
        cpu_ram_frame.pack(side=tk.LEFT, padx=5)

        self.cpu_label = tk.Label(
            cpu_ram_frame,
            textvariable=self.cpu_var,
            font=("Calibri", 7),
            bg="#212121",
            fg="#40c4ff"  
        )
        self.cpu_label.pack(side=tk.LEFT, padx=2)

        self.ram_label = tk.Label(
            cpu_ram_frame,
            textvariable=self.ram_var,
            font=("Calibri", 7),
            bg="#212121",
            fg="#40c4ff"
        )
        self.ram_label.pack(side=tk.LEFT, padx=2)

        frame_line_three = tk.Frame(self.frame, bg="#212121")
        frame_line_three.pack(side=tk.TOP, fill=tk.X)

        disk_frame = tk.Frame(frame_line_three, bg="#212121")
        disk_frame.pack(side=tk.LEFT, padx=5)

        self.disk_label = tk.Label(
            disk_frame,
            textvariable=self.disk_var,
            font=("Calibri", 7),
            bg="#212121",
            fg="#40c4ff"
        )
        self.disk_label.pack(side=tk.LEFT, padx=2)

        for widget in (self.time_display, self.frame, top_frame, metrics_line_two, cpu_ram_frame, disk_frame, frame_line_three, self.border_frame):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)
    
    def update_system_metrics(self):
        metrics = self.system_monitor.get_metrics()
        self.cpu_var.set(f"CPU: {metrics['cpu']:.2f}%")
        ram_percent, ram_total, ram_used = metrics['ram']
        self.ram_var.set(f"RAM: {ram_percent:2.2f}% ({ram_used:.2f}/{ram_total:.2f} GB)")
        
        read_speed, write_speed, disk_used, disk_total = metrics['disk']
        self.disk_var.set(f"SSD: R {read_speed:.2f} MB/s, W {write_speed:.2f} MB/s, {disk_used:.2f}/{disk_total:.2f} GB")
        
        self.root.after(1000, self.update_system_metrics)
    
    def position_window(self):
        window_width = 230 
        window_height = 58 
        
        if self.config["x"] is not None and self.config["y"] is not None:
            x = self.config["x"]
            y = self.config["y"]
        else:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = screen_width - window_width - 10
            y = screen_height - window_height - 50 
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def update_time(self):
        if self.running:
            self.seconds -= 1
            self.time_display.config(text=self.format_time(self.seconds))
            if self.seconds <= 0:
                self.time_display.config(text="00:00:00")
                self.play_pause_button.config(text="▶")
                self.running = False
                winsound.Beep(432, 4320) 
            else:
                self.after_id = self.root.after(1000, self.update_time)
    
    def toggle_play_pause(self):
        if self.running:
            self.running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.play_pause_button.config(text="▶")
        else:
            self.running = True
            self.update_time()
            self.play_pause_button.config(text="⏸")
    
    def reset(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.seconds = 0
        self.time_display.config(text="00:00:00")
        self.play_pause_button.config(text="▶")
    
    def add_time(self):
        try:
            time_str = self.adjust_entry.get()
            if time_str == self.adjust_entry.placeholder:
                return
            h, m, s = map(int, time_str.split(':'))
            seconds_to_add = h * 3600 + m * 60 + s
            self.seconds += seconds_to_add
            self.time_display.config(text=self.format_time(self.seconds))
        except ValueError:
            print("Valor inválido")
    
    def subtract_time(self):
        try:
            time_str = self.adjust_entry.get()
            if time_str == self.adjust_entry.placeholder:
                return
            h, m, s = map(int, time_str.split(':'))
            seconds_to_subtract = h * 3600 + m * 60 + s
            self.seconds -= seconds_to_subtract
            if self.seconds < 0:
                self.seconds = 0
            self.time_display.config(text=self.format_time(self.seconds))
        except ValueError:
            print("Valor inválido")
    
    def on_close(self):
        self.system_monitor.stop_monitoring()
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinimalTimer(root)
    root.mainloop()

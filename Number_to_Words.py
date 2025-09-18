#!/usr/bin/env python3
# Number to Words Generator # 

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from pathlib import Path
import queue

class NumberToWords:
    # Convert numbers to their written word form.
    
    def __init__(self):
        self.ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        self.teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 
                     'sixteen', 'seventeen', 'eighteen', 'nineteen']
        self.tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        self.scales = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion']
    
    def convert_under_thousand(self, num: int) -> str:
        # Convert numbers under 1000 to words.
        if num == 0:
            return ''
        
        result = ''
        
        # Handle hundreds
        if num >= 100:
            result += self.ones[num // 100] + ' hundred'
            num %= 100
            if num > 0:
                result += ' '
        
        # Handle tens and ones
        if num >= 20:
            result += self.tens[num // 10]
            if num % 10 > 0:
                result += ' ' + self.ones[num % 10]
        elif num >= 10:
            result += self.teens[num - 10]
        elif num > 0:
            result += self.ones[num]
        
        return result
    
    def convert(self, num: int) -> str:
        # Convert any number to words.
        if num == 0:
            return 'zero'
        
        if num < 0:
            return 'negative ' + self.convert(-num)
        
        result = ''
        scale_index = 0
        
        while num > 0:
            chunk = num % 1000
            if chunk > 0:
                chunk_words = self.convert_under_thousand(chunk)
                if scale_index > 0:
                    chunk_words += ' ' + self.scales[scale_index]
                
                if result:
                    result = chunk_words + ' ' + result
                else:
                    result = chunk_words
            
            num //= 1000
            scale_index += 1
        
        return result

class NumberGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.converter = NumberToWords()
        self.is_generating = False
        self.generation_thread = None
        self.progress_queue = queue.Queue()
        
        self.setup_gui()
        self.check_progress_queue()
    
    def setup_gui(self):
        # Set up the GUI interface.
        self.root.title("Numbers to Words Generator")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), background='#f0f0f0')
        style.configure('Generate.TButton', font=('Arial', 10, 'bold'))
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔢 Numbers to Words Generator", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Generation Settings", padding="15")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        # End number
        ttk.Label(input_frame, text="End Number:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.end_number_var = tk.StringVar(value="1000000")
        end_number_entry = ttk.Entry(input_frame, textvariable=self.end_number_var, 
                                   font=('Courier', 11), width=20)
        end_number_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Quick select buttons
        quick_frame = ttk.Frame(input_frame)
        quick_frame.grid(row=0, column=2, sticky=tk.E)
        
        quick_values = [("1K", "1000"), ("10K", "10000"), ("100K", "100000"), 
                       ("1M", "1000000"), ("10M", "10000000")]
        
        for i, (label, value) in enumerate(quick_values):
            btn = ttk.Button(quick_frame, text=label, width=4,
                           command=lambda v=value: self.end_number_var.set(v))
            btn.grid(row=0, column=i, padx=2)
        
        # Output file
        ttk.Label(input_frame, text="Output File:", style='Header.TLabel').grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        file_frame.columnconfigure(0, weight=1)
        
        self.output_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.output_file_var, 
                              font=('Arial', 9))
        file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_output_file).grid(row=0, column=1)
        
        # Batch size
        ttk.Label(input_frame, text="Batch Size:", style='Header.TLabel').grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        self.batch_size_var = tk.StringVar(value="10000")
        batch_entry = ttk.Entry(input_frame, textvariable=self.batch_size_var, 
                               font=('Courier', 11), width=10)
        batch_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        self.generate_btn = ttk.Button(button_frame, text="🚀 Generate Numbers", 
                                     style='Generate.TButton',
                                     command=self.start_generation)
        self.generate_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop", 
                                  command=self.stop_generation, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.test_btn = ttk.Button(button_frame, text="🧪 Test Convert", 
                                  command=self.test_conversion)
        self.test_btn.grid(row=0, column=2)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="15")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_var = tk.StringVar(value="Ready to generate")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, 
                               font=('Arial', 9))
        status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Info display
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="15")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=70, 
                                                 font=('Courier', 9), wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Number Preview", padding="15")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=6, width=70, 
                                                    font=('Courier', 9), wrap=tk.WORD)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(5, weight=1)
        
        self.show_welcome_info()
    
    def show_welcome_info(self):
        # Show welcome information.
        info = """Welcome to the Numbers to Words Generator!

📊 ESTIMATED FILE SIZES:
• 1,000 numbers ≈ 25 KB
• 10,000 numbers ≈ 250 KB  
• 100,000 numbers ≈ 2.5 MB
• 1,000,000 numbers ≈ 25 MB
• 10,000,000 numbers ≈ 250 MB

⚡ PERFORMANCE TIPS:
• Use larger batch sizes (50,000+) for better performance on large ranges
• Generation speed: ~100,000 numbers per minute on modern hardware
• Files are saved incrementally, so you can stop and resume

🎯 QUICK START:
1. Choose an end number (or use quick select buttons)
2. Optionally select an output file location
3. Click 'Generate Numbers' to start
4. Use 'Test Convert' to try individual number conversions

The output file will contain one number per line written in words:
one
two
three
...
"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
    
    def browse_output_file(self):
        # Open file dialog to select output file.
        try:
            end_num = int(self.end_number_var.get().replace(',', ''))
            default_name = f"numbers_1_to_{end_num:,}_longhand.txt".replace(',', '_')
        except ValueError:
            default_name = "numbers_longhand.txt"
        
        filename = filedialog.asksaveasfilename(
            title="Save output as…",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_name,          # <-- was 'initialvalue', use 'initialfile'
            initialdir=os.path.expanduser("~/Desktop"),  # optional, pick a sensible default
            confirmoverwrite=True              # optional, prompts if file exists
        )

        
        if filename:
            self.output_file_var.set(filename)
    
    def test_conversion(self):
        # Test number conversion with user input.
        def convert_and_show():
            try:
                test_num = int(test_entry.get().replace(',', ''))
                if test_num < 0 or test_num > 999999999999999:
                    result_label.config(text="Number out of range (0 to 999 quadrillion)")
                    return
                
                words = self.converter.convert(test_num)
                result_label.config(text=f"{test_num:,} = {words}")
                
                # Also show in preview
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, f"Test conversion:\n{test_num:,}: {words}\n\n")
                
                # Show some context numbers
                context = []
                for offset in [-2, -1, 1, 2]:
                    if test_num + offset > 0:
                        context_words = self.converter.convert(test_num + offset)
                        context.append(f"{test_num + offset:,}: {context_words}")
                
                if context:
                    self.preview_text.insert(tk.END, "Nearby numbers:\n" + "\n".join(context))
                
            except ValueError:
                result_label.config(text="Please enter a valid number")
        
        # Create test window
        test_window = tk.Toplevel(self.root)
        test_window.title("Test Number Conversion")
        test_window.geometry("500x200")
        test_window.configure(bg='#f0f0f0')
        
        frame = ttk.Frame(test_window, padding="20")
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text="Enter a number to convert:", font=('Arial', 10, 'bold')).pack(pady=(0, 10))
        
        test_entry = ttk.Entry(frame, font=('Courier', 11), width=30)
        test_entry.pack(pady=(0, 10))
        test_entry.insert(0, "12345")
        test_entry.focus()
        
        ttk.Button(frame, text="Convert", command=convert_and_show).pack(pady=(0, 15))
        
        result_label = ttk.Label(frame, text="", font=('Arial', 9), wraplength=450)
        result_label.pack()
        
        test_entry.bind('<Return>', lambda e: convert_and_show())
    
    def start_generation(self):
        # Start the number generation in a separate thread.
        if self.is_generating:
            return
        
        try:
            end_number = int(self.end_number_var.get().replace(',', ''))
            batch_size = int(self.batch_size_var.get().replace(',', ''))
            
            if end_number < 1 or end_number > 999999999999999:
                messagebox.showerror("Error", "End number must be between 1 and 999,999,999,999,999")
                return
            
            if batch_size < 1:
                messagebox.showerror("Error", "Batch size must be positive")
                return
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        
        # Determine output file
        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = f"numbers_1_to_{end_number:,}_longhand.txt".replace(',', '_')
            self.output_file_var.set(output_file)
        
        # Estimate file size and warn if large
        avg_chars = self.estimate_avg_chars(end_number)
        estimated_mb = (end_number * avg_chars) / (1024 * 1024)
        
        if estimated_mb > 1000:  # > 1GB
            result = messagebox.askyesno(
                "Large File Warning", 
                f"Estimated file size: {estimated_mb:.1f} MB\n"
                f"This may take a long time and use significant disk space.\n\n"
                f"Continue with generation?"
            )
            if not result:
                return
        
        # Start generation
        self.is_generating = True
        self.generate_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.generation_thread = threading.Thread(
            target=self.generate_numbers_thread,
            args=(end_number, output_file, batch_size),
            daemon=True
        )
        self.generation_thread.start()
    
    def generate_numbers_thread(self, end_number, output_file, batch_size):
        # Generate numbers in a separate thread.
        try:
            start_time = time.time()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                batch = []
                
                for i in range(1, end_number + 1):
                    if not self.is_generating:  # Check for stop
                        break
                    
                    words = self.converter.convert(i)
                    batch.append(words + '\n')
                    
                    # Write batch to file
                    if len(batch) >= batch_size:
                        f.writelines(batch)
                        batch = []
                        
                        # Update progress
                        progress = (i / end_number) * 100
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 0
                        eta = (end_number - i) / rate if rate > 0 else 0
                        
                        self.progress_queue.put({
                            'progress': progress,
                            'status': f"Generated {i:,} / {end_number:,} ({progress:.1f}%) - "
                                    f"{rate:.0f} numbers/sec - ETA: {eta:.0f}s",
                            'preview': '\n'.join(batch[-10:]) if batch else words
                        })
                
                # Write remaining batch
                if batch and self.is_generating:
                    f.writelines(batch)
            
            # Final update
            if self.is_generating:
                elapsed = time.time() - start_time
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                
                self.progress_queue.put({
                    'complete': True,
                    'progress': 100,
                    'status': f"Complete! Generated {end_number:,} numbers in {elapsed:.1f}s "
                            f"({file_size:.1f} MB)",
                    'info': f"✅ GENERATION COMPLETE!\n\n"
                           f"Numbers generated: {end_number:,}\n"
                           f"Output file: {output_file}\n"
                           f"File size: {file_size:.1f} MB\n"
                           f"Generation time: {elapsed:.1f} seconds\n"
                           f"Average rate: {end_number/elapsed:.0f} numbers/second\n\n"
                           f"The file contains one number per line written in words."
                })
            
        except Exception as e:
            self.progress_queue.put({
                'error': True,
                'status': f"Error: {str(e)}",
                'info': f"❌ ERROR OCCURRED:\n\n{str(e)}\n\nGeneration stopped."
            })
        
        finally:
            self.progress_queue.put({'finished': True})
    
    def stop_generation(self):
        # Stop the generation process.
        self.is_generating = False
        self.status_var.set("Stopping generation...")
    
    def check_progress_queue(self):
        # Check for progress updates from the generation thread.
        try:
            while True:
                update = self.progress_queue.get_nowait()
                
                if 'progress' in update:
                    self.progress_var.set(update['progress'])
                
                if 'status' in update:
                    self.status_var.set(update['status'])
                
                if 'preview' in update:
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, f"Recent numbers:\n{update['preview']}")
                
                if 'info' in update:
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, update['info'])
                
                if 'complete' in update:
                    messagebox.showinfo("Generation Complete", "Numbers generated successfully!")
                
                if 'error' in update:
                    messagebox.showerror("Generation Error", update['status'])
                
                if 'finished' in update:
                    self.is_generating = False
                    self.generate_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)
    
    def estimate_avg_chars(self, end_number):
        # Estimate average characters per number.
        if end_number <= 100:
            return 8
        elif end_number <= 1000:
            return 25
        elif end_number <= 1000000:
            return 45
        elif end_number <= 1000000000:
            return 65
        else:
            return 85

def main():
    # Main function to run the GUI application.
    root = tk.Tk()
    app = NumberGeneratorGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == '__main__':
    main()

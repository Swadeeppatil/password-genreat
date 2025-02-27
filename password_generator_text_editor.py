import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from tkinter.font import Font
import random
import string
import pyperclip
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Password Generator & Text Editor")
        self.geometry("800x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.password_tab = PasswordGenerator(self.notebook)
        self.editor_tab = TextEditor(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.password_tab, text='Password Generator')
        self.notebook.add(self.editor_tab, text='Text Editor')

class PasswordGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        
    def create_widgets(self):
        # Password Length
        length_frame = ttk.LabelFrame(self, text="Password Length", padding=10)
        length_frame.pack(fill='x', padx=10, pady=5)
        
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(
            length_frame, 
            from_=8, 
            to=32, 
            orient='horizontal',
            variable=self.length_var
        )
        self.length_scale.pack(fill='x')
        
        # Character Options
        options_frame = ttk.LabelFrame(self, text="Character Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Uppercase", variable=self.uppercase_var).pack(anchor='w')
        ttk.Checkbutton(options_frame, text="Lowercase", variable=self.lowercase_var).pack(anchor='w')
        ttk.Checkbutton(options_frame, text="Numbers", variable=self.numbers_var).pack(anchor='w')
        ttk.Checkbutton(options_frame, text="Special Characters", variable=self.special_var).pack(anchor='w')
        
        # Password Display
        display_frame = ttk.LabelFrame(self, text="Generated Password", padding=10)
        display_frame.pack(fill='x', padx=10, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            display_frame, 
            textvariable=self.password_var, 
            state='readonly',
            font=('Courier', 12)
        )
        self.password_entry.pack(fill='x', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Generate", command=self.generate_password).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Copy", command=self.copy_password).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_password).pack(side='left', padx=5)
        
        # Strength Indicator
        self.strength_var = tk.StringVar(value="Strength: N/A")
        ttk.Label(self, textvariable=self.strength_var).pack(pady=5)
        
    def generate_password(self):
        chars = ''
        if self.uppercase_var.get(): chars += string.ascii_uppercase
        if self.lowercase_var.get(): chars += string.ascii_lowercase
        if self.numbers_var.get(): chars += string.digits
        if self.special_var.get(): chars += string.punctuation
        
        if not chars:
            messagebox.showwarning("Warning", "Please select at least one character type!")
            return
            
        length = self.length_var.get()
        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)
        self.update_strength()
        
    def copy_password(self):
        if self.password_var.get():
            pyperclip.copy(self.password_var.get())
            messagebox.showinfo("Success", "Password copied to clipboard!")
            
    def clear_password(self):
        self.password_var.set("")
        self.strength_var.set("Strength: N/A")
        
    def update_strength(self):
        password = self.password_var.get()
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        strength = sum([has_upper, has_lower, has_digit, has_special])
        
        if length < 8:
            strength_text = "Weak"
        elif length < 12:
            strength_text = "Medium" if strength >= 3 else "Weak"
        else:
            strength_text = "Strong" if strength >= 3 else "Medium"
            
        self.strength_var.set(f"Strength: {strength_text}")

class TextEditor(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.filename = None
        self.create_widgets()
        
    def create_widgets(self):
        # Text widget with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.text_widget = tk.Text(text_frame, wrap='word', undo=True)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.text_widget.pack(expand=True, fill='both')

        # Create main menu
        self.create_menu()
        
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=2)
        
        # Font selection
        self.font_family = tk.StringVar(value='Arial')
        self.font_size = tk.IntVar(value=12)
        
        font_families = ['Arial', 'Times New Roman', 'Courier New', 'Helvetica']
        ttk.Combobox(toolbar, textvariable=self.font_family, values=font_families, width=15).pack(side='left', padx=2)
        ttk.Spinbox(toolbar, from_=8, to=72, width=5, textvariable=self.font_size).pack(side='left', padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var).pack(fill='x', padx=5)
        
        # Bind events
        self.text_widget.bind('<<Modified>>', self.update_status)
        self.text_widget.bind('<KeyRelease>', self.update_status)
        
    def create_menu(self):
        menubar = tk.Menu(self)
        self.master.master.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.text_widget.event_generate('<<Cut>>'))
        edit_menu.add_command(label="Copy", command=lambda: self.text_widget.event_generate('<<Copy>>'))
        edit_menu.add_command(label="Paste", command=lambda: self.text_widget.event_generate('<<Paste>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.text_widget.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_widget.edit_redo)
        
    def new_file(self):
        self.text_widget.delete(1.0, tk.END)
        self.filename = None
        self.update_status()
        
    def open_file(self):
        filetypes = [('Text Files', '*.txt'), ('All Files', '*.*')]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                with open(filename, 'r') as file:
                    self.text_widget.delete(1.0, tk.END)
                    self.text_widget.insert(1.0, file.read())
                self.filename = filename
                self.update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def save_file(self):
        if not self.filename:
            self.save_as()
        else:
            try:
                content = self.text_widget.get(1.0, tk.END)
                with open(self.filename, 'w') as file:
                    file.write(content)
                self.update_status("File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                
    def save_as(self):
        filetypes = [('Text Files', '*.txt'), ('All Files', '*.*')]
        filename = filedialog.asksaveasfilename(filetypes=filetypes)
        if filename:
            self.filename = filename
            self.save_file()
            
    def update_status(self, event=None):
        if isinstance(event, str):
            self.status_var.set(event)
        else:
            content = self.text_widget.get(1.0, tk.END)
            words = len(content.split())
            chars = len(content) - 1  # Subtract 1 to account for the extra newline
            self.status_var.set(f"Words: {words} | Characters: {chars}")
            
            if self.filename:
                self.status_var.set(f"{self.filename} | {self.status_var.get()}")

if __name__ == "__main__":
    app = App()
    app.mainloop()

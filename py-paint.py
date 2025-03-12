import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog, font
from PIL import Image, ImageDraw

class MSPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("MS Paint Clone")

        # Default settings
        self.brush_color = "black"
        self.bg_color = "white"
        self.brush_size = 5
        self.eraser_mode = False
        self.tool = "brush"
        self.start_x, self.start_y = None, None
        self.font_name = "Arial"
        self.font_size = 20

        # Canvas setup
        self.canvas = tk.Canvas(root, bg=self.bg_color, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create an image for drawing
        self.image = Image.new("RGB", (800, 500), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        # Fullscreen toggle
        self.root.bind("<F11>", self.toggle_fullscreen)

        # Toolbar
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(fill=tk.X)
        self.create_tool_buttons()

    def create_tool_buttons(self):
        """Create all tool buttons"""
        buttons = [
            ("Brush", lambda: self.select_tool("brush")),
            ("Eraser", lambda: self.select_tool("eraser")),
            ("Line", lambda: self.select_tool("line")),
            ("Rectangle", lambda: self.select_tool("rectangle")),
            ("Oval", lambda: self.select_tool("oval")),
            ("Text", lambda: self.select_tool("text")),
            ("Color", self.choose_color),
            ("Clear", self.clear_canvas),
            ("Save", self.save_image),
            ("Load", self.load_image)
        ]
        for text, command in buttons:
            tk.Button(self.toolbar, text=text, command=command).pack(side=tk.LEFT, padx=5)

        # Brush Size
        tk.Label(self.toolbar, text="Size:").pack(side=tk.LEFT)
        self.brush_size_slider = tk.Scale(self.toolbar, from_=1, to=20, orient=tk.HORIZONTAL)
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.pack(side=tk.LEFT)

        # Font Selection
        tk.Label(self.toolbar, text="Font:").pack(side=tk.LEFT)
        self.font_menu = tk.StringVar(value=self.font_name)
        font_dropdown = tk.OptionMenu(self.toolbar, self.font_menu, "Arial", "Times", "Courier", command=self.set_font)
        font_dropdown.pack(side=tk.LEFT)

        tk.Label(self.toolbar, text="Size:").pack(side=tk.LEFT)
        self.font_size_slider = tk.Scale(self.toolbar, from_=10, to=50, orient=tk.HORIZONTAL)
        self.font_size_slider.set(self.font_size)
        self.font_size_slider.pack(side=tk.LEFT)

    def paint(self, event):
        """Handles freehand drawing"""
        if self.tool == "brush":
            x, y = event.x, event.y
            color = "white" if self.eraser_mode else self.brush_color
            size = self.brush_size_slider.get()
            self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline=color)
            self.draw.ellipse([x-size, y-size, x+size, y+size], fill=color, outline=color)

    def start_draw(self, event):
        """Handles the starting point of shapes and text tool"""
        self.start_x, self.start_y = event.x, event.y
        if self.tool == "text":
            self.add_text(event.x, event.y)

    def end_draw(self, event):
        """Handles shape drawing on canvas"""
        x, y = event.x, event.y
        if self.start_x and self.start_y:
            color = self.brush_color if not self.eraser_mode else "white"
            width = self.brush_size_slider.get()
            if self.tool == "line":
                self.canvas.create_line(self.start_x, self.start_y, x, y, fill=color, width=width)
                self.draw.line([self.start_x, self.start_y, x, y], fill=color, width=width)
            elif self.tool == "rectangle":
                self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline=color, width=width)
                self.draw.rectangle([self.start_x, self.start_y, x, y], outline=color, width=width)
            elif self.tool == "oval":
                self.canvas.create_oval(self.start_x, self.start_y, x, y, outline=color, width=width)
                self.draw.ellipse([self.start_x, self.start_y, x, y], outline=color, width=width)
        self.start_x, self.start_y = None, None

    def choose_color(self):
        """Opens color picker"""
        color = colorchooser.askcolor()[1]
        if color:
            self.brush_color = color
            self.eraser_mode = False

    def select_tool(self, tool):
        """Sets the active tool"""
        self.tool = tool
        self.eraser_mode = (tool == "eraser")

    def add_text(self, x, y):
        """Adds text to the canvas at a specific position"""
        text = simpledialog.askstring("Text Tool", "Enter text:")
        if text:
            font_tuple = (self.font_name, self.font_size_slider.get())
            self.canvas.create_text(x, y, text=text, fill=self.brush_color, font=font_tuple)
            
            # Draw text on the PIL image
            img_font = font.Font(family=self.font_name, size=self.font_size_slider.get())
            self.draw.text((x, y), text, fill=self.brush_color, font=img_font)

    def set_font(self, font_name):
        """Updates the font selection"""
        self.font_name = font_name

    def clear_canvas(self):
        """Clears the canvas"""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (800, 500), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self):
        """Saves the canvas as an image"""
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("All Files", "*.*")])
        if file_path:
            self.image.save(file_path)

    def load_image(self):
        """Loads an image onto the canvas"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            img = Image.open(file_path)
            img = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.image = img
            self.draw = ImageDraw.Draw(self.image)
            self.canvas.img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.img)

    def toggle_fullscreen(self, event=None):
        """Toggles fullscreen mode without glitches"""
        state = not self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", state)
        if not state:
            self.root.geometry("800x600")  # Reset window size when exiting fullscreen

# Run the application
root = tk.Tk()
app = MSPaint(root)
root.mainloop()

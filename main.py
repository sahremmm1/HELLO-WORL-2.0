import ctypes
import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk
import random

def set_english_layout():
    # Переключение раскладки на английский (Windows)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    layout_id = 0x409  # английский (США)
    ctypes.windll.user32.LoadKeyboardLayoutW(f'{layout_id:08X}', 1)

# Вызов функции при запуске
set_english_layout()

class TurtleGame:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-fullscreen', True)
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.cell_size = 40
        self.cols = self.screen_width // self.cell_size
        self.rows = self.screen_height // self.cell_size
        self.canvas = tk.Canvas(self.master, width=self.screen_width, height=self.screen_height, bg='#000080')
        self.canvas.pack()

        self.key_state = {}
        self.master.bind('<KeyPress>', self.on_key_press)
        self.master.bind('<KeyRelease>', self.on_key_release)
        self.master.bind('<FocusIn>', lambda e: self.master.focus_set())

        # Показываем окно выбора карты по центру
        self.show_generation_choice()

    def on_key_press(self, event):
        self.key_state[event.keycode] = True
        self.process_movement()

    def on_key_release(self, event):
        self.key_state[event.keycode] = False

    def process_movement(self):
        if hasattr(self, 'game_over') and self.game_over:
            return
        move_commands = {
            87: (-1, 0),  # W
            65: (0, -1),  # A
            83: (1, 0),   # S
            68: (0, 1),   # D
            38: (-1, 0),  # стрелка вверх
            40: (1, 0),   # стрелка вниз
            37: (0, -1),  # стрелка влево
            39: (0, 1),   # стрелка вправо
        }

        for keycode, delta in move_commands.items():
            if self.key_state.get(keycode, False):
                self.update_position(delta[0], delta[1])
                break

    def show_generation_choice(self):
        self.choice_window = Toplevel(self.master)
        self.choice_window.title("Выберите генерацию блоков")
        width = 500
        height = 200
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.choice_window.geometry(f"{width}x{height}+{x}+{y}")
        self.choice_window.grab_set()

        label = tk.Label(self.choice_window, text="Выберите тип генерации блоков:")
        label.pack(pady=10)

        options = [
            ("Случайная", "random"),
            ("Горизонтальная симметрия", "sym_horizontal"),
            ("Вертикальная симметрия", "sym_vertical"),
            ("Лабиринт", "maze")
        ]

        self.gen_type = tk.StringVar(value="random")
        for text, mode in options:
            tk.Radiobutton(self.choice_window, text=text, variable=self.gen_type, value=mode).pack(anchor='w', padx=20)

        start_btn = tk.Button(self.choice_window, text="Начать игру", command=self.start_game)
        start_btn.pack(pady=10)

    def start_game(self):
        self.choice_window.destroy()
        self.generate_blocks()
        self.load_images()
        self.reset_positions()
        self.draw_field()
        self.master.after(3000, self.start_ghost_movement)

    def generate_blocks(self):
        self.blocks = set()
        total_blocks = int(self.rows * self.cols * 0.1)

        if self.gen_type.get() == "random":
            for _ in range(total_blocks):
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols - 1)
                self.blocks.add((r, c))
        elif self.gen_type.get() == "sym_horizontal":
            temp_blocks = set()
            for _ in range(total_blocks // 2):
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols // 2)
                temp_blocks.add((r, c))
            for (r, c) in temp_blocks:
                self.blocks.add((r, c))
                self.blocks.add((r, self.cols - 1 - c))
        elif self.gen_type.get() == "sym_vertical":
            temp_blocks = set()
            for _ in range(total_blocks // 2):
                r = random.randint(0, self.rows // 2)
                c = random.randint(0, self.cols - 1)
                temp_blocks.add((r, c))
            for (r, c) in temp_blocks:
                self.blocks.add((r, c))
                self.blocks.add((self.rows - 1 - r, c))
        elif self.gen_type.get() == "maze":
            for r in range(self.rows):
                for c in range(self.cols):
                    if r in [0, self.rows -1] or c in [0, self.cols -1]:
                        self.blocks.add((r, c))
            for _ in range(int(self.rows * self.cols * 0.2)):
                r = random.randint(1, self.rows - 2)
                c = random.randint(1, self.cols - 2)
                self.blocks.add((r, c))

    def load_images(self):
        try:
            self.person_image = Image.open("Photo.jpg")
        except:
            self.person_image = Image.new('RGB', (self.cell_size, self.cell_size), color='yellow')
        self.person_image = self.person_image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        self.person_tk = ImageTk.PhotoImage(self.person_image)

        try:
            ghost_img = Image.open("ghost.jpg")
            ghost_img = ghost_img.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
            self.ghost_tk = ImageTk.PhotoImage(ghost_img)
        except:
            self.ghost_tk = ImageTk.PhotoImage(Image.new('RGB', (self.cell_size, self.cell_size), color='red'))

    def reset_positions(self):
        self.pos = [self.rows // 2, self.cols // 2]
        self.ghost_pos = [random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)]
        while self.ghost_pos == self.pos or tuple(self.ghost_pos) in self.blocks:
            self.ghost_pos = [random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)]

    def draw_field(self):
        self.canvas.delete("all")
        for (r, c) in self.blocks:
            x1, y1 = c * self.cell_size, r * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='blue')
        x_g = self.ghost_pos[1] * self.cell_size + self.cell_size // 2
        y_g = self.ghost_pos[0] * self.cell_size + self.cell_size // 2
        if hasattr(self, 'ghost_id'):
            self.canvas.delete(self.ghost_id)
        self.ghost_id = self.canvas.create_image(x_g, y_g, image=self.ghost_tk)
        self.draw_person()

    def draw_person(self):
        if hasattr(self, 'image_id'):
            self.canvas.delete(self.image_id)
        x = self.pos[1] * self.cell_size + self.cell_size // 2
        y = self.pos[0] * self.cell_size + self.cell_size // 2
        self.image_id = self.canvas.create_image(x, y, image=self.person_tk)

    def update_position(self, delta_r, delta_c):
        if hasattr(self, 'game_over') and self.game_over:
            return
        new_r = self.pos[0] + delta_r
        new_c = self.pos[1] + delta_c
        if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
            if (new_r, new_c) not in self.blocks:
                self.pos = [new_r, new_c]
                self.draw_person()
                self.check_collision()

    def start_ghost_movement(self):
        self.move_ghost()

    def move_ghost(self):
        if hasattr(self, 'game_over') and self.game_over:
            return
        dr = self.pos[0] - self.ghost_pos[0]
        dc = self.pos[1] - self.ghost_pos[1]
        move_r = 0
        move_c = 0
        if dr != 0:
            move_r = 1 if dr > 0 else -1
        if dc != 0:
            move_c = 1 if dc > 0 else -1
        new_r = self.ghost_pos[0] + move_r
        new_c = self.ghost_pos[1] + move_c
        if (0 <= new_r < self.rows and 0 <= new_c < self.cols and
            (new_r, new_c) not in self.blocks):
            self.ghost_pos = [new_r, new_c]
        self.draw_field()
        self.check_collision()
        if not hasattr(self, 'game_over') or not self.game_over:
            self.master.after(300, self.move_ghost)

    def check_collision(self):
        if self.pos == self.ghost_pos:
            self.game_over = True
            self.show_end_screen()

    def show_end_screen(self):
        end_window = Toplevel(self.master)
        end_window.title("Конец игры")
        end_window.geometry("400x200")
        end_window.grab_set()

        label = tk.Label(end_window, text="Любовь Александровна вас поймала. Быстро делать дз!", wraplength=380)
        label.pack(pady=10)

        button_frame = tk.Frame(end_window)
        button_frame.pack(pady=10)

        restart_btn = tk.Button(button_frame, text="Начать заново", command=lambda: [end_window.destroy(), self.reset_game(), self.start_ghost_movement()])
        restart_btn.pack(side=tk.LEFT, padx=5)

        exit_btn = tk.Button(button_frame, text="Выход", command=self.master.destroy)
        exit_btn.pack(side=tk.LEFT, padx=5)

    def reset_game(self):
        self.game_over = False
        self.load_images()
        self.generate_blocks()
        self.reset_positions()
        self.draw_field()

if __name__ == "__main__":
    root = tk.Tk()
    game = TurtleGame(root)
    root.mainloop()
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import random

class TurtleGame:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-fullscreen', True)
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        # Запрос размера поля
        self.field_size = simpledialog.askinteger("Размер поля", "Введите размер поля (например, 20):", minvalue=10, maxvalue=100)
        if not self.field_size:
            self.field_size = 20

        # Создаем холст на весь экран
        self.canvas = tk.Canvas(self.master, width=self.screen_width, height=self.screen_height, bg='#000080')
        self.canvas.pack()

        # Размер ячейки под размер экрана
        self.cell_size = min(self.screen_width, self.screen_height) // self.field_size

        # Загружаем изображение человека
        try:
            self.person_image = Image.open("Photo.jpg")
        except:
            self.person_image = Image.new('RGB', (self.cell_size, self.cell_size), color='yellow')
        self.person_image = self.person_image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        self.person_tk = ImageTk.PhotoImage(self.person_image)

        # Путь к изображению призрака
        ghost_image_path = "ghost.jpg"  # <-- замените на свой путь
        try:
            ghost_img = Image.open(ghost_image_path)
            ghost_img = ghost_img.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
            self.ghost_tk = ImageTk.PhotoImage(ghost_img)
        except:
            self.ghost_tk = ImageTk.PhotoImage(
                Image.new('RGB', (self.cell_size, self.cell_size), color='red')
            )

        # Создаем блоки (стены)
        self.blocks = []
        for _ in range(int(self.field_size**2 * 0.1)):
            r = random.randint(0, self.field_size - 1)
            c = random.randint(0, self.field_size - 1)
            self.blocks.append((r, c))

        # Начальная позиция игрока
        self.pos = [self.field_size // 2, self.field_size // 2]
        # Позиция призрака
        self.ghost_pos = [random.randint(0, self.field_size - 1), random.randint(0, self.field_size - 1)]
        while tuple(self.ghost_pos) in self.blocks:
            self.ghost_pos = [random.randint(0, self.field_size - 1), random.randint(0, self.field_size - 1)]

        self.game_over = False

        # Изначально рисуем поле
        self.draw_field()

        # Управление
        self.master.bind('<Up>', self.move_up)
        self.master.bind('<Down>', self.move_down)
        self.master.bind('<Left>', self.move_left)
        self.master.bind('<Right>', self.move_right)
        self.master.bind('w', self.move_up)
        self.master.bind('s', self.move_down)
        self.master.bind('a', self.move_left)
        self.master.bind('d', self.move_right)

        # Запускаем задержку перед движением призрака
        self.master.after(3000, self.start_ghost_movement)

    def draw_field(self):
        self.canvas.delete("all")
        for (r, c) in self.blocks:
            x1 = c * self.cell_size
            y1 = r * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='blue')

        if self.ghost_tk:
            x = self.ghost_pos[1] * self.cell_size + self.cell_size // 2
            y = self.ghost_pos[0] * self.cell_size + self.cell_size // 2
            if hasattr(self, 'ghost_id'):
                self.canvas.delete(self.ghost_id)
            self.ghost_id = self.canvas.create_image(x, y, image=self.ghost_tk)

        self.draw_person()

    def draw_person(self):
        if hasattr(self, 'image_id'):
            self.canvas.delete(self.image_id)
        x = self.pos[1] * self.cell_size + self.cell_size // 2
        y = self.pos[0] * self.cell_size + self.cell_size // 2
        self.image_id = self.canvas.create_image(x, y, image=self.person_tk)

    def move_up(self, event):
        self.update_position(-1, 0)

    def move_down(self, event):
        self.update_position(1, 0)

    def move_left(self, event):
        self.update_position(0, -1)

    def move_right(self, event):
        self.update_position(0, 1)

    def update_position(self, delta_row, delta_col):
        if self.game_over:
            return
        new_row = self.pos[0] + delta_row
        new_col = self.pos[1] + delta_col
        if 0 <= new_row < self.field_size and 0 <= new_col < self.field_size:
            if (new_row, new_col) not in self.blocks:
                self.pos = [new_row, new_col]
                self.draw_person()
                self.check_collision()

    def start_ghost_movement(self):
        self.move_ghost()

    def move_ghost(self):
        if self.game_over:
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

        if (0 <= new_r < self.field_size and 0 <= new_c < self.field_size and
            (new_r, new_c) not in self.blocks):
            self.ghost_pos = [new_r, new_c]

        self.draw_field()
        self.check_collision()

        if not self.game_over:
            # Запуск следующего хода с интервалом 0.3 секунды
            self.master.after(300, self.move_ghost)

    def check_collision(self):
        if self.pos == self.ghost_pos:
            self.game_over = True
            messagebox.showinfo("Конец игры", "Призрак поймал вас! Игра окончена.")

if __name__ == "__main__":
    root = tk.Tk()
    game = TurtleGame(root)
    root.mainloop()
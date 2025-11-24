import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

class TurtleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Игра про человека")

        # Запрос размера поля у пользователя
        self.field_size = simpledialog.askinteger("Размер поля", "Введите размер поля (например, 20):", minvalue=10,
                                                  maxvalue=100)
        if not self.field_size:
            self.field_size = 20  # Значение по умолчанию

        # Создаем холст
        self.canvas_size = 400
        self.cell_size = self.canvas_size // self.field_size
        self.canvas = tk.Canvas(self.master, width=self.canvas_size, height=self.canvas_size, bg='white')
        self.canvas.pack()

        # Загружаем изображение человека
        self.person_image = Image.open("Photo.jpg")  # Укажите путь к вашему изображению
        # Обновленная строка с ресемплированием
        self.person_image = self.person_image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        self.person_tk = ImageTk.PhotoImage(self.person_image)

        # Начальная позиция человека
        self.pos = [self.field_size // 2, self.field_size // 2]
        self.image_id = None

        # Рисуем человека
        self.draw_person()

        # Назначаем управление стрелочками
        self.master.bind('<Up>', self.move_up)
        self.master.bind('<Down>', self.move_down)
        self.master.bind('<Left>', self.move_left)
        self.master.bind('<Right>', self.move_right)

    def draw_person(self):
        # Удаляем предыдущего человека
        if self.image_id:
            self.canvas.delete(self.image_id)
        # Вычисляем координаты
        x = self.pos[1] * self.cell_size + self.cell_size // 2
        y = self.pos[0] * self.cell_size + self.cell_size // 2
        # Рисуем изображение
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
        new_row = self.pos[0] + delta_row
        new_col = self.pos[1] + delta_col
        # Проверка границ
        if 0 <= new_row < self.field_size and 0 <= new_col < self.field_size:
            self.pos = [new_row, new_col]
            self.draw_person()

if __name__ == "__main__":
    root = tk.Tk()
    game = TurtleGame(root)
    root.mainloop()
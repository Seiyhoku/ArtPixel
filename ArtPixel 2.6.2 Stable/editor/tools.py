import pygame
from typing import Optional, Tuple

class Tools:
    def __init__(self, editor):
        self.editor = editor
        self.current_tool = "Карандаш"
        self.tools = ["Карандаш", "Ластик", "Заливка", "Пипетка", "Линия", "Прямоугольник", "Круг"]  # Добавляем Круг
        self.actions = ["Очистить", "Размер", "Сохранить"]  # Порядок остается тем же
        self.drawing = False
        self.start_pos = None
        self.is_drawing = False  # Добавляем флаг активного рисования

    def handle_tool_action(self, pixel_pos, is_dragging=False):
        """Обработка действий инструментов"""
        if pygame.mouse.get_pressed()[1] or self.editor.wheel_active:
            return
        
        if not pixel_pos:
            return
            
        try:
            # Инструменты рисования фигур
            if self.current_tool in ["Линия", "Прямоугольник", "Круг"]:
                if not is_dragging:
                    if not self.drawing:  # Начало рисования
                        self.start_pos = pixel_pos
                        self.drawing = True
                    else:  # Завершение рисования
                        self.draw_shape(self.start_pos, pixel_pos)
                        self.drawing = False
                        self.start_pos = None
                        self.editor.save_state()
                elif self.drawing:  # Предпросмотр при перетаскивании
                    self.preview_shape(self.start_pos, pixel_pos)
            else:
                self._handle_basic_tools(pixel_pos, is_dragging)

        except Exception as e:
            print(f"Ошибка инструмента {self.current_tool}: {str(e)}")
            self.drawing = False
            self.start_pos = None

    def preview_shape(self, start_pos, end_pos):
        """Отображение предпросмотра фигуры"""
        # Создаем копию текущего холста для предпросмотра
        preview_surface = self.editor.canvas.copy()
        self.editor.canvas.blit(preview_surface, (0, 0))
        
        # Рисуем предварительную фигуру
        if self.current_tool == "Линия":
            self.draw_line(start_pos, end_pos)
        elif self.current_tool == "Прямоугольник":
            self.draw_rectangle(start_pos, end_pos)
        elif self.current_tool == "Круг":
            self.draw_circle(start_pos, end_pos)
            
        # Восстанавливаем оригинальный холст
        self.editor.canvas.blit(preview_surface, (0, 0))

    def _handle_basic_tools(self, pixel_pos, is_dragging):
        """Обработка базовых инструментов"""
        if self.current_tool == "Карандаш":
            self.editor.draw_pixel(pixel_pos)
        elif self.current_tool == "Ластик":
            self.editor.draw_pixel(pixel_pos, (0, 0, 0, 0))
        elif self.current_tool == "Заливка" and not is_dragging:
            target_color = self.editor.canvas.get_at(pixel_pos)
            self.flood_fill(pixel_pos)
            self.editor.save_state()
        elif self.current_tool == "Пипетка" and not is_dragging:
            color = self.editor.canvas.get_at(pixel_pos)
            if color[3] > 0:
                self.editor.color_manager.set_color(color[:3])

    def flood_fill(self, pos: Tuple[int, int]) -> None:
        x, y = pos
        target_color = self.editor.canvas.get_at((x, y))
        replacement_color = self.editor.color_manager.current_color
        
        if target_color == replacement_color:
            return
        
        stack = [(x, y)]
        while stack:
            x, y = stack.pop()
            if not (0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size):
                continue
            
            current_color = self.editor.canvas.get_at((x, y))
            if current_color != target_color:
                continue
            
            self.editor.draw_pixel((x, y), replacement_color)
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    def draw_shape(self, start_pos, end_pos):
        if self.current_tool == "Линия":
            self.draw_line(start_pos, end_pos)
        elif self.current_tool == "Прямоугольник":
            self.draw_rectangle(start_pos, end_pos)
        elif self.current_tool == "Круг":
            self.draw_circle(start_pos, end_pos)

    def draw_rectangle(self, start_pos, end_pos):
        """Улучшенное рисование прямоугольника"""
        x0, y0 = start_pos
        x1, y1 = end_pos
        
        # Определяем границы прямоугольника
        left = min(x0, x1)
        right = max(x0, x1)
        top = min(y0, y1)
        bottom = max(y0, y1)
        
        # Рисуем горизонтальные линии
        for x in range(left, right + 1):
            self.editor.draw_pixel((x, top))
            self.editor.draw_pixel((x, bottom))
            
        # Рисуем вертикальные линии
        for y in range(top + 1, bottom):
            self.editor.draw_pixel((left, y))
            self.editor.draw_pixel((right, y))

    def draw_line(self, start_pos, end_pos):
        """Улучшенное рисование линии (алгоритм Брезенхэма)"""
        x0, y0 = start_pos
        x1, y1 = end_pos
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                self.editor.draw_pixel((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                self.editor.draw_pixel((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        self.editor.draw_pixel((x, y))

    def draw_circle(self, start_pos, end_pos):
        """Улучшенное рисование окружности"""
        x0, y0 = start_pos
        x1, y1 = end_pos
        
        # Вычисляем радиус
        radius = int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        
        # Используем алгоритм Брезенхэма для окружности
        x = radius
        y = 0
        decision = 1 - radius
        
        while y <= x:
            self._draw_circle_points(x0, y0, x, y)
            y += 1
            if decision <= 0:
                decision += 2 * y + 1
            else:
                x -= 1
                decision += 2 * (y - x) + 1

    def _draw_circle_points(self, x0, y0, x, y):
        """Вспомогательный метод для рисования точек окружности"""
        self.editor.draw_pixel((x0 + x, y0 + y))
        self.editor.draw_pixel((x0 + x, y0 - y))
        self.editor.draw_pixel((x0 - x, y0 + y))
        self.editor.draw_pixel((x0 - x, y0 - y))
        self.editor.draw_pixel((x0 + y, y0 + x))
        self.editor.draw_pixel((x0 + y, y0 - x))
        self.editor.draw_pixel((x0 - y, y0 + x))
        self.editor.draw_pixel((x0 - y, y0 - x))

    def get_tools(self) -> list:
        """Возвращает список доступных инструментов."""
        return self.tools

    def get_actions(self) -> list:
        """Возвращает список доступных действий."""
        return self.actions
import pygame
from typing import Tuple
import logging

class Tools:
    def __init__(self, editor):
        self.editor = editor
        self.current_tool = "Карандаш"
        self.tools = ["Карандаш", "Ластик", "Заливка", "Пипетка", "Линия", "Прямоугольник", "Круг"]
        self.actions = ["Очистить", "Размер", "Сохранить"]  # Добавляем атрибут actions
        self.drawing = False
        self.start_pos = None
        self.preview_surface = None
        self.temp_surface = pygame.Surface((editor.grid_size, editor.grid_size), pygame.SRCALPHA)

    def reset_drawing_state(self):
        """Сброс состояния рисования"""
        self.drawing = False
        self.start_pos = None
        self.preview_surface = None
        self.temp_surface.fill((0, 0, 0, 0))

    def handle_tool_action(self, pixel_pos, is_dragging=False, is_mouse_up=False):
        """Обработка действий инструментов"""
        try:
            # Если кнопка мыши отпущена, завершаем рисование
            if is_mouse_up:
                if self.drawing and self.start_pos and pixel_pos:
                    # Рисуем финальную фигуру
                    if self.preview_surface:
                        self.editor.canvas = self.preview_surface.copy()
                    # Финальная отрисовка
                    self.draw_shape(self.start_pos, pixel_pos)
                    self.editor.save_state()
                self.reset_drawing_state()
                return

            if not pixel_pos:
                return

            if self.current_tool in ["Линия", "Прямоугольник", "Круг"]:
                if not is_dragging:
                    # Начало рисования
                    self.start_pos = pixel_pos
                    self.drawing = True
                    self.preview_surface = self.editor.canvas.copy()
                elif self.drawing and self.start_pos:
                    # Очищаем временную поверхность
                    self.temp_surface.fill((0, 0, 0, 0))
                    # Восстанавливаем состояние из preview
                    self.editor.canvas = self.preview_surface.copy()
                    # Рисуем предпросмотр
                    self.draw_preview_shape(self.start_pos, pixel_pos)
            else:
                self._handle_basic_tools(pixel_pos, is_dragging)
        except Exception as e:
            print(f"Ошибка инструмента {self.current_tool}: {str(e)}")
            self.reset_drawing_state()

    def draw_shape(self, start_pos, end_pos):
        """Общий метод для рисования фигур"""
        try:
            if self.current_tool == "Линия":
                self._draw_line(start_pos, end_pos)
            elif self.current_tool == "Прямоугольник":
                self._draw_rectangle(start_pos, end_pos)
            elif self.current_tool == "Круг":
                self._draw_circle(start_pos, end_pos)
        except Exception as e:
            logging.error(f"Ошибка отрисовки фигуры: {str(e)}")

    def _draw_circle(self, start_pos, end_pos, surface=None):
        """Отрисовка круга"""
        x0, y0 = start_pos
        x1, y1 = end_pos
        for point in self._get_circle_points(x0, y0, x1, y1):
            x, y = point
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                if surface:
                    surface.set_at((x, y), self.editor.color_manager.current_color)
                else:
                    self.editor.draw_pixel((x, y))

    def _get_circle_points(self, x0, y0, x1, y1):
        """Получение точек для круга по алгоритму Брезенхэма"""
        points = set()  # Используем set для уникальных точек
        radius = int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        
        x = 0
        y = radius
        delta = 1 - 2 * radius
        error = 0
        
        while y >= x:
            # Добавляем точки для всех октантов
            points.update([
                (x0 + x, y0 + y), (x0 + x, y0 - y),
                (x0 - x, y0 + y), (x0 - x, y0 - y),
                (x0 + y, y0 + x), (x0 + y, y0 - x),
                (x0 - y, y0 + x), (x0 - y, y0 - x)
            ])
            
            error = 2 * (delta + y) - 1
            if delta < 0 and error <= 0:
                x += 1
                delta += 2 * x + 1
                continue
                
            if delta > 0 and error > 0:
                y -= 1
                delta -= 2 * y + 1
                continue
                
            x += 1
            delta += 2 * (x - y)
            y -= 1
            
        return list(points)

    def draw_preview_shape(self, start_pos, end_pos):
        """Отрисовка предпросмотра фигуры"""
        # Проверяем и обновляем размер временной поверхности
        if self.temp_surface.get_size() != (self.editor.grid_size, self.editor.grid_size):
            self.update_temp_surface(self.editor.grid_size)
            
        preview_color = (*self.editor.color_manager.current_color[:3], 128)
        
        # Очищаем временную поверхность
        self.temp_surface.fill((0, 0, 0, 0))
        
        # Получаем точки для фигуры
        points = []
        if self.current_tool == "Линия":
            points = self._get_line_points(*start_pos, *end_pos)
        elif self.current_tool == "Прямоугольник":
            points = self._get_rectangle_points(*start_pos, *end_pos)
        elif self.current_tool == "Круг":
            points = self._get_circle_points(*start_pos, *end_pos)
            
        # Отрисовка точек
        for x, y in points:
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                self.temp_surface.set_at((x, y), preview_color)
        
        # Обновляем холст с предпросмотром
        if self.preview_surface:
            self.editor.canvas.blit(self.preview_surface, (0, 0))
        self.editor.canvas.blit(self.temp_surface, (0, 0))

    def _draw_preview_line(self, start_pos, end_pos, color):
        x1, y1 = start_pos
        x2, y2 = end_pos
        points = self._get_line_points(x1, y1, x2, y2)
        for x, y in points:
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                self.temp_surface.set_at((x, y), color)
        self.editor.canvas.blit(self.temp_surface, (0, 0))

    def _draw_preview_rectangle(self, start_pos, end_pos, color):
        x1, y1 = start_pos
        x2, y2 = end_pos
        points = self._get_rectangle_points(x1, y1, x2, y2)
        for x, y in points:
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                self.temp_surface.set_at((x, y), color)
        self.editor.canvas.blit(self.temp_surface, (0, 0))

    def _draw_preview_circle(self, start_pos, end_pos, color):
        x0, y0 = start_pos
        x1, y1 = end_pos
        points = self._get_circle_points(x0, y0, x1, y1)
        for x, y in points:
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                self.temp_surface.set_at((x, y), color)
        self.editor.canvas.blit(self.temp_surface, (0, 0))

    def _draw_rectangle(self, start_pos, end_pos, surface=None):
        """Рисование полого прямоугольника с помощью линий Брезенхэма"""
        surface = surface or self.editor.canvas
        x1, y1 = start_pos
        x2, y2 = end_pos
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # Рисуем 4 отдельные линии
        points = []
        # Верхняя горизонтальная линия
        for x in range(min_x, max_x + 1):
            points.append((x, min_y))
        # Нижняя горизонтальная линия
        for x in range(min_x, max_x + 1):
            points.append((x, max_y))
        # Левая вертикальная линия
        for y in range(min_y + 1, max_y):
            points.append((min_x, y))
        # Правая вертикальная линия
        for y in range(min_y + 1, max_y):
            points.append((max_x, y))
            
        # Рисуем все точки
        for x, y in points:
            if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                surface.set_at((x, y), self.editor.color_manager.current_color)

    def _draw_line(self, start_pos, end_pos, surface=None):
        """Рисование линии на указанной поверхности"""
        surface = surface or self.editor.canvas
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2
            while x != x2:
                if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                    surface.set_at((x, y), self.editor.color_manager.current_color)
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                x += step_x
        else:
            err = dy / 2
            while y != y2:
                if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
                    surface.set_at((x, y), self.editor.color_manager.current_color)
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                y += step_y
                
        if 0 <= x2 < self.editor.grid_size and 0 <= y2 < self.editor.grid_size:
            surface.set_at((x2, y2), self.editor.color_manager.current_color)

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

    def can_draw_at(self, x: int, y: int) -> bool:
        """Проверяет, можно ли рисовать в данной позиции"""
        if 0 <= x < self.editor.grid_size and 0 <= y < self.editor.grid_size:
            return True
        return False

    def get_actions(self) -> list:
        """Возвращает список доступных действий"""
        return self.actions

    def get_tools(self) -> list:
        """Возвращает список доступных инструментов"""
        return self.tools

    def _get_line_points(self, x1, y1, x2, y2):
        """Получение точек для линии"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                x += step_x
        else:
            err = dy / 2
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                y += step_y
        points.append((x2, y2))
        return points

    def _get_rectangle_points(self, x1, y1, x2, y2):
        """Получение точек для прямоугольника"""
        points = []
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # Горизонтальные линии
        for x in range(min_x, max_x + 1):
            points.append((x, min_y))
            points.append((x, max_y))
            
        # Вертикальные линии
        for y in range(min_y + 1, max_y):
            points.append((min_x, y))
            points.append((max_x, y))
            
        return points

    def update_temp_surface(self, new_size):
        """Обновляет размер временной поверхности при изменении размера холста"""
        self.temp_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
        self.reset_drawing_state()
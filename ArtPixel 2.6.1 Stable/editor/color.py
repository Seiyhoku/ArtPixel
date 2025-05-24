import pygame
import colorsys
from typing import Tuple

class ColorManager:
    def __init__(self, editor):
        self.editor = editor
        self.current_color = (255, 255, 255, 255)
        self.hue = 0.0
        self.alpha = 1.0
        self.sv_s = 1.0
        self.sv_v = 1.0
        self.sv_square_size = 120  # Размер квадрата выбора цвета
        self.hue_bar_rect = pygame.Rect(0, 0, 16, self.sv_square_size)
        self.sv_square_rect = pygame.Rect(0, 0, self.sv_square_size, self.sv_square_size)
        self.alpha_bar_rect = pygame.Rect(0, 0, self.sv_square_size + 20, 12)

    def set_color(self, color: Tuple[int, int, int]) -> None:
        self.current_color = (*color, int(self.alpha * 255))
        h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        self.hue = h
        self.sv_s = s
        self.sv_v = v
    
    def update_current_color(self) -> None:
        """Обновление текущего цвета"""
        try:
            rgb = self.hsv_to_rgb(self.hue, self.sv_s, self.sv_v)
            self.current_color = (*rgb, int(self.alpha * 255))
            print(f"Новый цвет: {self.current_color}")  # Отладка

            # Обновляем UI и перерисовываем экран
            if hasattr(self.editor, 'ui'):
                self.editor.ui.draw()
                pygame.display.update()

        except Exception as e:
            print(f"Ошибка обновления цвета: {str(e)}")

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def update_hue(self, y: int) -> None:
        """Обновляет оттенок цвета"""
        if y < 0:
            return
        self.hue = max(0, min(1, y / self.sv_square_size))
        print(f"Hue updated: {self.hue}")  # Отладочный вывод
        self.update_current_color()

    def update_sv(self, pos: Tuple[int, int]) -> None:
        """Обновляет насыщенность и яркость"""
        x, y = pos
        if x < 0 or y < 0:
            return
        self.sv_s = max(0, min(1, x / self.sv_square_size))
        self.sv_v = 1 - max(0, min(1, y / self.sv_square_size))
        print(f"SV updated: s={self.sv_s}, v={self.sv_v}")  # Отладочный вывод
        self.update_current_color()

    def update_alpha(self, x: int) -> None:
        """Обновляет прозрачность"""
        if x < 0:
            return
        self.alpha = max(0, min(1, x / (self.sv_square_size + 30)))
        print(f"Alpha updated: {self.alpha}")  # Отладочный вывод
        self.update_current_color()

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Конвертирует RGB в HEX формат"""
        return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Улучшенная обработка кликов"""
        try:
            print(f"ColorManager получил клик: {pos}")  # Отладка
            print(f"Координаты компонентов:")  # Отладка
            print(f"Hue bar: {self.hue_bar_rect}")
            print(f"SV square: {self.sv_square_rect}")
            print(f"Alpha bar: {self.alpha_bar_rect}")

            # Проверка клика по компонентам
            if self.hue_bar_rect.collidepoint(pos):
                local_y = pos[1] - self.hue_bar_rect.y
                self.hue = max(0, min(1, local_y / self.hue_bar_rect.height))
                print(f"Установлен Hue: {self.hue}")  # Отладка
                self.update_current_color()
                return True

            if self.sv_square_rect.collidepoint(pos):
                local_x = pos[0] - self.sv_square_rect.x
                local_y = pos[1] - self.sv_square_rect.y
                self.sv_s = max(0, min(1, local_x / self.sv_square_rect.width))
                self.sv_v = 1 - max(0, min(1, local_y / self.sv_square_rect.height))
                print(f"Установлены S: {self.sv_s}, V: {self.sv_v}")  # Отладка
                self.update_current_color()
                return True

            if self.alpha_bar_rect.collidepoint(pos):
                local_x = pos[0] - self.alpha_bar_rect.x
                self.alpha = max(0, min(1, local_x / self.alpha_bar_rect.width))
                print(f"Установлен Alpha: {self.alpha}")  # Отладка
                self.update_current_color()
                return True

            return False

        except Exception as e:
            print(f"Ошибка в Color Picker: {str(e)}")
            return False

    def handle_drag(self, pos: Tuple[int, int]) -> bool:
        return self.handle_click(pos)
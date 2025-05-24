# Импорты
import pygame
import os
import json
from typing import Optional, Tuple, List, Dict
from .ui import UI
from .tools import Tools
from .color import ColorManager
from .file_io import save_artwork, save_to_json, load_from_json
import colorsys
import math

# Константы
GRID_COLOR = (60, 60, 60)
UI_BG_COLOR = (45, 45, 48)

class PixelArtEditor:
    """
    Основной класс редактора пиксельной графики.
    Управляет всеми аспектами приложения: холстом, инструментами, UI.
    """
    
    def __init__(self, width=1280, height=1024, grid_size=32, zoom=16):
        """Инициализация редактора"""
        # Базовая инициализация pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Пиксельный редактор")
        
        # Основные параметры
        self._init_basic_params(width, height, grid_size, zoom)
        
        # Менеджеры и компоненты
        self._init_managers()
        
        # UI элементы
        self._init_ui_elements()
        
        # События и состояния
        self._init_states()
        
        # История
        self._init_history()

        # Новые атрибуты для обработки BACKSPACE
        self.backspace_delay = 500  # Начальная задержка перед быстрым удалением (в мс)
        self.backspace_interval = 50  # Интервал между удалениями при удержании (в мс)
        self.backspace_time = 0  # Время начала удержания
        self.backspace_next = 0  # Время следующего удаления

        # Добавляем флаг для отслеживания вывода отладки
        self.debug_logged = False

        # Добавляем флаг для отслеживания вывода
        self.files_search_logged = False

    def _init_basic_params(self, width, height, grid_size, zoom):
        """Инициализация базовых параметров"""
        self.original_width = width
        self.original_height = height
        self.grid_size = grid_size
        self.base_zoom = zoom
        self.zoom = zoom
        self.show_grid = True
        self.canvas = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
        self.canvas.fill((0, 0, 0, 0))

        # Инициализация шрифтов
        self.font = pygame.font.SysFont("Segoe UI", 12)
        self.large_font = pygame.font.SysFont("Segoe UI", 14, bold=True)

    def _init_managers(self):
        """Инициализация менеджеров компонентов"""
        self.color_manager = ColorManager(self)
        self.tools = Tools(self)
        self.ui = UI(self)

    def _init_ui_elements(self):
        """Инициализация элементов интерфейса"""
        # Добавляем атрибуты UI
        self.grid_color = GRID_COLOR
        self.ui_bg_color = UI_BG_COLOR  # Default UI background color
        
        # Добавляем недостающие атрибуты интерфейса
        self.ui_accent_color = (0, 122, 204)  # Цвет акцента интерфейса
        self.ui_text_color = (241, 241, 241)  # Цвет текста интерфейса
        self.ui_panel_color = (37, 37, 38)   # Цвет панелей интерфейса

        # Добавляем новые атрибуты
        self.magnifier_active = False
        self.magnifier_zoom_factor = 1.0
        self.magnifier_size = 200
        self.magnifier_mode = "zoom"
        self.last_zoom = self.zoom  # Исправляем здесь - используем self.zoom вместо zoom
        self.zoom_center = None
        
        # Обновляем цвета интерфейса
        self.colors = {
            'bg': (30, 30, 32),
            'panel': (45, 45, 48),
            'button': (37, 37, 38),
            'button_hover': (47, 47, 48),
            'button_active': (0, 122, 204),
            'border': (62, 62, 64),
            'text': (241, 241, 241),
            'text_dim': (180, 180, 180),
            'accent': (0, 122, 204)
        }

        # Добавляем атрибуты для функций быстрого доступа
        self.keyboard_shortcuts = {
            'grid': 'G',
            'undo': 'Ctrl+Z',
            'redo': 'Ctrl+Y',
            'save': 'Ctrl+S',
            'clear': 'Ctrl+C',
            'fullscreen': 'F11',
            'resize': 'R'
        }
        
        # Добавляем атрибуты для HEX-редактора
        self.hex_input_active = False
        self.hex_input = ""
        self.hex_input_error = False
        
        # Добавляем атрибуты для перемещения холста
        self.dragging_canvas = False
        self.last_mouse_pos = None
        self.canvas_x = None
        self.canvas_y = None
        self.update_canvas_position()

    def _init_states(self):
        """Инициализация состояний приложения"""
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Добавляем атрибуты для обработки событий мыши
        self.mouse_pressed = False
        self.last_pixel_pos = None
        self.ignore_next_mouse_up = False  # Добавляем флаг для игнорирования следующего события отпускания кнопки
        
        # Добавляем атрибуты для MOUSEWHEEL события
        self.current_mouse_pos = None

        # Обновляем атрибуты для диалога изменения размера
        self.resize_dialog_active = False
        self.resize_input = ""
        self.resize_dialog_ok_rect = None
        self.resize_dialog_cancel_rect = None
        self.large_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
        # Добавляем обработку курсора
        self.default_cursor = pygame.SYSTEM_CURSOR_ARROW
        self.move_cursor = pygame.SYSTEM_CURSOR_SIZEALL
        pygame.mouse.set_cursor(self.default_cursor)

        self.is_zooming = False
        self.allow_drawing = True  # Новый флаг для контроля рисования

        self.wheel_active = False  # Новый флаг для колеса мыши
        self.wheel_cooldown = 0  # Добавляем задержку после прокрутки

        # Фиксим проблему с absent attributes
        self.update_ui_elements = self.update_canvas_position  # Добавляем алиас для метода
        self.tools_panel_height = 420  # Добавляем высоту панели инструментов
        self.side_panel_width = 200  # Добавляем ширину боковой панели
        self.resize_dialog_active = False  # Добавляем флаг активности диалога
        self.resize_input = ""  # Добавляем поле для ввода размера
        self.resize_dialog_ok_rect = None  # Добавляем rect для кнопки ОК
        self.resize_dialog_cancel_rect = None  # Добавляем rect для кнопки Отмена

        # Добавляем атрибуты для диалога сохранения
        self.save_dialog_active = False
        self.save_input = ""
        self.save_dialog_ok_rect = None
        self.save_dialog_cancel_rect = None

        # Добавляем атрибуты для диалога открытия
        self.open_dialog_active = False
        self.selected_file_index = 0
        self.available_files = []
    
    def _init_history(self):
        """Инициализация системы истории"""
        self.history: List[pygame.Surface] = []
        self.history_index = -1
        self.save_state()

    def update_canvas_position(self):
        """Обновление позиции холста при изменении размера окна"""
        self.canvas_width = self.grid_size * self.zoom
        self.canvas_height = self.grid_size * self.zoom
        
        if self.canvas_x is None or self.canvas_y is None:
            self.canvas_x = (self.screen.get_width() - self.canvas_width) // 2
            self.canvas_y = (self.screen.get_height() - self.canvas_height) // 2

    def run(self):
        """Основной цикл приложения"""
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.handle_events(event)
                
                self.draw()
                self.clock.tick(60)
        except Exception as e:
            print(f"Ошибка в основном цикле: {str(e)}")
        finally:
            pygame.quit()

    def _apply_resize(self):
        """Оптимизированное изменение размера"""
        try:
            if not self.resize_input:
                return
                
            new_size = int(self.resize_input)
            if 2 <= new_size <= 256:
                old_size = self.grid_size
                if self.resize_canvas(new_size) and old_size != self.grid_size:
                    self.resize_dialog_active = False
                    self.resize_input = ""
                    print(f"Размер холста: {new_size}x{new_size}")
                
        except ValueError as e:
            print(f"Ошибка размера: {e}")

    def handle_events(self, event):
        """Центральный обработчик событий"""
        try:
            # Сначала проверяем события колеса мыши
            if event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_ALT:
                    # Инвертируем направление для более естественного масштабирования
                    return self.handle_zoom(event.y, pygame.mouse.get_pos())  # Убираем минус перед event.y
            
            # Проверка активных диалогов
            if self.resize_dialog_active or self.save_dialog_active or self.open_dialog_active:
                return self._handle_dialog_events(event)
            
            # Обработка остальных событий мыши
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                return self._handle_mouse_events(event)
                
            # Обработка клавиатуры
            if event.type == pygame.KEYDOWN:
                return self.handle_keyboard_events(event)
                
        except Exception as e:
            print(f"Ошибка событий: {e}")

    # === Обработка мыши ===

    def _handle_mouse_events(self, event):
        """Обработка событий мыши"""
        try:
            pos = pygame.mouse.get_pos()

            # Масштабирование с Alt + колесо мыши
            if event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_ALT:
                    self.wheel_active = True
                    # Инвертируем направление для более естественного масштабирования
                    zoom_direction = -event.y
                    self.handle_zoom(zoom_direction, pos)
                    return True
                return False

            # Сбрасываем флаг колеса мыши
            self.wheel_active = False

            # Обработка кнопок мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # Средняя кнопка (колесо)
                    self.dragging_canvas = True
                    self.last_mouse_pos = pos
                    pygame.mouse.set_cursor(self.move_cursor)
                    return True
                elif event.button == 1:  # ЛКМ
                    # Проверяем клик по UI панелям
                    if pos[0] > self.screen.get_width() - self.side_panel_width:
                        if self.color_manager.handle_click(pos):
                            return True
                    elif pos[0] < self.side_panel_width:
                        if self.ui.handle_click(pos):
                            return True
                    else:
                        # Клик по холсту
                        pixel_pos = self.get_pixel_pos(pos)
                        if pixel_pos:
                            self.tools.handle_tool_action(pixel_pos)
                            return True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Средняя кнопка (колесо)
                    self.dragging_canvas = False
                    self.last_mouse_pos = None
                    pygame.mouse.set_cursor(self.default_cursor)
                    return True

            elif event.type == pygame.MOUSEMOTION:
                # Перетаскивание холста
                if self.dragging_canvas and self.last_mouse_pos:
                    dx = pos[0] - self.last_mouse_pos[0]
                    dy = pos[1] - self.last_mouse_pos[1]
                    self.canvas_x += dx
                    self.canvas_y += dy
                    self.last_mouse_pos = pos
                    return True
                # Обработка рисования и UI
                elif pygame.mouse.get_pressed()[0]:  # Зажата ЛКМ
                    if pos[0] > self.screen.get_width() - self.side_panel_width:
                        return self.color_manager.handle_drag(pos)
                    elif pos[0] > self.side_panel_width:
                        pixel_pos = self.get_pixel_pos(pos)
                        if pixel_pos:
                            self.tools.handle_tool_action(pixel_pos, True)
                            return True

            return False

        except Exception as e:
            print(f"Ошибка обработки мыши: {str(e)}")
            return False

    def handle_zoom(self, direction: int, mouse_pos: Tuple[int, int]) -> None:
        """Улучшенная обработка масштабирования"""
        try:
            if not mouse_pos:
                return

            # Сохраняем текущее положение мыши относительно холста
            rel_x = (mouse_pos[0] - self.canvas_x) / self.zoom
            rel_y = (mouse_pos[1] - self.canvas_y) / self.zoom
            
            old_zoom = self.zoom
            
            # Меняем логику масштабирования
            if direction > 0 and self.zoom < 50:  # Прокрутка вверх - приближение
                self.zoom = min(50, self.zoom + max(1, self.zoom * 0.1))
            elif direction < 0 and self.zoom > 2:  # Прокрутка вниз - отдаление
                self.zoom = max(2, self.zoom - max(1, self.zoom * 0.1))
            
            # Обновляем размеры холста
            self.canvas_width = self.grid_size * self.zoom
            self.canvas_height = self.grid_size * self.zoom

            # Обновляем позицию холста, сохраняя позицию курсора
            self.canvas_x = mouse_pos[0] - (rel_x * self.zoom)
            self.canvas_y = mouse_pos[1] - (rel_y * self.zoom)

            print(f"Zoom: {self.zoom}x, Old: {old_zoom}x, Dir: {direction}")

        except Exception as e:
            print(f"Ошибка масштабирования: {str(e)}")

    # === Отрисовка ===

    def draw(self):
        """Основная функция отрисовки"""
        try:
            # Проверяем удержание backspace
            if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                current_time = pygame.time.get_ticks()
                if current_time >= self.backspace_next:
                    # Если в фокусе диалог сохранения
                    if self.save_dialog_active and self.save_input:
                        self.save_input = self.save_input[:-1]
                        self.backspace_next = current_time + self.backspace_interval
                    # Если в фокусе диалог изменения размера
                    elif self.resize_dialog_active and self.resize_input:
                        self.resize_input = self.resize_input[:-1]
                        self.backspace_next = current_time + self.backspace_interval

            # Очищаем экран один раз
            self.screen.fill(self.colors['bg'])
            
            # Рисуем все элементы в правильном порядке
            self.draw_canvas()  # Холст всегда первый
            
            # Если нет активных диалогов - обновляем и рисуем UI
            if not (self.resize_dialog_active or self.save_dialog_active or self.open_dialog_active):
                # Обновляем позицию цветовой панели один раз
                if hasattr(self.ui, 'color_picker_rect'):
                    self.ui.color_picker_rect.x = self.screen.get_width() - self.side_panel_width + self.ui.panel_margin
                # Отрисовка UI
                self.ui.draw()
            
            # Отрисовка дополнительных элементов
            if self.magnifier_active:
                self.draw_magnifier()
    
            # Диалоги отрисовываются последними
            if self.open_dialog_active:
                if not self.debug_logged:
                    print("Отрисовка диалога открытия")  # Отладка только один раз
                    self.debug_logged = True
                self.draw_open_dialog()
            else:
                self.debug_logged = False  # Сбрасываем флаг когда диалог закрыт
            if self.resize_dialog_active:
                self.draw_resize_dialog()
            elif self.save_dialog_active:
                self.draw_save_dialog()
                
            pygame.display.flip()

        except Exception as e:
            print(f"Ошибка отрисовки: {str(e)}")
            import traceback
            traceback.print_exc()

    def draw_save_dialog(self):
        """Отрисовка диалога сохранения файла"""
        # Затемняем фон
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 25, 180))
        self.screen.blit(overlay, (0, 0))

        # Параметры диалога
        dialog_w, dialog_h = 420, 220
        dialog_x = (self.screen.get_width() - dialog_w) // 2
        dialog_y = (self.screen.get_height() - dialog_h) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        # Рисуем окно
        pygame.draw.rect(self.screen, (38, 41, 48), dialog_rect, border_radius=14)
        pygame.draw.rect(self.screen, (80, 80, 90), dialog_rect, 2, border_radius=14)

        # Заголовок
        title = self.large_font.render("Сохранить файл", True, (255, 255, 255))
        title_rect = title.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 32))
        self.screen.blit(title, title_rect)

        # Поле ввода с ограничением по ширине
        input_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.y + 95, 300, 38)
        pygame.draw.rect(self.screen, (50, 50, 60), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 140), input_rect, 2, border_radius=8)
        
        # Текст ввода с курсором и обрезкой
        input_text = self.save_input
        if pygame.time.get_ticks() % 1000 < 500:
            input_text += "|"
            
        # Обрезаем текст, если он не помещается
        temp_text = self.font.render(input_text, True, (255, 255, 255))
        max_width = input_rect.width - 20  # Отступ по 10 пикселей с каждой стороны
        
        if temp_text.get_width() > max_width:
            # Показываем конец текста, если он слишком длинный
            while temp_text.get_width() > max_width and len(input_text) > 1:
                input_text = "..." + input_text[4:]
                temp_text = self.font.render(input_text, True, (255, 255, 255))
        
        text = self.font.render(input_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=input_rect.center)
        self.screen.blit(text, text_rect)

        # Подсказка
        hint = self.font.render("Введите имя файла", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(dialog_rect.centerx, input_rect.top - 10))
        self.screen.blit(hint, hint_rect)

        # Кнопки
        btn_w, btn_h = 120, 36
        btn_gap = 24
        btn_y = dialog_rect.y + dialog_h - btn_h - 24
        
        # Кнопка "Сохранить"
        save_rect = pygame.Rect(dialog_rect.centerx - btn_w - btn_gap//2, btn_y, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        save_color = (0, 122, 204) if save_rect.collidepoint(mouse_pos) else (30, 90, 160)
        pygame.draw.rect(self.screen, save_color, save_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 200), save_rect, 2, border_radius=8)
        save_text = self.font.render("Сохранить", True, (255,255,255))
        self.screen.blit(save_text, save_text.get_rect(center=save_rect.center))

        # Кнопка "Отмена"
        cancel_rect = pygame.Rect(dialog_rect.centerx + btn_gap//2, btn_y, btn_w, btn_h)
        cancel_color = (60, 60, 70) if cancel_rect.collidepoint(mouse_pos) else (40, 40, 50)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 140), cancel_rect, 2, border_radius=8)
        cancel_text = self.font.render("Отмена", True, (220,220,220))
        self.screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))

        self.save_dialog_ok_rect = save_rect
        self.save_dialog_cancel_rect = cancel_rect

    def draw_resize_dialog(self):
        """Отрисовка диалога изменения размера холста"""
        # Затемняем фон
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 25, 180))
        self.screen.blit(overlay, (0, 0))

        # Параметры диалога
        dialog_w, dialog_h = 420, 220
        dialog_x = (self.screen.get_width() - dialog_w) // 2
        dialog_y = (self.screen.get_height() - dialog_h) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        # Рисуем окно с тенью
        shadow = pygame.Surface((dialog_w+8, dialog_h+8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,80), shadow.get_rect(), border_radius=18)
        self.screen.blit(shadow, (dialog_x-4, dialog_y-4))
        pygame.draw.rect(self.screen, (38, 41, 48), dialog_rect, border_radius=14)
        pygame.draw.rect(self.screen, (80, 80, 90), dialog_rect, 2, border_radius=14)

        # Заголовок
        title = self.large_font.render("Изменить размер холста", True, (255, 255, 255))
        title_rect = title.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 32))
        self.screen.blit(title, title_rect)

        # Отрисовываем текст с текущим размером над полем ввода
        prompt = self.font.render(f"Текущий размер: {self.grid_size}x{self.grid_size}", True, (180, 180, 180))
        prompt_rect = prompt.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 75))
        self.screen.blit(prompt, prompt_rect)

        # Поле ввода с фокусом
        input_rect = pygame.Rect(dialog_rect.centerx - 70, dialog_rect.y + 95, 140, 38)
        input_color = (60, 60, 70) if self.resize_dialog_active else (50, 50, 60)
        pygame.draw.rect(self.screen, input_color, input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (0, 122, 204), input_rect, 2, border_radius=8)
        
        # Мигающий курсор в поле ввода
        input_text = self.resize_input
        if pygame.time.get_ticks() % 1000 < 500:
            input_text += "|"
        text = self.font.render(input_text, True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=input_rect.center))

        # Подсказка под полем ввода
        size_hint = self.font.render("(2-256)", True, (180, 180, 180))
        size_hint_rect = size_hint.get_rect(centerx=dialog_rect.centerx, top=input_rect.bottom + 8)
        self.screen.blit(size_hint, size_hint_rect)

        # Кнопки
        btn_w, btn_h = 120, 36
        btn_gap = 24
        btn_y = dialog_rect.y + dialog_h - btn_h - 24

        # Кнопка "Применить"
        apply_rect = pygame.Rect(dialog_rect.centerx - btn_w - btn_gap//2, btn_y, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        apply_color = (0, 122, 204) if apply_rect.collidepoint(mouse_pos) else (30, 90, 160)
        pygame.draw.rect(self.screen, apply_color, apply_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 200), apply_rect, 2, border_radius=8)
        apply_text = self.font.render("Применить", True, (255,255,255))
        self.screen.blit(apply_text, apply_text.get_rect(center=apply_rect.center))

        # Кнопка "Отмена"
        cancel_rect = pygame.Rect(dialog_rect.centerx + btn_gap//2, btn_y, btn_w, btn_h)
        cancel_color = (60, 60, 70) if cancel_rect.collidepoint(mouse_pos) else (40, 40, 50)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 140), cancel_rect, 2, border_radius=8)
        cancel_text = self.font.render("Отмена", True, (220,220,220))
        self.screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))

        self.resize_dialog_ok_rect = apply_rect
        self.resize_dialog_cancel_rect = cancel_rect
        return apply_rect, cancel_rect

    def draw_canvas(self):
        """Отрисовка холста"""
        # Рисуем шахматный фон для прозрачности
        cell_size = max(4, self.zoom // 2)  # Размер клетки фона
        for y in range(0, self.canvas_height, cell_size):
            for x in range(0, self.canvas_width, cell_size):
                color = (60, 60, 60) if ((x + y) // cell_size) % 2 == 0 else (70, 70, 70)
                rect = pygame.Rect(self.canvas_x + x, self.canvas_y + y, 
                                 min(cell_size, self.canvas_width - x),
                                 min(cell_size, self.canvas_height - y))
                pygame.draw.rect(self.screen, color, rect)
        
        # Отрисовка масштабированного холста
        canvas_scaled = pygame.transform.scale(
            self.canvas,
            (self.canvas_width, self.canvas_height)
        )
        self.screen.blit(canvas_scaled, (self.canvas_x, self.canvas_y))
        
        # Отрисовка сетки
        if self.show_grid:
            for i in range(self.grid_size + 1):
                x = self.canvas_x + i * self.zoom
                y = self.canvas_y + i * self.zoom
                # Вертикальные линии
                pygame.draw.line(
                    self.screen, self.grid_color,
                    (x, self.canvas_y),
                    (x, self.canvas_y + self.canvas_height)
                )
                # Горизонтальные линии
                pygame.draw.line(
                    self.screen, self.grid_color,
                    (self.canvas_x, y),
                    (self.canvas_x + self.canvas_width, y)
                )

    def draw_magnifier(self):
        """Отрисовка лупы"""
        if not self.magnifier_active:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos
        
        rect_size = self.magnifier_size
        half_size = rect_size // 2
        
        magnifier_surface = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
        
        canvas_pos = self.get_pixel_pos(mouse_pos)
        if not canvas_pos:
            return
            
        px, py = canvas_pos
        
        zoom_factor = 4.0  # Фиксированный коэффициент увеличения для лупы
        if self.magnifier_mode == "unzoom":
            zoom_factor = 0.5
            
        source_size = rect_size / (self.zoom * zoom_factor)
        src_x = max(0, px - source_size/2)
        src_y = max(0, py - source_size/2)
        src_x_end = min(self.grid_size, src_x + source_size)
        src_y_end = min(self.grid_size, src_y + source_size)
        
        cell_size = (rect_size / source_size) if source_size > 0 else 0
        
        for y in range(int(src_y), int(src_y_end)):
            for x in range(int(src_x), int(src_x_end)):
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    color = self.canvas.get_at((x, y))
                    pos_x = (x - src_x) * cell_size
                    pos_y = (y - src_y) * cell_size
                    pygame.draw.rect(
                        magnifier_surface, color,
                        (pos_x, pos_y, math.ceil(cell_size), math.ceil(cell_size))
                    )
        
        # Отрисовка лупы
        border_rect = (mx - half_size - 2, my - half_size - 2, rect_size + 4, rect_size + 4)
        pygame.draw.rect(self.screen, (200, 200, 200), border_rect, 2)
        pygame.draw.rect(self.screen, (80, 80, 80), border_rect, 1)
        
        self.screen.blit(magnifier_surface, (mx - half_size, my - half_size))
        
        # Рисуем перекрестие
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (mx - half_size, my), (mx + half_size, my), 1)
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (mx, my - half_size), (mx, my + half_size), 1)
        
        # Отображаем текст с режимом и масштабом
        mode_text = "Уменьшение" if self.magnifier_mode == "unzoom" else "Увеличение"
        text_surf = self.font.render(f"{mode_text} {zoom_factor:.1f}x", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(mx, my + half_size + 15))
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (text_rect.x - 5, text_rect.y - 2, text_rect.width + 10, text_rect.height + 4))
        self.screen.blit(text_surf, text_rect)

    # === Утилиты ===

    def save_state(self):
        """Сохранение состояния для истории"""
        canvas_copy = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
        canvas_copy.blit(self.canvas, (0, 0))
        
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(canvas_copy)
        self.history_index = len(self.history) - 1
        
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1

    def update_canvas_position(self):
        """Обновление позиции холста при изменении размера окна"""
        self.canvas_width = self.grid_size * self.zoom
        self.canvas_height = self.grid_size * self.zoom
        
        if self.canvas_x is None or self.canvas_y is None:
            self.canvas_x = (self.screen.get_width() - self.canvas_width) // 2
            self.canvas_y = (self.screen.get_height() - self.canvas_height) // 2

    # === Обработчики инструментов ===

    def draw_pixel(self, pos: Tuple[int, int], color=None) -> None:
        """Отрисовка пикселя"""
        try:
            x, y = pos
            if color is None:
                color = self.color_manager.current_color
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                # Проверяем, рисуем ли мы предпросмотр
                if self.tools.drawing and self.tools.current_tool in ["Линия", "Прямоугольник", "Круг"]:
                    # Создаем временную копию для предпросмотра
                    temp_surface = self.canvas.copy()
                    self.canvas.set_at((int(x), int(y)), color)
                    # Восстанавливаем оригинальный холст
                    self.screen.blit(temp_surface, (self.canvas_x, self.canvas_y))
                else:
                    self.canvas.set_at((int(x), int(y)), color)
                    if not self.tools.drawing:
                        self.save_state()
        except Exception as e:
            print(f"Ошибка отрисовки пикселя: {str(e)}")

    def clear_canvas(self):
        """Очистка холста"""
        self.save_state()
        self.canvas.fill((0, 0, 0, 0))

    def resize_canvas(self, new_size: int):
        """Изменение размера холста"""
        try:
            if not isinstance(new_size, int):
                raise ValueError("Размер должен быть целым числом")
            
            if new_size < 2 or new_size > 512:
                raise ValueError("Размер должен быть от 2 до 512")

            self.save_state()
            old_canvas = self.canvas.copy()
            self.grid_size = new_size
            self.canvas = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
            self.canvas.fill((0, 0, 0, 0))

            # Копируем содержимое старого холста в новый
            copy_size = min(old_canvas.get_width(), new_size)
            self.canvas.blit(old_canvas, (0, 0), (0, 0, copy_size, copy_size))
            self.update_canvas_position()
        except Exception as e:
            print(f"Ошибка изменения размера: {str(e)}")
            return False

    def get_pixel_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Преобразует координаты экрана в координаты пикселя на холсте."""
        x, y = pos
        
        # Проверяем, находится ли точка в пределах холста
        if (self.canvas_x <= x < self.canvas_x + self.canvas_width and
            self.canvas_y <= y < self.canvas_y + self.canvas_height):
            
            # Вычисляем координаты пикселя
            px = int((x - self.canvas_x) / self.zoom)
            py = int((y - self.canvas_y) / self.zoom)
            
            # Проверяем границы
            if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                return (px, py)
        
        return None

    def handle_zoom(self, direction: int, mouse_pos: Tuple[int, int]) -> None:
        """Обработка масштабирования относительно позиции курсора."""
        if not mouse_pos:
            return

        old_zoom = self.zoom
        
        # Изменяем масштаб с учетом ограничений
        if direction > 0 and self.zoom < 50:  # Приближение
            self.zoom += 1
        elif direction < 0 and self.zoom > 2:  # Отдаление
            self.zoom -= 1
        else:
            return  # Если масштаб не изменился, выходим

        # Получаем позицию курсора относительно холста до изменения масштаба
        canvas_x = (mouse_pos[0] - self.canvas_x) / old_zoom
        canvas_y = (mouse_pos[1] - self.canvas_y) / old_zoom

        # Обновляем размеры холста
        self.canvas_width = self.grid_size * self.zoom
        self.canvas_height = self.grid_size * self.zoom

        # Вычисляем новую позицию холста, чтобы точка под курсором осталась на месте
        self.canvas_x = mouse_pos[0] - (canvas_x * self.zoom)
        self.canvas_y = mouse_pos[1] - (canvas_y * self.zoom)

    def handle_mousewheel_event(self, event):
        """Отдельный метод для обработки колеса мыши"""
        self.wheel_active = True
        self.ignore_next_mouse_up = True
        self.mouse_pressed = False  # Сбрасываем флаг нажатия мыши
        self.last_pixel_pos = None  # Сбрасываем последнюю позицию пикселя
    
        if pygame.key.get_mods() & pygame.KMOD_ALT:
            self.handle_zoom(event.y, pygame.mouse.get_pos())
        return True
    def save_image(self):
        """Открывает диалог сохранения изображения."""
        self.save_dialog_active = True
        self.save_input = ""

    def _apply_resize(self):
        """Вспомогательный метод для применения изменения размера холста"""
        try:
            if not self.resize_input:
                return
                
            new_size = int(self.resize_input)
            if 2 <= new_size <= 256:
                # Сохраняем старый размер для проверки изменений
                old_size = self.grid_size
                
                # Применяем изменение размера
                self.resize_canvas(new_size)
                
                # Очищаем диалог только если размер действительно изменился
                if old_size != self.grid_size:
                    self.resize_dialog_active = False
                    self.resize_input = ""
                    print(f"Размер холста изменен на {new_size}x{new_size}")
                
        except ValueError as e:
            print(f"Ошибка изменения размера: {str(e)}")
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")

    def _handle_mouse_events(self, event):
        """Обработка событий мыши"""
        try:
            pos = pygame.mouse.get_pos()

            # Масштабирование с Alt + колесо мыши
            if event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_ALT:
                    self.wheel_active = True
                    # Инвертируем направление для более естественного масштабирования
                    zoom_direction = -event.y
                    self.handle_zoom(zoom_direction, pos)
                    return True
                return False

            # Сбрасываем флаг колеса мыши
            self.wheel_active = False

            # Обработка кнопок мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # Средняя кнопка (колесо)
                    self.dragging_canvas = True
                    self.last_mouse_pos = pos
                    pygame.mouse.set_cursor(self.move_cursor)
                    return True
                elif event.button == 1:  # ЛКМ
                    # Проверяем клик по UI панелям
                    if pos[0] > self.screen.get_width() - self.side_panel_width:
                        if self.color_manager.handle_click(pos):
                            return True
                    elif pos[0] < self.side_panel_width:
                        if self.ui.handle_click(pos):
                            return True
                    else:
                        # Клик по холсту
                        pixel_pos = self.get_pixel_pos(pos)
                        if pixel_pos:
                            self.tools.handle_tool_action(pixel_pos)
                            return True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Средняя кнопка (колесо)
                    self.dragging_canvas = False
                    self.last_mouse_pos = None
                    pygame.mouse.set_cursor(self.default_cursor)
                    return True

            elif event.type == pygame.MOUSEMOTION:
                # Перетаскивание холста
                if self.dragging_canvas and self.last_mouse_pos:
                    dx = pos[0] - self.last_mouse_pos[0]
                    dy = pos[1] - self.last_mouse_pos[1]
                    self.canvas_x += dx
                    self.canvas_y += dy
                    self.last_mouse_pos = pos
                    return True
                # Обработка рисования и UI
                elif pygame.mouse.get_pressed()[0]:  # Зажата ЛКМ
                    if pos[0] > self.screen.get_width() - self.side_panel_width:
                        return self.color_manager.handle_drag(pos)
                    elif pos[0] > self.side_panel_width:
                        pixel_pos = self.get_pixel_pos(pos)
                        if pixel_pos:
                            self.tools.handle_tool_action(pixel_pos, True)
                            return True

            return False

        except Exception as e:
            print(f"Ошибка обработки мыши: {str(e)}")
            return False

    def handle_zoom(self, y: int, mouse_pos: Tuple[int, int]) -> None:
        """Улучшенная обработка масштабирования"""
        try:
            if not mouse_pos:
                return

            old_zoom = self.zoom
            
            # Изменяем масштаб с учетом направления прокрутки
            if y > 0 and self.zoom < 50:  # Приближение
                self.zoom = min(50, self.zoom + 1)
            elif y < 0 and self.zoom > 2:  # Отдаление
                self.zoom = max(2, self.zoom - 1)
            else:
                return  # Масштаб не изменился

            # Получаем позицию курсора относительно холста до изменения масштаба
            canvas_x = (mouse_pos[0] - self.canvas_x) / old_zoom
            canvas_y = (mouse_pos[1] - self.canvas_y) / old_zoom

            # Обновляем размеры холста
            self.canvas_width = self.grid_size * self.zoom
            self.canvas_height = self.grid_size * self.zoom

            # Вычисляем новую позицию холста относительно курсора
            self.canvas_x = mouse_pos[0] - (canvas_x * self.zoom)
            self.canvas_y = mouse_pos[1] - (canvas_y * self.zoom)

            print(f"Zoom: {self.zoom}x")  # Отладка

        except Exception as e:
            print(f"Ошибка масштабирования: {str(e)}")

    def _handle_dialog_events(self, event):
        """Обработка событий диалоговых окон"""
        try:
            if self.resize_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_resize_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_resize_dialog_click(event)
                    
            elif self.save_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_save_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_save_dialog_click(event)
            
            elif self.open_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_open_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_open_dialog_click(event)
            
            return False

        except Exception as e:
            print(f"Ошибка диалога: {e}")
            return False

    def _handle_canvas_drag(self, pos):
        """Обработка перетаскивания холста"""
        dx = pos[0] - self.last_mouse_pos[0]
        dy = pos[1] - self.last_mouse_pos[1]
        self.canvas_x += dx
        self.canvas_y += dy
        self.last_mouse_pos = pos
        pygame.mouse.set_cursor(self.move_cursor)

    def _handle_resize_dialog_key(self, event):
        """Обработка клавиш в диалоге изменения размера"""
        if event.key == pygame.K_ESCAPE:
            self.resize_dialog_active = False
            self.resize_input = ""
        elif event.key == pygame.K_RETURN:
            self._apply_resize()
        elif event.key == pygame.K_BACKSPACE:
            current_time = pygame.time.get_ticks()
            self.backspace_time = current_time
            self.backspace_next = current_time + self.backspace_delay
            self.resize_input = self.resize_input[:-1]
        elif event.unicode.isdigit() and len(self.resize_input) < 3:
            self.resize_input += event.unicode
        return True

    def _handle_resize_dialog_click(self, event):
        """Обработка кликов в диалоге изменения размера"""
        pos = pygame.mouse.get_pos()
        if self.resize_dialog_ok_rect and self.resize_dialog_ok_rect.collidepoint(pos):
            self._apply_resize()
        elif self.resize_dialog_cancel_rect and self.resize_dialog_cancel_rect.collidepoint(pos):
            self.resize_dialog_active = False
            self.resize_input = ""
        return True

    def handle_keyboard_events(self, event) -> bool:
        """Обработка событий клавиатуры"""
        try:
            # Если активны диалоги
            if self.save_dialog_active:
                return self._handle_save_dialog_key(event)
            elif self.resize_dialog_active:
                return self._handle_resize_dialog_key(event)
            elif self.open_dialog_active:
                return self._handle_open_dialog_key(event)

            # Общие клавиши
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return True
                
            # Горячие клавиши с модификаторами
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:  # Ctrl+Z - отмена
                    self.undo()
                    return True
                elif event.key == pygame.K_y:  # Ctrl+Y - повтор
                    self.redo()
                    return True
                elif event.key == pygame.K_s:  # Ctrl+S - сохранить
                    self.save_dialog_active = True
                    return True
                elif event.key == pygame.K_c:  # Ctrl+C - очистить
                    self.clear_canvas()
                    return True
                elif event.key == pygame.K_o:  # Ctrl+O - открыть
                    self.open_dialog_active = True
                    self.selected_file_index = 0
                    self.available_files = self.get_available_files()
                    return True

            # Функциональные клавиши и другие
            if event.key == pygame.K_F11:  # F11 - полный экран
                self.toggle_fullscreen()
                return True
            elif event.key == pygame.K_g:  # G - сетка
                self.show_grid = not self.show_grid
                return True
            elif event.key == pygame.K_m:  # M - лупа
                self.magnifier_active = not self.magnifier_active
                return True
            elif event.key == pygame.K_r:  # R - размер холста
                self.resize_dialog_active = True
                self.resize_input = ""
                return True

            return False

        except Exception as e:
            print(f"Ошибка клавиатуры: {str(e)}")
            return False

    def _handle_save_dialog_key(self, event) -> bool:
        """Обработка клавиш в диалоге сохранения"""
        if event.key == pygame.K_ESCAPE:
            self.save_dialog_active = False
            self.save_input = ""
        elif event.key == pygame.K_RETURN:
            if self.save_input.strip():
                save_artwork(self.canvas, self.save_input)
                self.save_dialog_active = False
                self.save_input = ""
        elif event.key == pygame.K_BACKSPACE:
            current_time = pygame.time.get_ticks()
            self.backspace_time = current_time
            self.backspace_next = current_time + self.backspace_delay
            self.save_input = self.save_input[:-1]
        elif event.unicode.isalnum() or event.unicode in "-_ ":
            # Ограничиваем длину имени файла
            if len(self.save_input) < 50:  # Максимальная длина имени файла
                self.save_input += event.unicode
        return True

    def _handle_save_dialog_click(self, event):
        """Обработка кликов в диалоге сохранения"""
        try:
            pos = pygame.mouse.get_pos()
            if self.save_dialog_ok_rect and self.save_dialog_ok_rect.collidepoint(pos):
                if self.save_input.strip():
                    save_artwork(self.canvas, self.save_input)
                    print(f"Файл сохранен: {self.save_input}")
                self.save_dialog_active = False
                self.save_input = ""
                return True
            elif self.save_dialog_cancel_rect and self.save_dialog_cancel_rect.collidepoint(pos):
                self.save_dialog_active = False
                self.save_input = ""
                return True
            return False
        except Exception as e:
            print(f"Ошибка при обработке клика диалога сохранения: {str(e)}")
            return False

    def draw_open_dialog(self):
        """Отрисовка диалога открытия файла"""
        # Затемняем фон
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 20, 25, 180))
        self.screen.blit(overlay, (0, 0))

        # Параметры диалога
        dialog_w, dialog_h = 420, 320
        dialog_x = (self.screen.get_width() - dialog_w) // 2
        dialog_y = (self.screen.get_height() - dialog_h) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        # Основное окно
        pygame.draw.rect(self.screen, (38, 41, 48), dialog_rect, border_radius=14)
        pygame.draw.rect(self.screen, (80, 80, 90), dialog_rect, 2, border_radius=14)

        # Заголовок
        title = self.large_font.render("Открыть проект", True, (255, 255, 255))
        title_rect = title.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 32))
        self.screen.blit(title, title_rect)

        # Список файлов
        if not self.available_files:
            self.available_files = self.get_available_files()

        # Область списка
        list_rect = pygame.Rect(dialog_rect.x + 20, dialog_rect.y + 60, 
                               dialog_rect.width - 40, dialog_rect.height - 120)
        pygame.draw.rect(self.screen, (30, 30, 35), list_rect, border_radius=8)
        pygame.draw.rect(self.screen, (60, 60, 70), list_rect, 1, border_radius=8)

        # Отрисовка файлов
        y = list_rect.y + 10
        for i, file in enumerate(self.available_files):
            item_rect = pygame.Rect(list_rect.x + 5, y, list_rect.width - 10, 30)
            if i == self.selected_file_index:
                pygame.draw.rect(self.screen, (0, 122, 204, 100), item_rect, border_radius=4)
                
            text = self.font.render(file, True, (255, 255, 255))
            self.screen.blit(text, (item_rect.x + 10, item_rect.y + 6))
            y += 35

        # Кнопки
        btn_w, btn_h = 120, 36
        btn_gap = 24  # Добавляем определение отступа между кнопками
        btn_y = dialog_rect.y + dialog_h - btn_h - 24
        
        # Кнопка "Открыть"
        open_rect = pygame.Rect(dialog_rect.centerx - btn_w - btn_gap//2, btn_y, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        open_color = (0, 122, 204) if open_rect.collidepoint(mouse_pos) else (30, 90, 160)
        pygame.draw.rect(self.screen, open_color, open_rect, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 200), open_rect, 2, border_radius=8)
        open_text = self.font.render("Открыть", True, (255,255,255))
        self.screen.blit(open_text, open_text.get_rect(center=open_rect.center))

        # Кнопка "Отмена"
        cancel_rect = pygame.Rect(dialog_rect.centerx + 12, btn_y, btn_w, btn_h)
        cancel_color = (60, 60, 70) if cancel_rect.collidepoint(mouse_pos) else (40, 40, 50)
        pygame.draw.rect(self.screen, cancel_color, cancel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 140), cancel_rect, 2, border_radius=8)
        cancel_text = self.font.render("Отмена", True, (220,220,220))
        self.screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))

        # Сохраняем ссылки на кнопки
        self.open_dialog_ok_rect = open_rect
        self.open_dialog_cancel_rect = cancel_rect

    def _handle_dialog_events(self, event):
        """Обработка событий диалоговых окон"""
        try:
            if self.open_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_open_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_open_dialog_click(event)
            # Проверяем остальные диалоги
            elif self.resize_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_resize_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_resize_dialog_click(event)
                    
            elif self.save_dialog_active:
                if event.type == pygame.KEYDOWN:
                    return self._handle_save_dialog_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return self._handle_save_dialog_click(event)
            
            return False

        except Exception as e:
            print(f"Ошибка диалога: {str(e)}")
            return False

    def _handle_open_dialog_key(self, event):
        """Обработка клавиш в диалоге открытия"""
        if event.key == pygame.K_ESCAPE:
            self.open_dialog_active = False
            self.files_search_logged = False  # Сбрасываем флаг при закрытии
        elif event.key == pygame.K_RETURN:
            self._apply_open()
        elif event.key == pygame.K_UP:
            self.selected_file_index = max(0, self.selected_file_index - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_file_index = min(len(self.available_files) - 1, self.selected_file_index + 1)
        return True

    def _handle_open_dialog_click(self, event):
        """Обработка кликов в диалоге открытия"""
        try:
            pos = pygame.mouse.get_pos()
            
            # Перемещаем проверку кнопки отмены в начало
            if self.open_dialog_cancel_rect and self.open_dialog_cancel_rect.collidepoint(pos):
                print("Нажата кнопка Отмена")
                self.open_dialog_active = False
                self.files_search_logged = False  # Сбрасываем флаг при закрытии
                return True
            
            # Проверяем клик по списку файлов, только если есть файлы
            if self.available_files:
                list_start_y = self.screen.get_height() // 2 - 100
                
                # Проверяем клик по каждому элементу списка
                for i, _ in enumerate(self.available_files):
                    item_rect = pygame.Rect(
                        self.screen.get_width() // 2 - 190,
                        list_start_y + (i * 35),
                        380,
                        30
                    )
                    if item_rect.collidepoint(pos):
                        self.selected_file_index = i
                        return True

                # Проверяем клик по кнопке открытия
                if self.open_dialog_ok_rect and self.open_dialog_ok_rect.collidepoint(pos):
                    print("Нажата кнопка Открыть")
                    self._apply_open()
                    return True
            
            return False

        except Exception as e:
            print(f"Ошибка при обработке клика диалога открытия: {str(e)}")
            return False

    def _apply_open(self):
        """Применение открытия файла"""
        try:
            if not self.available_files:
                print("Нет доступных файлов")
                return
                
            if 0 <= self.selected_file_index < len(self.available_files):
                filename = self.available_files[self.selected_file_index]
                print(f"Попытка открыть файл: {filename}")
                if self.load_project(filename):
                    print("Файл успешно загружен")
                    self.open_dialog_active = False
                else:
                    print("Не удалось загрузить файл")
        except Exception as e:
            print(f"Ошибка открытия файла: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_project(self, filename: str) -> bool:
        """Загрузка проекта из файла"""
        try:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
            filepath = os.path.join(save_dir, filename)
            
            print(f"Загрузка файла: {filepath}")
            
            if not os.path.exists(filepath):
                print(f"Файл не найден: {filepath}")
                return False
            
            try:
                loaded_surface = pygame.image.load(filepath)
                loaded_surface = loaded_surface.convert_alpha()
                print(f"Изображение загружено, размер: {loaded_surface.get_size()}")
                
                # Обновляем размер холста
                new_size = max(loaded_surface.get_width(), loaded_surface.get_height())
                self.grid_size = new_size
                self.canvas = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                self.canvas.fill((0, 0, 0, 0))
                
                # Копируем изображение
                x = (new_size - loaded_surface.get_width()) // 2
                y = (new_size - loaded_surface.get_height()) // 2
                self.canvas.blit(loaded_surface, (x, y))
                
                self.update_canvas_position()
                self.save_state()
                return True
                
            except pygame.error as e:
                print(f"Ошибка pygame при загрузке: {e}")
                return False
                
        except Exception as e:
            print(f"Ошибка загрузки проекта: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def undo(self):
        """Отмена последнего действия"""
        if self.history_index > 0:
            self.history_index -= 1
            self.canvas = self.history[self.history_index].copy()

    def redo(self):
        """Повтор отмененного действия"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.canvas = self.history[self.history_index].copy()

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        is_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        if is_fullscreen:
            self.screen = pygame.display.set_mode(
                (self.original_width, self.original_height),
                pygame.RESIZABLE
            )
        else:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN
            )
        self.update_canvas_position()

    def get_available_files(self) -> List[str]:
        """Получение списка доступных файлов"""
        try:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
            
            if not self.files_search_logged:
                print(f"Поиск файлов в директории: {save_dir}")
                self.files_search_logged = True
            
            if not os.path.exists(save_dir):
                if not self.files_search_logged:
                    print("Создание директории saves")
                os.makedirs(save_dir)
                return []
            
            files = [f for f in os.listdir(save_dir) if f.endswith('.png')]
            
            if not self.files_search_logged:
                if not files:
                    print("Файлы не найдены")
                else:
                    for file in files:
                        print(f"Найден файл: {file}")
            
            return sorted(files)
            
        except Exception as e:
            if not self.files_search_logged:
                print(f"Ошибка получения списка файлов: {str(e)}")
            return []
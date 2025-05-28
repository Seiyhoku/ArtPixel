import pygame
from typing import Tuple, Dict
from .constants import SHORTCUTS  # Добавляем импорт

class UI:
    def __init__(self, editor):
        self.editor = editor
        self.font = pygame.font.SysFont("Segoe UI", 12)
        self.large_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
        # Обновляем цветовую схему
        self.colors = {
            'bg': (18, 18, 18),
            'panel': (28, 28, 30),
            'button': (45, 45, 48),
            'button_hover': (55, 55, 58),
            'button_active': (0, 122, 204),
            'border': (64, 64, 70),
            'text': (230, 230, 230),
            'text_dim': (180, 180, 180),
            'accent': (0, 122, 204)
        }
    
        # Определяем все размеры сразу в начале
        self.side_panel_width = 200
        self.panel_margin = 10
        self.panel_spacing = 12
        self.panel_padding = 16
        self.button_height = 28  # Уменьшаем высоту кнопок
        self.button_spacing = 4  # Уменьшаем отступ между кнопками
        self.color_picker_height = 280  # Добавляем определение до создания rect'ов
        self.tools_panel_height = 440  # Уменьшаем высоту панели с 460 до 440

        # Вычисляем высоту информационной панели на основе количества строк
        base_info_lines = 2  # Базовая информация
        shortcut_lines = (
            1 +  # Заголовок "Управление"
            1 +  # СКМ
            1 +  # Пустая строка
            1 +  # Заголовок "Горячие клавиши"
            1 +  # Пустая строка
            1 +  # "Файл:"
            len(SHORTCUTS["FILE"]) +
            1 +  # Пустая строка
            1 +  # "Редактирование:"
            len(SHORTCUTS["EDIT"]) +
            1 +  # Пустая строка
            1 +  # "Холст:"
            len(SHORTCUTS["CANVAS"])
        )
        
        # Высота = отступ сверху + (количество строк * высота строки) + отступ снизу
        self.info_panel_height = 40 + ((base_info_lines + shortcut_lines) * 20) + 20

        # Теперь создаем все rect'ы
        self._setup_rects()
        
        # Кнопки инструментов
        self.tool_buttons: Dict[str, pygame.Rect] = {}
        
        # Создаем прямоугольники для всех элементов интерфейса
        self.clear_button_rect = None
        self.resize_button_rect = None
        self.open_button_rect = None  # Добавляем новый атрибут
        
        # Вызываем setup_tool_buttons после создания всех необходимых атрибутов
        self.setup_tool_buttons()
        
        # Добавляем атрибуты для HEX-редактора
        self.hex_input_rect = None
        self.hex_input_active = False

    def _setup_rects(self):
        """Централизованная настройка прямоугольников"""
        self.tools_panel_rect = pygame.Rect(
            self.panel_margin,
            self.panel_margin,
            self.side_panel_width - (self.panel_margin * 2),
            self.tools_panel_height
        )
        
        self.color_picker_rect = pygame.Rect(
            self.editor.screen.get_width() - self.side_panel_width + self.panel_margin,
            self.panel_margin,
            self.side_panel_width - (self.panel_margin * 2),
            self.color_picker_height
        )
        
        self.info_rect = pygame.Rect(
            self.panel_margin,
            self.tools_panel_rect.bottom + self.panel_spacing,
            self.side_panel_width - (self.panel_margin * 2),
            self.info_panel_height
        )

    def setup_tool_buttons(self) -> None:
        """Инициализация кнопок инструментов с улучшенным позиционированием"""
        # Вычисляем размеры с учетом отступов
        button_width = self.side_panel_width - (self.panel_padding * 3)
        
        # Начальная позиция после заголовка
        y = self.tools_panel_rect.y + 40
        
        # Инициализация кнопок инструментов в центре панели
        for tool in self.editor.tools.tools:
            rect = pygame.Rect(
                (self.side_panel_width - button_width) // 2,  # Центрирование по горизонтали
                y,
                button_width,
                self.button_height
            )
            self.tool_buttons[tool] = rect
            y += self.button_height + self.button_spacing
        
        # Добавляем разделитель перед утилитными кнопками
        y += self.button_spacing * 2
        
        # Утилитные кнопки
        self.tools_panel_height = 440  # Обновляем значение и тут

        self.clear_button_rect = pygame.Rect(
            (self.side_panel_width - button_width) // 2,
            y,
            button_width,
            self.button_height
        )
        
        y += self.button_height + self.button_spacing
        
        self.resize_button_rect = pygame.Rect(
            (self.side_panel_width - button_width) // 2,
            y,
            button_width,
            self.button_height
        )

        # Добавляем увеличенный отступ перед кнопкой сохранения
        y += self.button_height + (self.button_spacing * 4)  # Увеличиваем отступ в 4 раза
        
        # Кнопка открытия
        self.open_button_rect = pygame.Rect(
            (self.side_panel_width - button_width) // 2,
            y,
            button_width,
            self.button_height
        )
        
        y += self.button_height + (self.button_spacing * 4)  # Увеличиваем отступ в 4 раза

        # Кнопка сохранения последней
        self.save_button_rect = pygame.Rect(
            (self.side_panel_width - button_width) // 2,
            y,
            button_width,
            self.button_height
        )

    def draw(self) -> None:
        try:
            # Обновляем позицию цветовой панели при каждой отрисовке
            self.color_picker_rect.x = self.editor.screen.get_width() - self.side_panel_width + self.panel_margin
            
            # Рисуем основные панели и их фоны
            pygame.draw.rect(self.editor.screen, self.colors['bg'], 
                            (0, 0, self.side_panel_width, self.editor.screen.get_height()))
            pygame.draw.rect(self.editor.screen, self.colors['bg'], 
                            (self.editor.screen.get_width() - self.side_panel_width, 0, 
                             self.side_panel_width, self.editor.screen.get_height()))
        
            # Рисуем разделительные линии
            pygame.draw.line(self.editor.screen, self.colors['border'],
                            (self.side_panel_width, 0), 
                            (self.side_panel_width, self.editor.screen.get_height()), 2)
            pygame.draw.line(self.editor.screen, self.colors['border'],
                            (self.editor.screen.get_width() - self.side_panel_width, 0), 
                            (self.editor.screen.get_width() - self.side_panel_width, self.editor.screen.get_height()), 2)
        
            # Рисуем панели в правильном порядке с проверками
            if hasattr(self, 'tools_panel_rect'):
                self.draw_tools_panel()
            if hasattr(self, 'color_picker_rect'):
                self.draw_color_picker()
            if hasattr(self, 'info_rect'):
                self.draw_info_panel()
                
        except Exception as e:
            print(f"Ошибка отрисовки UI: {str(e)}")

    def draw_info_panel(self):
        """Отрисовка информационной панели"""
        # Рисуем информационную панель
        pygame.draw.rect(self.editor.screen, self.colors['panel'], self.info_rect, border_radius=8)
        pygame.draw.rect(self.editor.screen, self.colors['border'], self.info_rect, 1, border_radius=8)

        # Заголовок информационной панели
        title = self.large_font.render("Информация", True, self.colors['text'])
        self.editor.screen.blit(title, (self.info_rect.x + 10, self.info_rect.y + 10))

        # Базовая информация
        info_text = [
            f"Размер холста: {self.editor.grid_size}x{self.editor.grid_size}",
            f"Масштаб: {self.editor.zoom}x",
            "",
            "Управление:",
            "СКМ - Перемещение холста",
            "",
            "Горячие клавиши:",
            "",
            "Файл:",
            *[v for v in SHORTCUTS["FILE"].values()],
            "",
            "Редактирование:",
            *[v for v in SHORTCUTS["EDIT"].values()],
            "",
            "Холст:",
            *[v for v in SHORTCUTS["CANVAS"].values()]
        ]

        y = self.info_rect.y + 40
        for line in info_text:
            if (line.startswith("Файл:") or 
                line.startswith("Редактирование:") or 
                line.startswith("Холст:") or
                line.startswith("Управление:")):
                text = self.large_font.render(line, True, self.colors['text'])
            else:
                text = self.font.render(line, True, self.colors['text'])
            self.editor.screen.blit(text, (self.info_rect.x + 10, y))
            y += 20  # Отступ между строками

    def draw_tools_panel(self) -> None:
        # Рисуем фон панели инструментов
        pygame.draw.rect(self.editor.screen, self.colors['panel'], self.tools_panel_rect, border_radius=8)
        pygame.draw.rect(self.editor.screen, self.colors['border'], self.tools_panel_rect, 1, border_radius=8)
        
        # Заголовок по центру
        title = self.large_font.render("Инструменты", True, self.colors['text'])
        title_rect = title.get_rect(
            centerx=self.tools_panel_rect.centerx,
            top=self.tools_panel_rect.y + 12
        )
        self.editor.screen.blit(title, title_rect)
        
        # Отрисовка кнопок инструментов с улучшенной проверкой наведения
        mouse_pos = pygame.mouse.get_pos()
        
        for tool in self.editor.tools.tools:
            button_rect = self.tool_buttons[tool]
            is_selected = tool == self.editor.tools.current_tool
            is_hovered = self.check_button_hover(button_rect, mouse_pos)
            self.draw_tool_button(button_rect, tool, is_selected, is_hovered)

        # Отрисовка утилитных кнопок
        is_hovered = self.check_button_hover(self.clear_button_rect, mouse_pos)
        self.draw_tool_button(self.clear_button_rect, "Очистить", False, is_hovered)

        is_hovered = self.check_button_hover(self.resize_button_rect, mouse_pos)
        self.draw_tool_button(self.resize_button_rect, "Изменить размер", False, is_hovered)

        # Добавляем отрисовку кнопки открытия
        is_hovered = self.check_button_hover(self.open_button_rect, mouse_pos)
        self.draw_tool_button(self.open_button_rect, "Открыть", False, is_hovered)
        
        # Отрисовка кнопки сохранения
        is_hovered = self.check_button_hover(self.save_button_rect, mouse_pos)
        self.draw_tool_button(self.save_button_rect, "Сохранить", False, is_hovered)

    def draw_color_picker(self) -> None:
        """Оптимизированная отрисовка цветового пикера"""
        try:
            content_x = self.color_picker_rect.x + self.panel_padding
            content_y = self.color_picker_rect.y + 40
            
            rects = {
                'hue': (content_x, content_y, 20, self.editor.color_manager.sv_square_size),
                'sv': (content_x + 30, content_y, self.editor.color_manager.sv_square_size, self.editor.color_manager.sv_square_size),
                'alpha': (content_x, content_y + self.editor.color_manager.sv_square_size + 10, 
                         self.editor.color_manager.sv_square_size + 30, 15)
            }
            
            self.editor.color_manager.hue_bar_rect = pygame.Rect(*rects['hue'])
            self.editor.color_manager.sv_square_rect = pygame.Rect(*rects['sv'])
            self.editor.color_manager.alpha_bar_rect = pygame.Rect(*rects['alpha'])
            
            # Отрисовка компонентов
            self._draw_color_picker_components()
            pygame.display.update(self.color_picker_rect)
            
        except Exception as e:
            print(f"Ошибка Color Picker: {str(e)}")

    def _draw_color_picker_components(self):
        """Вспомогательный метод для отрисовки компонентов цветового пикера"""
        self.draw_panel_with_shadow(self.color_picker_rect, "Выбор цвета")
        self.draw_hue_bar()
        self.draw_sv_square()
        self.draw_alpha_bar()
        
        # Превью цвета
        preview_rect = pygame.Rect(
            self.color_picker_rect.x + self.panel_padding,
            self.editor.color_manager.alpha_bar_rect.bottom + 10,
            self.color_picker_rect.width - self.panel_padding * 2,
            60
        )
        self.draw_color_preview_enhanced(preview_rect)

    def draw_panel_with_shadow(self, rect, title):
        # Тень
        shadow = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 40))
        self.editor.screen.blit(shadow, (rect.x - 2, rect.y - 2))
        
        # Основная панель
        pygame.draw.rect(self.editor.screen, self.colors['panel'], rect, border_radius=10)
        pygame.draw.rect(self.editor.screen, self.colors['border'], rect, 1, border_radius=10)
        
        # Заголовок
        title_surf = self.large_font.render(title, True, self.colors['text'])
        self.editor.screen.blit(title_surf, (rect.x + 12, rect.y + 12))

    def draw_tool_button(self, rect: pygame.Rect, tool: str, active: bool, hovered: bool) -> None:
        if rect is None:  # Добавляем проверку
            return
        
        # Фон кнопки
        color = (
            self.colors['button_active'] if active else
            self.colors['button_hover'] if hovered else
            self.colors['button']
        )
        
        # Рисуем кнопку с эффектами
        pygame.draw.rect(self.editor.screen, color, rect, border_radius=8)
        if active or hovered:
            pygame.draw.rect(self.editor.screen, self.colors['accent'], rect, 2, border_radius=8)
        else:
            pygame.draw.rect(self.editor.screen, self.colors['border'], rect, 1, border_radius=8)
        
        # Текст инструмента
        text = self.font.render(tool, True, self.colors['text'])
        text_rect = text.get_rect(center=rect.center)
        self.editor.screen.blit(text, text_rect)

    def draw_color_preview_enhanced(self, rect):
        """Исправляем отображение текущего цвета."""
        padding = 10
        color_rect = rect.inflate(-padding, -padding)
        pygame.draw.rect(self.editor.screen, self.editor.color_manager.current_color, color_rect, border_radius=6)
        pygame.draw.rect(self.editor.screen, self.colors['border'], color_rect, 1, border_radius=6)

        # HEX-код
        hex_color = self.editor.color_manager.rgb_to_hex(self.editor.color_manager.current_color[:3])
        hex_text = self.font.render(hex_color, True, self.colors['text'])
        hex_rect = hex_text.get_rect(center=color_rect.center)
        self.editor.screen.blit(hex_text, hex_rect)

    def draw_transparency_bg(self, rect):
        # Рисует шахматный фон для отображения прозрачности
        square_size = 5
        for y in range(rect.height // square_size):
            for x in range(rect.width // square_size):
                color = (200, 200, 200) if (x + y) % 2 == 0 else (150, 150, 150)
                pygame.draw.rect(self.editor.screen, color, (
                    rect.x + x * square_size,
                    rect.y + y * square_size,
                    square_size, square_size
                ))

    def draw_hue_bar(self):
        rect = self.editor.color_manager.hue_bar_rect
        border = 2
        
        # Рисуем фон и рамку
        pygame.draw.rect(self.editor.screen, (40, 40, 45), rect.inflate(border*2, border*2), border_radius=4)
        
        # Рисуем градиент оттенков
        for y in range(rect.height):
            color = self.editor.color_manager.hsv_to_rgb(y / rect.height, 1, 1)
            pygame.draw.line(self.editor.screen, color, 
                           (rect.x, rect.y + y), 
                           (rect.right, rect.y + y))
        
        # Рисуем рамку
        pygame.draw.rect(self.editor.screen, self.editor.ui_accent_color, rect.inflate(border*2, border*2), 1, border_radius=4)
        
        # Индикатор текущего цвета
        curr_y = int(self.editor.color_manager.hue * rect.height)
        indicator_rect = pygame.Rect(rect.x - 3, rect.y + curr_y - 3, rect.width + 6, 6)
        pygame.draw.rect(self.editor.screen, (255, 255, 255), indicator_rect, border_radius=3)
        pygame.draw.rect(self.editor.screen, (40, 40, 45), indicator_rect, 1, border_radius=3)

    def draw_sv_square(self):
        rect = self.editor.color_manager.sv_square_rect
        border = 2
        
        # Рисуем фон и рамку
        pygame.draw.rect(self.editor.screen, (40, 40, 45), rect.inflate(border*2, border*2), border_radius=4)
        
        # Рисуем градиент насыщенности и яркости
        for y in range(rect.height):
            for x in range(rect.width):
                s = x / rect.width
                v = 1 - (y / rect.height)
                color = self.editor.color_manager.hsv_to_rgb(self.editor.color_manager.hue, s, v)
                pygame.draw.rect(self.editor.screen, color, (rect.x + x, rect.y + y, 1, 1))
        
        # Рисуем рамку
        pygame.draw.rect(self.editor.screen, self.editor.ui_accent_color, rect.inflate(border*2, border*2), 1, border_radius=4)
        
        # Индикатор выбранного цвета
        curr_x = int(self.editor.color_manager.sv_s * rect.width)
        curr_y = int((1 - self.editor.color_manager.sv_v) * rect.height)
        
        # Внешний круг
        pygame.draw.circle(self.editor.screen, (255, 255, 255), 
                         (rect.x + curr_x, rect.y + curr_y), 6)
        # Внутренний круг
        pygame.draw.circle(self.editor.screen, (40, 40, 45), 
                         (rect.x + curr_x, rect.y + curr_y), 5)

    def draw_alpha_bar(self):
        rect = self.editor.color_manager.alpha_bar_rect
        border = 2
        
        # Фон для прозрачности
        self.draw_transparency_bg(rect)
        
        # Рисуем градиент прозрачности
        for x in range(rect.width):
            alpha = x / rect.width
            color = (*self.editor.color_manager.current_color[:3], int(255 * alpha))
            pygame.draw.line(self.editor.screen, color,
                           (rect.x + x, rect.y),
                           (rect.x + x, rect.bottom))
        
        # Рамка
        pygame.draw.rect(self.editor.screen, self.editor.ui_accent_color, rect, 1)
        
        # Индикатор текущей прозрачности
        curr_x = int(self.editor.color_manager.alpha * rect.width)
        indicator_rect = pygame.Rect(rect.x + curr_x - 2, rect.y - 3, 4, rect.height + 6)
        pygame.draw.rect(self.editor.screen, (255, 255, 255), indicator_rect, border_radius=2)
        pygame.draw.rect(self.editor.screen, (40, 40, 45), indicator_rect, 1, border_radius=2)

    def check_button_hover(self, rect: pygame.Rect, pos: Tuple[int, int]) -> bool:
        """Проверка наведения на кнопку с уменьшенной зоной срабатывания"""
        if rect is None:
            return False
        
        # Создаем уменьшенный прямоугольник для проверки наведения
        hover_rect = rect.inflate(-4, -4)
        return hover_rect.collidepoint(pos)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Улучшенная обработка кликов по UI"""
        try:
            # Проверяем клик по цветовому пикеру
            if self.color_picker_rect.collidepoint(pos):
                result = self.editor.color_manager.handle_click(pos)
                return result

            # Перемещаем проверку кнопки открытия перед проверкой других кнопок
            if self.open_button_rect and self.open_button_rect.collidepoint(pos):
                print("Клик по кнопке Открыть")
                self.editor.open_dialog_active = True
                self.editor.selected_file_index = 0
                self.editor.files_scroll_offset = 0  # Сбрасываем скролл
                self.editor.available_files = self.editor.get_available_files()
                print(f"Найдены файлы: {self.editor.available_files}")
                return True

            # Остальные проверки
            if self.hex_input_rect and self.hex_input_rect.collidepoint(pos):
                self.hex_input_active = True
                return True

            for tool_name, rect in self.tool_buttons.items():
                if rect and rect.collidepoint(pos):
                    self.editor.tools.current_tool = tool_name
                    return True
            
            if self.clear_button_rect and self.clear_button_rect.collidepoint(pos):
                self.editor.clear_canvas()
                return True

            if self.resize_button_rect and self.resize_button_rect.collidepoint(pos):
                self.editor.resize_dialog_active = True
                return True

            if self.save_button_rect and self.save_button_rect.collidepoint(pos):
                self.editor.save_dialog_active = True
                return True

            return False

        except Exception as e:
            print(f"Ошибка обработки клика UI: {str(e)}")
            return False

        return False
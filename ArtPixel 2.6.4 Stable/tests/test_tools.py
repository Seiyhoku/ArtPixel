import unittest
import pygame
from editor.tools import Tools
from editor.core import PixelArtEditor

class TestTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        
    def setUp(self):
        self.editor = PixelArtEditor(grid_size=16, zoom=1)
        self.tools = Tools(self.editor)
        
    def tearDown(self):
        del self.editor
        del self.tools
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_initial_state(self):
        """Проверка начального состояния Tools"""
        self.assertEqual(self.tools.current_tool, "Карандаш")
        self.assertFalse(self.tools.drawing)
        self.assertIsNone(self.tools.start_pos)

    def test_tool_list(self):
        """Проверка списка инструментов"""
        expected_tools = ["Карандаш", "Ластик", "Заливка", "Пипетка", 
                         "Линия", "Прямоугольник", "Круг"]
        self.assertEqual(self.tools.get_tools(), expected_tools)

    def test_actions_list(self):
        """Проверка списка действий"""
        expected_actions = ["Очистить", "Размер", "Сохранить"]
        self.assertEqual(self.tools.get_actions(), expected_actions)

    def test_draw_pixel(self):
        """Проверка рисования пикселя"""
        test_pos = (5, 5)
        self.tools.current_tool = "Карандаш"
        self.tools.handle_tool_action(test_pos)
        color = self.editor.canvas.get_at(test_pos)
        self.assertEqual(color, self.editor.color_manager.current_color)

    def test_flood_fill(self):
        """Проверка заливки"""
        # Рисуем пиксель
        self.editor.draw_pixel((5, 5), (255, 0, 0, 255))
        
        # Заливаем область другим цветом
        self.tools.current_tool = "Заливка"
        self.editor.color_manager.current_color = (0, 255, 0, 255)
        self.tools.handle_tool_action((5, 5))
        
        # Проверяем результат
        filled_color = self.editor.canvas.get_at((5, 5))
        self.assertEqual(filled_color, (0, 255, 0, 255))

    def test_eraser(self):
        """Проверка работы ластика"""
        # Рисуем пиксель
        test_pos = (5, 5)
        self.tools.current_tool = "Карандаш"
        self.tools.handle_tool_action(test_pos)
        
        # Стираем его
        self.tools.current_tool = "Ластик"
        self.tools.handle_tool_action(test_pos)
        
        # Проверяем что пиксель стерт (прозрачен)
        color = self.editor.canvas.get_at(test_pos)
        self.assertEqual(color[3], 0)  # Альфа-канал должен быть 0

    def test_color_picker(self):
        """Проверка работы пипетки"""
        # Рисуем пиксель определенного цвета
        test_pos = (5, 5)
        test_color = (255, 0, 0, 255)
        self.editor.draw_pixel(test_pos, test_color)
        
        # Используем пипетку
        self.tools.current_tool = "Пипетка"
        self.tools.handle_tool_action(test_pos)
        
        # Проверяем что цвет установлен правильно
        self.assertEqual(self.editor.color_manager.current_color, test_color)

    def test_line_tool(self):
        """Проверка инструмента линии"""
        self.tools.current_tool = "Линия"
        start_pos = (1, 1)
        end_pos = (5, 5)
        
        # Начинаем рисовать линию
        self.tools.handle_tool_action(start_pos)
        self.assertEqual(self.tools.start_pos, start_pos)
        
        # Заканчиваем линию
        self.tools.drawing = True
        self.tools.handle_tool_action(end_pos)
        
        # Проверяем что точки линии нарисованы
        self.assertEqual(
            self.editor.canvas.get_at(start_pos),
            self.editor.canvas.get_at(end_pos)
        )

    def test_clear_action(self):
        """Проверка очистки холста"""
        # Рисуем что-то на холсте
        self.editor.draw_pixel((5, 5), (255, 0, 0, 255))
        
        # Очищаем холст
        self.editor.clear_canvas()
        
        # Проверяем что все пиксели прозрачные
        for x in range(self.editor.grid_size):
            for y in range(self.editor.grid_size):
                self.assertEqual(
                    self.editor.canvas.get_at((x, y))[3], 
                    0
                )

if __name__ == '__main__':
    unittest.main()
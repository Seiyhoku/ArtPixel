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

if __name__ == '__main__':
    unittest.main()
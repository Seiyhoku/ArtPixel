import unittest
import pygame
import colorsys
from editor.color import ColorManager
from editor.core import PixelArtEditor

class TestColorManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        
    def setUp(self):
        self.editor = PixelArtEditor(grid_size=16, zoom=1)
        self.color_manager = ColorManager(self.editor)

    def tearDown(self):
        del self.editor
        del self.color_manager
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_initial_state(self):
        """Проверка начального состояния ColorManager"""
        self.assertEqual(self.color_manager.current_color, (255, 255, 255, 255))
        self.assertEqual(self.color_manager.hue, 0.0)
        self.assertEqual(self.color_manager.alpha, 1.0)
        self.assertEqual(self.color_manager.sv_s, 1.0)
        self.assertEqual(self.color_manager.sv_v, 1.0)

    def test_set_color(self):
        """Проверка установки цвета"""
        test_color = (128, 64, 32)
        self.color_manager.set_color(test_color)
        self.assertEqual(self.color_manager.current_color[:3], test_color)
        self.assertEqual(self.color_manager.current_color[3], 255)  # Альфа канал

    def test_update_hue(self):
        """Проверка обновления оттенка"""
        self.color_manager.update_hue(60)  # 60 пикселей из 120 = 0.5
        self.assertAlmostEqual(self.color_manager.hue, 0.5, places=2)

    def test_update_sv(self):
        """Проверка обновления насыщенности и яркости"""
        self.color_manager.update_sv((60, 60))  # Половина от размера квадрата
        self.assertAlmostEqual(self.color_manager.sv_s, 0.5, places=2)
        self.assertAlmostEqual(self.color_manager.sv_v, 0.5, places=2)

    def test_update_alpha(self):
        """Проверка обновления прозрачности"""
        self.color_manager.update_alpha(75)  # Корректируем входное значение для получения 0.5
        self.assertAlmostEqual(self.color_manager.alpha, 0.5, places=2)

    def test_hsv_to_rgb(self):
        """Проверка конвертации HSV в RGB"""
        test_cases = [
            ((0.0, 1.0, 1.0), (255, 0, 0)),    # Красный
            ((0.333, 1.0, 1.0), (0, 255, 0)),  # Зеленый
            ((0.666, 1.0, 1.0), (0, 0, 255)),  # Синий
            ((0.0, 0.0, 1.0), (255, 255, 255)) # Белый
        ]
        
        for hsv, expected_rgb in test_cases:
            with self.subTest(hsv=hsv, expected_rgb=expected_rgb):
                result = self.color_manager.hsv_to_rgb(*hsv)
                for actual, expected in zip(result, expected_rgb):
                    self.assertAlmostEqual(actual, expected, delta=1)

    def test_rgb_to_hex(self):
        """Проверка конвертации RGB в HEX"""
        test_cases = [
            ((255, 0, 0), '#FF0000'),
            ((0, 255, 0), '#00FF00'),
            ((0, 0, 255), '#0000FF'),
            ((255, 255, 255), '#FFFFFF')
        ]
        
        for rgb, expected_hex in test_cases:
            with self.subTest(rgb=rgb, expected_hex=expected_hex):
                result = self.color_manager.rgb_to_hex(rgb)
                self.assertEqual(result.upper(), expected_hex)

    def test_boundary_values(self):
        """Проверка граничных значений"""
        # Проверка максимальных значений
        self.color_manager.update_hue(self.color_manager.sv_square_size)
        self.assertEqual(self.color_manager.hue, 1.0)
        
        self.color_manager.update_sv((self.color_manager.sv_square_size, 0))
        self.assertEqual(self.color_manager.sv_s, 1.0)
        self.assertEqual(self.color_manager.sv_v, 1.0)
        
        self.color_manager.update_alpha(self.color_manager.sv_square_size + 30)
        self.assertEqual(self.color_manager.alpha, 1.0)
        
        # Проверка минимальных значений
        self.color_manager.update_hue(0)
        self.assertEqual(self.color_manager.hue, 0.0)
        
        self.color_manager.update_sv((0, self.color_manager.sv_square_size))
        self.assertEqual(self.color_manager.sv_s, 0.0)
        self.assertEqual(self.color_manager.sv_v, 0.0)
        
        self.color_manager.update_alpha(0)
        self.assertEqual(self.color_manager.alpha, 0.0)

    def test_negative_values(self):
        """Проверка отрицательных значений"""
        old_color = self.color_manager.current_color
        
        self.color_manager.update_hue(-1)
        self.color_manager.update_sv((-1, -1))
        self.color_manager.update_alpha(-1)
        
        self.assertEqual(self.color_manager.current_color, old_color)

    def test_color_conversion(self):
        """Проверка конвертации цветов"""
        # HSV -> RGB
        rgb = self.color_manager.hsv_to_rgb(0, 1, 1)  # Красный
        self.assertEqual(rgb, (255, 0, 0))
        
        rgb = self.color_manager.hsv_to_rgb(0.33, 1, 1)  # Зеленый
        self.assertAlmostEqual(rgb[1], 255, delta=1)
        
        # RGB -> HEX
        self.assertEqual(self.color_manager.rgb_to_hex((255, 0, 0)), '#FF0000')
        self.assertEqual(self.color_manager.rgb_to_hex((0, 255, 0)), '#00FF00')
        self.assertEqual(self.color_manager.rgb_to_hex((0, 0, 255)), '#0000FF')

if __name__ == '__main__':
    unittest.main()
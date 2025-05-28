import unittest
import pygame
import os
import shutil
import json
from editor.file_io import save_to_json, load_from_json, save_artwork

class TestFileIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Создаем тестовую директорию
        cls.test_dir = os.path.join(os.path.dirname(__file__), "test_files")
        os.makedirs(cls.test_dir, exist_ok=True)
        
    def setUp(self):
        self.test_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.test_surface.fill((255, 0, 0, 255))
        # Используем полный путь для файла
        self.test_filename = os.path.join(self.test_dir, "test_artwork")
        
    def tearDown(self):
        # Удаляем тестовые файлы
        for ext in ['.png', '.json']:
            test_file = f"{self.test_filename}{ext}"
            if os.path.exists(test_file):
                os.remove(test_file)
                
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        # Рекурсивно удаляем тестовую директорию
        try:
            if os.path.exists(cls.test_dir):
                shutil.rmtree(cls.test_dir)
        except Exception as e:
            print(f"Ошибка при удалении тестовой директории: {e}")
            # Не вызываем исключение, чтобы тесты могли завершиться
            pass

    def test_save_load_json(self):
        """Проверка сохранения и загрузки JSON"""
        # Сохраняем
        save_to_json(self.test_surface, f"{self.test_filename}.json")
        self.assertTrue(os.path.exists(f"{self.test_filename}.json"))
        
        # Загружаем
        loaded_surface = load_from_json(f"{self.test_filename}.json")
        self.assertEqual(
            self.test_surface.get_at((0, 0)),
            loaded_surface.get_at((0, 0))
        )

    def test_save_artwork(self):
        """Проверка сохранения изображения"""
        png_path, json_path = save_artwork(self.test_surface, self.test_filename)
        
        self.assertTrue(os.path.exists(png_path))
        self.assertTrue(os.path.exists(json_path))
        
        # Проверяем содержимое JSON
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['width'], 16)
            self.assertEqual(data['height'], 16)

    def test_invalid_file(self):
        """Проверка обработки неправильного файла"""
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
            
        with self.assertRaises(Exception):
            load_from_json(invalid_file)
            
    def test_empty_surface(self):
        """Проверка сохранения пустого холста"""
        empty_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        
        # Сохраняем пустой холст
        png_path, json_path = save_artwork(empty_surface, self.test_filename)
        
        # Проверяем что файлы созданы
        self.assertTrue(os.path.exists(png_path))
        self.assertTrue(os.path.exists(json_path))
        
        # Загружаем и проверяем содержимое
        loaded_surface = load_from_json(json_path)
        self.assertEqual(loaded_surface.get_size(), (16, 16))
        
    def test_file_overwrite(self):
        """Проверка перезаписи существующего файла"""
        # Сохраняем первый раз
        save_artwork(self.test_surface, self.test_filename)
        
        # Меняем цвет и сохраняем второй раз
        new_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        new_surface.fill((0, 255, 0, 255))
        png_path, json_path = save_artwork(new_surface, self.test_filename)
        
        # Проверяем что цвет изменился
        loaded_surface = load_from_json(json_path)
        self.assertEqual(
            loaded_surface.get_at((0, 0)),
            (0, 255, 0, 255)
        )

if __name__ == '__main__':
    unittest.main()
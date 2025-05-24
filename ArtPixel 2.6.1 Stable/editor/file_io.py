import pygame
import json
import os
from typing import Dict, List, Tuple

def save_to_json(surface: pygame.Surface, filename: str) -> None:
    """Сохраняет пиксельное изображение в JSON файл"""
    if not filename.endswith('.json'):
        filename += '.json'
    
    pixels = []
    for y in range(surface.get_height()):
        row = []
        for x in range(surface.get_width()):
            color = surface.get_at((x, y))
            row.append({
                'r': color.r,
                'g': color.g,
                'b': color.b,
                'a': color.a
            })
        pixels.append(row)
    
    data = {
        'width': surface.get_width(),
        'height': surface.get_height(),
        'pixels': pixels
    }
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_json(filename: str) -> pygame.Surface:
    """Загружает пиксельное изображение из JSON файла"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    surface = pygame.Surface((data['width'], data['height']), pygame.SRCALPHA)
    for y, row in enumerate(data['pixels']):
        for x, pixel in enumerate(row):
            color = (
                pixel['r'],
                pixel['g'],
                pixel['b'],
                pixel['a']
            )
            surface.set_at((x, y), color)
    
    return surface

def save_artwork(surface: pygame.Surface, name: str = None) -> Tuple[str, str]:
    """Сохраняет изображение в форматах PNG и JSON"""
    # Создаем папку saves в директории проекта
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Генерируем имя файла
    if name is None:
        counter = 1
        while True:
            base_name = f"artwork_{counter}"
            if not os.path.exists(os.path.join(save_dir, f"{base_name}.png")) and \
               not os.path.exists(os.path.join(save_dir, f"{base_name}.json")):
                name = base_name
                break
            counter += 1
    
    # Сохраняем PNG
    png_path = os.path.join(save_dir, f"{name}.png")
    pygame.image.save(surface, png_path)
    
    # Сохраняем JSON
    json_path = os.path.join(save_dir, f"{name}.json")
    save_to_json(surface, json_path)
    
    print(f"Файлы сохранены в {save_dir}")
    return png_path, json_path

def get_save_directory() -> str:
    """Возвращает путь к директории с сохранениями"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")

def get_available_files() -> List[str]:
    """Получает список доступных файлов проектов"""
    save_dir = get_save_directory()
    if not os.path.exists(save_dir):
        return []
        
    files = []
    for file in os.listdir(save_dir):
        if file.endswith('.json'):
            files.append(file)
    return sorted(files)

def load_project(filename: str, editor) -> bool:
    """Загружает проект из файла"""
    try:
        filepath = os.path.join(get_save_directory(), filename)
        if not os.path.exists(filepath):
            return False
            
        loaded_surface = load_from_json(filepath)
        if loaded_surface:
            editor.grid_size = loaded_surface.get_width()
            editor.canvas = loaded_surface
            editor.update_canvas_position()
            editor.save_state()
            return True
            
    except Exception as e:
        print(f"Ошибка загрузки проекта: {str(e)}")
        return False
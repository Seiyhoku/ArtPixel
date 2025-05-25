import pygame
import sys
import traceback
import logging
from editor.core import PixelArtEditor

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

def handle_pygame_events():
    """Обработчик событий pygame для отладки"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        logging.debug(f"Pygame Event: {event}")
    return True

def main():
    try:
        pygame.init()
        logging.info("Pygame initialized")
        
        editor = PixelArtEditor(grid_size=32, zoom=16)
        logging.info("Editor created successfully")
        logging.info(f"Canvas size: {editor.grid_size}x{editor.grid_size}")
        logging.info(f"Initial zoom: {editor.zoom}")
        
        editor.run()
        
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        logging.critical(traceback.format_exc())
    finally:
        pygame.quit()
        logging.info("Application terminated")

if __name__ == "__main__":
    main()
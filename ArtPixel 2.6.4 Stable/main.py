import pygame
import sys
import os
import traceback
import logging
import time
from editor.core import PixelArtEditor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def safe_exit(editor=None):
    """Безопасное завершение программы"""
    try:
        if editor and not editor.is_closing:
            logging.info("Завершение работы редактора...")
            editor.shutdown()
            time.sleep(0.15)  # Задержка для разделения логов
            
        logging.info("Выполняется выход из программы...")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        logging.error(f"Ошибка при выходе: {e}")
        os._exit(1)

def main():
    editor = None
    try:
        pygame.init()
        logging.info("Инициализация Pygame завершена")
        
        editor = PixelArtEditor(grid_size=32, zoom=16)
        logging.info("Редактор успешно создан и готов к работе")
        
        editor.run()
    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}")
        logging.critical(traceback.format_exc())
    finally:
        safe_exit(editor)

if __name__ == "__main__":
    main()
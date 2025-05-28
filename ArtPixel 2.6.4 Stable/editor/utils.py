import logging
import sys
import os

def setup_logger():
    """Настройка логгера с проверками и безопасной инициализацией"""
    try:
        # Если логгер уже настроен, пропускаем
        if logging.getLogger().handlers:
            return True
            
        # Создаем директорию для логов если её нет
        log_dir = os.path.dirname(os.path.dirname(__file__))
        log_file = os.path.join(log_dir, 'debug.log')
        os.makedirs(log_dir, exist_ok=True)
        
        # Очищаем старые хендлеры
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        # Настройка форматирования
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        # Файловый хендлер с проверкой прав доступа
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except PermissionError:
            print(f"Нет прав на запись в файл {log_file}")
            
        # Консольный хендлер
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Устанавливаем уровень логирования
        logger.setLevel(logging.INFO)
        
        # Проверяем работоспособность
        logger.info("Логгер успешно инициализирован")
        return True
        
    except Exception as e:
        print(f"Критическая ошибка при настройке логгера: {str(e)}")
        return False

def log_message(message: str, level: str = "INFO") -> bool:
    """Безопасное логирование с проверкой успешности"""
    try:
        level = level.upper()
        logger = logging.getLogger()
        
        if not logger.handlers:
            if not setup_logger():
                return False
                
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "DEBUG":
            logger.debug(message)
        else:
            logger.info(message)
            
        return True
        
    except Exception as e:
        print(f"Ошибка логирования: {str(e)}")
        return False

# ArtPixel 2.6.4 - Редактор пиксельной графики

## 📝 Описание
ArtPixel 2.6.4 - Это современный редактор пиксельной графики с интуитивным интерфейсом, разработанный на Python с использованием Pygame, с открытым исходным кодом.

## 🔧 Системные требования
- Python 3.8+
- Pygame 2.0+
- Windows 10/11

## 📥 Установка

1. **Клонирование репозитория:**
```bash
git clone https://github.com/yourusername/ArtPixel.git
cd ArtPixel
```

2. **Настройка виртуального окружения:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

## 🎨 Возможности

### Основные функции
- Перемещение холста с помощью средней кнопки мыши (СКМ)
- Масштабирование с помощью Alt + колесо мыши
- Прозрачный предпросмотр фигур
- Поддержка прозрачности (альфа-канал)
- Сохранение в PNG

### Инструменты
| Инструмент | Описание |
|------------|----------|
| 🖊️ Карандаш | Рисование отдельных пикселей |
| ⬜ Ластик | Удаление пикселей |
| 🪣 Заливка | Заливка области одним цветом |
| 👆 Пипетка | Выбор цвета с холста |
| 📏 Линия | Рисование прямых линий с предпросмотром |
| 🟥 Прямоугольник | Создание контуров прямоугольников |
| ⭕ Круг | Рисование окружностей |

### Работа с цветом
- HSV палитра с визуальным выбором
- Настройка прозрачности
- Предпросмотр текущего цвета
- Отображение HEX-кода цвета

### Файловые операции
- Сохранение в PNG
- Открытие существующих проектов
- Изменение размера холста

Перед запуском тестов убедитесь, что:
- Активировано виртуальное окружение
- Установлены все зависимости из requirements.txt
- Вы находитесь в корневой директории проекта

## ⌨️ Горячие клавиши
| Комбинация | Действие |
|------------|----------|
| `Ctrl+Z` | Отмена действия |
| `Ctrl+Y` | Повтор действия |
| `Ctrl+S` | Сохранить |
| `Ctrl+O` | Открыть |
| `Ctrl+C` | Очистить холст |
| `F11` | Полноэкранный режим |
| `G` | Показать/скрыть сетку |
| `R` | Изменить размер холста |
| `Esc` | Выход |

## 📁 Структура проекта
```
ArtPixel/
├── editor/
│   ├── __init__.py
│   ├── color.py     # Управление цветом
│   ├── tools.py     # Инструменты рисования
│   ├── core.py      # Основная логика
│   ├── ui.py        # Интерфейс
│   └── constants.py # Константы
├── saves/           # Папка для сохранений
└── main.py
```

## 🧪 Тестирование

### Запуск всех тестов
```bash
python -m unittest discover tests
```

### Запуск отдельных тестовых модулей
```bash
# Тесты для работы с цветом
python -m unittest tests.test_color

# Тесты для работы с файлами
python -m unittest tests.test_file_io

# Тесты для инструментов
python -m unittest tests.test_tools
```

### Структура тестов
```
tests/
├── __init__.py
├── test_color.py     # Тесты управления цветом
├── test_file_io.py   # Тесты файловых операций
└── test_tools.py     # Тесты инструментов рисования
```

## ⚠️ Известные особенности
- Папка "saves" создается при первом сохранении
- Размер холста: от 2x2 до 256x256 пикселей
- Масштаб: от 2x до 50x

## 🔄 Версия
Текущая версия: 2.6.4 Stable
Дата релиза: 25 май 2025 г.

---
© 2025 ArtPixel. Все права защищены.

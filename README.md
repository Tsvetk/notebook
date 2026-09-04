🗂️ NavigableNotebook - Advanced Tkinter Notebook Widget
========================================================

**A feature-rich, highly customizable tab control for Tkinter with navigation buttons, drag-and-drop, and interactive tab management.**

✨ Key Features
--------------

*   **Complete Navigation Suite**: First, Previous, Next, Last buttons with customizable visibility

*   **Tab Management**: Add, close, rename, duplicate tabs with intuitive controls

*   **Drag & Drop Support**: Reorder tabs by dragging them

*   **Dynamic Tab Visibility**: Automatically hides tabs when they don't fit, with smooth scrolling

*   **Interactive Controls**: Label-based buttons with tooltips and visual feedback

*   **Customizable Layout**: Control which buttons appear and where (left or right side)

*   **Keyboard Shortcuts**: Ctrl+Tab, Ctrl+Shift+Tab, mouse wheel support

*   **Context Menus**: Right-click and dropdown menus for quick actions

*   **Visual Themes**: Customizable colors, fonts, and styling


🚀 Quick Example
----------------

```python
import tkinter as tk
from tabs_class import NavigableNotebook

root = tk.Tk()
notebook = NavigableNotebook(root, tooltip=True, cyclically=True)
notebook.pack(expand=True, fill='both')

# Add some tabs
for i in range(5):
    notebook.add_new_tab(text=f"Tab {i+1}")

root.mainloop()
```
📦 Installation
---------------

Simply copy `tabs_class.py` to your project and import it.

bash

pip install tkinter  \# Usually pre-installed with Python

🎛️ Configuration Options
-------------------------

| Parameter | Type | Description |
| ------- | ------- | ------- |
| order | dict | Control visibility of all button groups |
| tooltip | bool | Enable/disable tooltips |
| enable_close | bool | Show/hide close buttons on tabs |
| cyclically | bool | Allow cyclic tab navigation |
| font | tuple | Font for tab labels and buttons |
| color | dict | Colors for buttons and text |
| color_bg | dict | Background colors for hover states |

### Button Groups

```python
order = {
    'first': {'visible': True},    # First tab
    'prev': {'visible': True},     # Previous tab
    'counter': {'visible': True},  # Tab counter (e.g., "3/10")
    'close': {'visible': True},    # Close current tab
    'add': {'visible': True},      # Add new tab
    'menu': {'visible': True},     # Context menu
    'next': {'visible': True},     # Next tab
    'last': {'visible': True}      # Last tab
}
```

🛠️ Available Methods
---------------------

### Tab Management

*   `add_new_tab(text=None, content=None)` - Create a new tab

*   `close_current_tab()` - Close the active tab

*   `close_tab(index)` - Close a specific tab

*   `close_other_tabs()` - Close all tabs except current

*   `rename_current_tab()` - Rename active tab

*   `rename_tab(index, new_text)` - Rename a specific tab

*   `duplicate_current_tab()` - Create a copy of current tab


### Navigation

*   `go_to_first()`, `go_to_last()` - Jump to first/last tab

*   `go_to_prev()`, `go_to_next()` - Navigate sequentially


### Visibility Control

*   `show_button_group(group_name, visible)` - Show/hide button groups

*   `get_button_state(group_name)` - Get current visibility state


### Information

*   `get_tabs_info()` - Get list of all tabs

*   `get_current_tab_info()` - Get current tab details


🎨 Customization Examples
-------------------------

### Minimal Setup

```python
notebook = NavigableNotebook( root,
    font=('Arial', 12)
)
```
### Complete Customization

```python
notebook = NavigableNotebook(
    root,
    order={
        'first': {'visible': True, 'setting': {'text': '⏮'}},
        'prev': {'visible': True},
        'counter': {'visible': True},
        'close': {'visible': True},
        'add': {'visible': True, 'setting': {'text': '➕'}},
        'menu': {'visible': True, 'right': False},
        'next': {'visible': True},
        'last': {'visible': True}
    },
    font=('Tahoma', 11, 'bold'),
    color={'bg': '#2c3e50', 'fg': '#ecf0f1'},
    tooltip=True,
    cyclically=True
)
```
🖥️ Demo Application
--------------------

The included `DemoApp` demonstrates multiple configurations:

*   **Full Setup**: All features enabled

*   **Minimal**: Essential buttons only

*   **Navigation Only**: Just navigation controls

*   **Management Only**: Tab management features only

*   **Custom**: Unique layout with custom labels


Run the demo:

bash

python tabs\_class.py

🤝 Contributing
---------------

Contributions are welcome! Please feel free to submit issues, feature requests

* * *

🗂️ NavigableNotebook - Расширенный виджет вкладок для Tkinter
==============================================================

**Многофункциональный, высоконастраиваемый элемент управления вкладками для Tkinter с кнопками навигации, перетаскиванием и интерактивным управлением вкладками.**

✨ Основные возможности
----------------------

*   **Полный набор навигации**: Кнопки "Первая", "Предыдущая", "Следующая", "Последняя" с настраиваемой видимостью

*   **Управление вкладками**: Добавление, закрытие, переименование, дублирование с интуитивным управлением

*   **Поддержка Drag & Drop**: Изменение порядка вкладок перетаскиванием

*   **Динамическая видимость**: Автоматическое скрытие вкладок при переполнении с плавной прокруткой

*   **Интерактивные элементы**: Кнопки на основе Label с подсказками и визуальной обратной связью

*   **Настраиваемая компоновка**: Управление видимостью и расположением кнопок

*   **Горячие клавиши**: Ctrl+Tab, Ctrl+Shift+Tab, поддержка колесика мыши

*   **Контекстные меню**: Быстрые действия через выпадающие меню

*   **Визуальные темы**: Настраиваемые цвета, шрифты и стили


🚀 Быстрый пример
-----------------

```python
import tkinter as tk
from tabs_class import NavigableNotebook

root = tk.Tk()
notebook = NavigableNotebook(root, tooltip=True, cyclically=True)
notebook.pack(expand=True, fill='both')

# Добавляем вкладки
for i in range(5):
    notebook.add_new_tab(text=f"Вкладка {i+1}")

root.mainloop()
```

📦 Установка
------------

Просто скопируйте файл `tabs_class.py` в ваш проект и импортируйте.

bash

pip install tkinter  \# Обычно уже установлен с Python

🎛️ Параметры настройки
-----------------------
| Параметр | Тип | Описание |
| ------- | ------- | ------- |
| order | dict | Управление видимостью групп кнопок |
| tooltip | bool | Включение/отключение всплывающих подсказок |
| enable_close | bool | Отображение кнопок закрытия на вкладках |
| cyclically | bool | Циклическая навигация по вкладкам |
| font | tuple | Шрифт для вкладок и кнопок |
| color | dict | Цвета кнопок и текста |
| color_bg | dict | Цвета фона при наведении |

### Группы кнопок

```python
order = {
    'first': {'visible': True},    # Первая вкладка
    'prev': {'visible': True},     # Предыдущая вкладка
    'counter': {'visible': True},  # Счетчик вкладок (напр., "3/10")
    'close': {'visible': True},    # Закрыть текущую вкладку
    'add': {'visible': True},      # Добавить вкладку
    'menu': {'visible': True},     # Контекстное меню
    'next': {'visible': True},     # Следующая вкладка
    'last': {'visible': True}      # Последняя вкладка
}
```

🛠️ Доступные методы
--------------------

### Управление вкладками

*   `add_new_tab(text=None, content=None)` - Создать новую вкладку

*   `close_current_tab()` - Закрыть активную вкладку

*   `close_tab(index)` - Закрыть конкретную вкладку

*   `close_other_tabs()` - Закрыть все вкладки кроме текущей

*   `rename_current_tab()` - Переименовать активную вкладку

*   `rename_tab(index, new_text)` - Переименовать конкретную вкладку

*   `duplicate_current_tab()` - Создать копию текущей вкладки


### Навигация

*   `go_to_first()`, `go_to_last()` - Перейти к первой/последней вкладке

*   `go_to_prev()`, `go_to_next()` - Последовательная навигация


### Управление видимостью

*   `show_button_group(group_name, visible)` - Показать/скрыть группы кнопок

*   `get_button_state(group_name)` - Получить текущее состояние видимости


### Информация

*   `get_tabs_info()` - Получить список всех вкладок

*   `get_current_tab_info()` - Получить информацию о текущей вкладке


🎨 Примеры настройки
--------------------

### Минимальная конфигурация

```python
notebook = NavigableNotebook(
    root,
    font=('Arial', 12)
)
```

### Полная кастомизация

```python
notebook = NavigableNotebook(
    root,
    order={
        'first': {'visible': True, 'setting': {'text': '⏮'}},
        'prev': {'visible': True},
        'counter': {'visible': True},
        'close': {'visible': True},
        'add': {'visible': True, 'setting': {'text': '➕'}},
        'menu': {'visible': True, 'right': False},
        'next': {'visible': True},
        'last': {'visible': True}
    },
    font=('Tahoma', 11, 'bold'),
    color={'bg': '#2c3e50', 'fg': '#ecf0f1'},
    tooltip=True,
    cyclically=True
)
```

🖥️ Демонстрационное приложение
-------------------------------

Включенный `DemoApp` демонстрирует несколько конфигураций:

*   **Полная**: Все функции включены

*   **Минимальная**: Только необходимые кнопки

*   **Только навигация**: Только элементы управления

*   **Только управление**: Только функции управления вкладками

*   **Пользовательская**: Уникальная компоновка с пользовательскими метками


Запуск демо:

bash

python tabs\_class\.py

🤝 Вклад в проект
-----------------

Приветствуются любые вклады! Пожалуйста, не стесняйтесь отправлять вопросы, запросы на новые функции

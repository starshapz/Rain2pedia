import sys
import csv
import sqlite3
import random
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QPushButton, QLabel,
                             QDialog, QTextEdit, QFileDialog, QMessageBox,
                             QHeaderView, QFormLayout, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor


class Item:
    # класс для представления предметов

    RARITY_COLORS = {
        "Обычный": QColor(200, 200, 200),  # серый
        "Необычный": QColor(75, 139, 59),  # зеленый
        "Легендарный": QColor(255, 215, 0),  # золотой
        "Босс": QColor(255, 69, 0),  # оранжево-красный
        "Лунный": QColor(0, 191, 255),  # голубой
        "Снаряжение": QColor(147, 112, 219),  # фиолетовый
        "Бездонный": QColor(138, 43, 226)  # темно-фиолетовый
    }

    RARITY_ORDER = {"Обычный": 0, "Необычный": 1, "Легендарный": 2,
                    "Босс": 3, "Лунный": 4, "Снаряжение": 5, "Бездонный": 6}

    def __init__(self, name, rarity, desc, effect):
        self.name = name
        self.rarity = rarity
        self.desc = desc
        self.effect = effect

    def get_rarity_color(self):
        # возвращает цвет для редкости предмета
        return self.RARITY_COLORS.get(self.rarity, QColor(200, 200, 200))

    def get_rarity_order(self):
        # возвращает порядковый номер редкости для сортировки
        return self.RARITY_ORDER.get(self.rarity, 0)


class DatabaseManager:
    # менеджер базы данных sqlite

    def __init__(self, db_path="items.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        # инициализация базы данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rarity TEXT NOT NULL,
                desc TEXT NOT NULL,
                effect TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_items(self):
        # получает все предметы из базы данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, rarity, desc, effect FROM items")
        items_data = cursor.fetchall()
        conn.close()

        items = []
        for name, rarity, desc, effect in items_data:
            items.append(Item(name, rarity, desc, effect))
        return items

    def add_item(self, item):
        # добавляет предмет в базу данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, rarity, desc, effect) VALUES (?, ?, ?, ?)",
            (item.name, item.rarity, item.desc, item.effect)
        )
        conn.commit()
        conn.close()

    def delete_item(self, item):
        # удаляет предмет из базы данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM items WHERE name = ? AND rarity = ? AND desc = ? AND effect = ?",
            (item.name, item.rarity, item.desc, item.effect)
        )
        conn.commit()
        conn.close()

    def clear_all_items(self):
        # очищает все предметы из базы данных
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items")
        conn.commit()
        conn.close()

    def import_from_csv(self, csv_path):
        # импортирует предметы из csv файла
        imported_count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute(
                    "INSERT INTO items (name, rarity, desc, effect) VALUES (?, ?, ?, ?)",
                    (row['name'], row['rarity'], row['desc'], row['effect'])
                )
                imported_count += 1

        conn.commit()
        conn.close()
        return imported_count

    def export_to_csv(self, csv_path):
        # экспортирует предметы в csv файл
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, rarity, desc, effect FROM items")
        items_data = cursor.fetchall()
        conn.close()

        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['name', 'rarity', 'desc', 'effect'])
            for item in items_data:
                writer.writerow(item)

        return len(items_data)


class ItemDialog(QDialog):
    # диалог добавления и редактирования предмета

    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.init_ui()

        if item:
            self.load_item_data()

    def init_ui(self):
        self.setWindowTitle("Добавить предмет" if not self.item else "Редактировать предмет")
        self.setFixedSize(500, 350)

        layout = QVBoxLayout()

        # форма ввода
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["Обычный", "Необычный", "Легендарный", "Босс", "Лунный", "Снаряжение", "Бездонный"])

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)

        self.effect_edit = QTextEdit()
        self.effect_edit.setMaximumHeight(80)

        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Редкость:", self.rarity_combo)
        form_layout.addRow("Описание:", self.desc_edit)
        form_layout.addRow("Эффект:", self.effect_edit)

        # кнопки
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_item_data(self):
        # загружает данные предмета в форму
        if self.item:
            self.name_edit.setText(self.item.name)
            self.rarity_combo.setCurrentText(self.item.rarity)
            self.desc_edit.setPlainText(self.item.desc)
            self.effect_edit.setPlainText(self.item.effect)

    def get_item_data(self):
        # возвращает данные из формы
        return {
            'name': self.name_edit.text().strip(),
            'rarity': self.rarity_combo.currentText(),
            'desc': self.desc_edit.toPlainText().strip(),
            'effect': self.effect_edit.toPlainText().strip()
        }


class ItemDetailsDialog(QDialog):
    # диалог отображения полной информации о предмете

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Детали: {self.item.name}")
        self.setFixedSize(450, 350)

        layout = QVBoxLayout()

        # заголовок с названием и редкостью предмета
        header_layout = QHBoxLayout()
        name_label = QLabel(self.item.name)
        name_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.item.get_rarity_color().name()};")

        rarity_label = QLabel(self.item.rarity)
        rarity_label.setStyleSheet(
            f"font-size: 14px; color: {self.item.get_rarity_color().name()}; padding: 5px; border: 1px solid {self.item.get_rarity_color().name()}; border-radius: 10px;")

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(rarity_label)

        # информация о предмете
        info_group = QGroupBox("Информация о предмете")
        info_layout = QFormLayout()

        desc_label = QLabel(self.item.desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("padding: 5px;")

        effect_label = QLabel(self.item.effect)
        effect_label.setWordWrap(True)
        effect_label.setStyleSheet("padding: 5px; background-color: #2d2d2d; color: white; border-radius: 5px;")

        info_layout.addRow("Описание:", desc_label)
        info_layout.addRow("Эффект:", effect_label)

        info_group.setLayout(info_layout)

        layout.addLayout(header_layout)
        layout.addWidget(info_group)
        layout.addStretch()

        # кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class LootGeneratorDialog(QDialog):
    # диалог для генерации рандомного лута

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items
        self.init_ui()
        self.generate_loot()

    def init_ui(self):
        self.setWindowTitle("Генератор лута - Режим игры")
        self.setFixedSize(900, 500)

        layout = QVBoxLayout()

        # заголовок
        title_label = QLabel("🎲 Случайный лут после забега 🎲")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")

        # контейнер для предметов
        self.items_layout = QHBoxLayout()

        # кнопки
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("🎲 Сгенерировать")
        self.generate_btn.clicked.connect(self.generate_loot)
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.close_btn)

        layout.addWidget(title_label)
        layout.addLayout(self.items_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def generate_loot(self):
        # генерирует случайный набор из 5 предметов
        # сначала очищаем предыдущие предметы
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # отступы по бокам
        self.items_layout.addStretch()

        # выбираем 5 случайных предметов
        loot_items = random.sample(self.items, min(5, len(self.items)))

        for item in loot_items:
            item_widget = self.create_item_widget(item)
            self.items_layout.addWidget(item_widget)

        # отступы по бокам
        self.items_layout.addStretch()

    def create_item_widget(self, item):
        # делает виджет отображения предмета
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setFixedSize(170, 280)
        widget.setStyleSheet(f"""
            border: 3px solid {item.get_rarity_color().name()}; 
            border-radius: 12px; 
            padding: 12px;
            background-color: #2d2d2d;
            margin: 5px;  # добавил отступ между ячейками
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(12)

        # эмодзи редкости
        emoji_dict = {
            "Обычный": "⚪",
            "Необычный": "🟢",
            "Легендарный": "🟡",
            "Босс": "🔴",
            "Лунный": "🔵",
            "Снаряжение": "🟣",
            "Бездонный": "⚫"
        }

        emoji_label = QLabel(emoji_dict.get(item.rarity, "📦"))
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_label.setStyleSheet("font-size: 42px;")
        emoji_label.setFixedHeight(60)

        # название
        name_label = QLabel(item.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"""
            font-weight: bold; 
            color: {item.get_rarity_color().name()}; 
            font-size: 11px;  # уменьшил шрифт названия
            margin: 5px;
            padding: 5px;
        """)
        name_label.setFixedHeight(90)

        # редкость
        rarity_label = QLabel(item.rarity)
        rarity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rarity_label.setWordWrap(True)
        rarity_label.setStyleSheet(f"""
            font-size: 12px; 
            color: {item.get_rarity_color().name()};
            font-weight: bold;
            padding: 8px;
            background-color: #3d3d3d;
            border-radius: 8px;
            margin-top: 8px;
            border: 1px solid {item.get_rarity_color().name()};
        """)
        rarity_label.setFixedHeight(50)

        layout.addWidget(emoji_label)
        layout.addWidget(name_label)
        layout.addWidget(rarity_label)

        widget.setLayout(layout)

        return widget


class ItempediaApp(QMainWindow):
    # главное окно приложения itempedia

    def __init__(self):
        super().__init__()
        self.items = []
        self.filtered_items = []
        self.item_of_the_day = None
        self.db_manager = DatabaseManager()  # менеджер базы данных
        self.init_ui()
        self.load_items()
        self.update_item_of_the_day()
        self.apply_dark_theme()

    def init_ui(self):
        # инициализация пользовательского интерфейса
        self.setWindowTitle("Rain2pedia - Библиотека предметов Risk of Rain 2")
        self.setGeometry(100, 100, 1200, 800)

        # центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # главный layout
        main_layout = QVBoxLayout()

        # панель поиска и фильтров
        search_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Поиск по названию или описанию...")
        self.search_edit.textChanged.connect(self.filter_items)

        self.rarity_filter = QComboBox()
        self.rarity_filter.addItem("Все редкости")
        self.rarity_filter.addItems(
            ["Обычный", "Необычный", "Легендарный", "Босс", "Лунный", "Снаряжение", "Бездонный"])
        self.rarity_filter.currentTextChanged.connect(self.filter_items)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По названию", "По редкости"])
        self.sort_combo.currentTextChanged.connect(self.sort_items)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(QLabel("Фильтр редкости:"))
        search_layout.addWidget(self.rarity_filter)
        search_layout.addWidget(QLabel("Сортировка:"))
        search_layout.addWidget(self.sort_combo)

        # кнопки действий
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Добавить предмет")
        self.add_btn.clicked.connect(self.add_new_item)

        self.loot_btn = QPushButton("🎲 Режим игры")
        self.loot_btn.clicked.connect(self.random_loot)

        self.daily_btn = QPushButton("📅 Предмет дня")
        self.daily_btn.clicked.connect(self.show_item_of_the_day)

        self.edit_btn = QPushButton("✏ Редактировать")
        self.edit_btn.clicked.connect(self.edit_selected_item)


        self.delete_btn = QPushButton("❌ Удалить предмет")
        self.delete_btn.clicked.connect(self.delete_selected_item)
        self.delete_btn.setStyleSheet("background-color: #ff4444; color: white;")

        self.clear_btn = QPushButton("🗑️ Очистить все")
        self.clear_btn.clicked.connect(self.clear_items)
        self.clear_btn.setStyleSheet("background-color: #d32f2f; color: white;")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.loot_btn)
        button_layout.addWidget(self.daily_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addStretch()

        # таблица предметов
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Название", "Редкость", "Описание", "Эффект"])
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.items_table.doubleClicked.connect(self.show_selected_item_info)
        self.items_table.setSortingEnabled(True)

        # запрещаем редактирование ячеек
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # статус бар
        self.statusBar().showMessage("Готово")

        # сборка layout
        main_layout.addLayout(search_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.items_table)

        central_widget.setLayout(main_layout)

        # создание меню
        self.create_menu()

    def delete_selected_item(self):
        # удаляет выбранный предмет из таблицы и базы данных
        current_row = self.items_table.currentRow()

        if current_row < 0:
            QMessageBox.information(self, "Информация", "Пожалуйста, выберите предмет для удаления!")
            return

        if current_row < len(self.filtered_items):
            item = self.filtered_items[current_row]

            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить предмет '{item.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # удаляем из базы данных
                self.db_manager.delete_item(item)

                # удаляем из локальных списков
                if item in self.items:
                    self.items.remove(item)
                if item in self.filtered_items:
                    self.filtered_items.remove(item)

                # обновляем таблицу
                self.update_items_table()

                # обновляем предмет дня
                self.update_item_of_the_day()

                self.statusBar().showMessage(f"Удален предмет: {item.name}")
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный выбор предмета!")

    def edit_selected_item(self):
        #редактирование выбранного предмета
        current_row = self.items_table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_items):
            item = self.filtered_items[current_row]

            #находим ориг. предмет
            original_item = None
            for orig_item in self.items_list:
                if (orig_item.name == item.name and
                        orig_item.rarity == item.rarity and
                        orig_item.desc == item.desc):
                    original_item = orig_item
                    break
            if original_item:
                dialog = ItemDialog(self, original_item)
                if dialog.exec():
                    item_data = dialog.get_item_data()

                    # обновляем данные предмета
                    original_item.name = item_data['name']
                    original_item.rarity = item_data['rarity']
                    original_item.desc = item_data['desc']
                    original_item.effect = item_data['effect']

                    self.save_items()
                    self.filter_items()
                    self.statusBar().showMessage(f"Обновлен предмет:{original_item.name}")
                else:
                    QMessageBox.warning(self, "Внимание", "Выберите предмет для редактирования")


    def clear_items(self):
        # очищает все предметы из базы данных
        reply = QMessageBox.question(
            self,
            "Подтверждение очистки",
            "Вы уверены, что хотите удалить все предметы? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # очищаем базу данных
            self.db_manager.clear_all_items()

            # очищаем списки предметов
            self.items.clear()
            self.filtered_items.clear()

            # очищаем таблицу
            self.items_table.setRowCount(0)

            # обновляем статус бар
            self.statusBar().showMessage("Все предметы удалены")

            # обновляем предмет дня
            self.update_item_of_the_day()

    def create_menu(self):
        # создает меню приложения
        menubar = self.menuBar()

        # меню файл
        file_menu = menubar.addMenu('Файл')

        import_action = file_menu.addAction('Импорт предметов (CSV)')
        import_action.triggered.connect(self.import_items)

        export_action = file_menu.addAction('Экспорт предметов (CSV)')
        export_action.triggered.connect(self.export_items)

        file_menu.addSeparator()

        exit_action = file_menu.addAction('Выход')
        exit_action.triggered.connect(self.close)

    def load_items(self):
        # загружает предметы из базы данных
        try:
            # загружаем из базы данных
            self.items = self.db_manager.get_all_items()

            # если база пустая, создаем демо данные
            if not self.items:
                self.create_demo_data()
                # сохраняем демо данные в базу
                for item in self.items:
                    self.db_manager.add_item(item)

            self.filtered_items = self.items.copy()
            self.update_items_table()
            self.statusBar().showMessage(f"Загружено предметов: {len(self.items)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить предметы: {str(e)}")

    def create_demo_data(self):
        # создает демонстрационные данные
        demo_items = [
            Item("Шприц солдата", "Обычный", "Увеличивает скорость атаки", "+15% скорость атаки"),
            Item("Плюшевый мишка", "Обычный", "Дает шанс избежать урона", "15% шанс блокировать урон"),
            Item("Укулеле", "Необычный", "Вызывает электрические разряды между врагами", "25% шанс ударить молнией"),
            Item("57-листный клевер", "Легендарный", "Повторяет броски удачи", "Перебрасывает неудачные шансы"),
            Item("Церемониальный кинжал", "Легендарный", "Убийства создают кинжалы", "3 кинжала на убийство"),
            Item("Блистательный бегемот", "Легендарный", "Взрывы увеличиваются в размере", "+60% радиус взрыва"),
            Item("Ограненное стекло", "Лунный", "Удваивает урон, но уменьшает здоровье", "2x урон, 50% здоровья"),
            Item("Защитные микророботы", "Босс", "Автоматически перехватывает снаряды", "Перехватывает снаряды"),
            Item("Королевский конденсатор", "Снаряжение", "Вызывает молнию по цели", "Удар молнией по прицелу"),
            Item("Линзы Потерянного Провидца", "Бездонный", "Шанс мгновенно убить врага", "1% шанс instant kill"),
            Item("Личный щит", "Обычный", "Защищает при полном здоровье", "+13 щита"),
            Item("Энергетический напиток", "Обычный", "Увеличивает скорость движения",
                 "+25% скорость на 2 сек после удара"),
            Item("Кроссовки", "Необычный", "Повышает скорость передвижения", "+20% скорость движения"),
            Item("Клык берсерка", "Необычный", "Увеличивает урон при низком здоровье", "+50% урон при здоровье <25%"),
            Item("Инфузия", "Необычный", "Увеличивает максимальное здоровье", "+100 здоровья за убийство"),
            Item("Бессмертие", "Легендарный", "Воскрешение после смерти", "Воскрешение с 50% здоровья")
        ]

        self.items.extend(demo_items)

    def update_items_table(self):
        # обновляет таблицу предметов
        self.items_table.setRowCount(len(self.filtered_items))

        for row, item in enumerate(self.filtered_items):
            # название
            name_item = QTableWidgetItem(item.name)
            name_item.setForeground(item.get_rarity_color())

            # редкость
            rarity_item = QTableWidgetItem(item.rarity)
            rarity_item.setForeground(item.get_rarity_color())

            # описание
            desc_item = QTableWidgetItem(item.desc)

            # эффект
            effect_item = QTableWidgetItem(item.effect)

            self.items_table.setItem(row, 0, name_item)
            self.items_table.setItem(row, 1, rarity_item)
            self.items_table.setItem(row, 2, desc_item)
            self.items_table.setItem(row, 3, effect_item)

        self.items_table.resizeColumnsToContents()

    def filter_items(self):
        # фильтрует предметы по редкости и по поисковому запросу
        search_text = self.search_edit.text().lower()
        rarity_filter = self.rarity_filter.currentText()

        self.filtered_items = [
            item for item in self.items
            if
            (search_text in item.name.lower() or search_text in item.desc.lower() or search_text in item.effect.lower())
            and (rarity_filter == "Все редкости" or item.rarity == rarity_filter)
        ]

        self.sort_items()
        self.statusBar().showMessage(f"Найдено предметов: {len(self.filtered_items)}")

    def sort_items(self):
        # сортирует предметы
        sort_by = self.sort_combo.currentText()

        if sort_by == "По названию":
            self.filtered_items.sort(key=lambda x: x.name)
        elif sort_by == "По редкости":
            self.filtered_items.sort(key=lambda x: (x.get_rarity_order(), x.name))

        self.update_items_table()

    def add_new_item(self):
        # открывает диалог добавления нового предмета
        dialog = ItemDialog(self)
        if dialog.exec():
            item_data = dialog.get_item_data()

            # проверка обязательных полей
            if not item_data['name']:
                QMessageBox.warning(self, "Ошибка", "Название предмета обязательно!")
                return

            # создание нового предмета
            new_item = Item(
                item_data['name'],
                item_data['rarity'],
                item_data['desc'],
                item_data['effect']
            )

            # добавляем в базу данных
            self.db_manager.add_item(new_item)

            # добавляем в локальный список
            self.items.append(new_item)

            self.filter_items()
            self.statusBar().showMessage(f"Добавлен предмет: {new_item.name}")

    def show_selected_item_info(self):
        # показывает инф-ю о выбранном предмете
        current_row = self.items_table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_items):
            item = self.filtered_items[current_row]
            dialog = ItemDetailsDialog(item, self)
            dialog.exec()

    def random_loot(self):
        # открывает диалог генерации случайного лута
        if not self.items:
            QMessageBox.information(self, "Информация", "Нет предметов для генерации лута!")
            return

        dialog = LootGeneratorDialog(self.items, self)
        dialog.exec()

    def update_item_of_the_day(self):
        # обновляет предмет дня
        if self.items:
            # используем текущую дату как сид(seed)
            today = datetime.now().date()
            random.seed(today.toordinal())
            self.item_of_the_day = random.choice(self.items)
            random.seed()  # сбрасываем сид

    def show_item_of_the_day(self):
        # показывает предмет дня
        if self.item_of_the_day:
            dialog = ItemDetailsDialog(self.item_of_the_day, self)
            dialog.setWindowTitle(f"📅 Предмет дня: {self.item_of_the_day.name}")
            dialog.exec()
        else:
            QMessageBox.information(self, "Информация", "Предмет дня не доступен!")

    def apply_dark_theme(self):
        # темная тема
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))

        QApplication.setPalette(dark_palette)

    def import_items(self):
        # импорт предметов из csv-файла в базу данных
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт предметов", "", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                imported_count = self.db_manager.import_from_csv(file_path)

                # перезагружаем предметы из базы
                self.items = self.db_manager.get_all_items()
                self.filter_items()

                self.statusBar().showMessage(f"Импортировано предметов: {imported_count}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать предметы: {str(e)}")

    def export_items(self):
        # экспорт всех предметов из базы данных в csv-файл
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт предметов", "ror2_items_export.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                exported_count = self.db_manager.export_to_csv(file_path)
                self.statusBar().showMessage(f"Экспортировано предметов: {exported_count}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать предметы: {str(e)}")


def main():
    # главная функция приложения через которую запускается само приложениее
    app = QApplication(sys.argv)
    app.setApplicationName("Rain2pedia")
    app.setApplicationVersion("1.0")

    app.setStyle('Fusion')

    window = ItempediaApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
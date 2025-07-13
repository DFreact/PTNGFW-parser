import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QLineEdit, QVBoxLayout, QHBoxLayout, QCheckBox, QMessageBox
)
from modules.dump import dump_all_json
from modules.exporter import export_all_html_and_csv


class FirewallExportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Экспорт правил межсетевого экрана")
        self.setMinimumWidth(600)

        # Поля
        self.config_path = QLineEdit("config_secure.json")
        self.json_path = QLineEdit("save_json/")
        self.html_path = QLineEdit("save_html/")
        self.use_color = QCheckBox("Цветной HTML")
        self.csv_path = QLineEdit("save_csv/")

        # Кнопки
        self.btn_select_config = QPushButton("Выбрать config.json")
        self.btn_select_json = QPushButton("Папка JSON")
        self.btn_select_html = QPushButton("Папка HTML")
        self.btn_select_csv = QPushButton("Папка CSV")
        self.btn_start = QPushButton("Старт экспорта")

        # Layout
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Файл конфигурации:"))
        layout.addWidget(self.config_path)
        layout.addWidget(self.btn_select_config)

        layout.addWidget(QLabel("Путь для JSON-файлов:"))
        layout.addWidget(self.json_path)
        layout.addWidget(self.btn_select_json)

        layout.addWidget(QLabel("Путь для HTML-файлов:"))
        layout.addWidget(self.html_path)
        layout.addWidget(self.btn_select_html)

        layout.addWidget(QLabel("Путь для CSV-файлов:"))
        layout.addWidget(self.csv_path)
        layout.addWidget(self.btn_select_csv)

        layout.addWidget(self.use_color)
        layout.addWidget(self.btn_start)

        self.setLayout(layout)

        # События
        self.btn_select_config.clicked.connect(self.select_config)
        self.btn_select_json.clicked.connect(self.select_json_folder)
        self.btn_select_html.clicked.connect(self.select_html_folder)
        self.btn_select_csv.clicked.connect(self.select_csv_folder)
        self.btn_start.clicked.connect(self.run_export)

    def select_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите config_secure.json", "", "JSON Files (*.json)")
        if path:
            self.config_path.setText(path)

    def select_json_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для JSON")
        if folder:
            self.json_path.setText(folder)

    def select_html_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для HTML")
        if folder:
            self.html_path.setText(folder)
        
    def select_csv_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для CSV")
        if folder:
            self.csv_path.setText(folder)
        

    def run_export(self):
        try:
            config_path = self.config_path.text().strip()
            json_path = self.json_path.text().strip()
            html_path = self.html_path.text().strip()
            color = self.use_color.isChecked()

            if not os.path.exists(config_path):
                raise Exception("Файл конфигурации не найден.")
            if not os.path.exists(json_path):
                os.makedirs(json_path)
            if not os.path.exists(html_path):
                os.makedirs(html_path)

            csv_path = self.csv_path.text().strip()
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)

            dump_all_json(config_path=config_path, save_path=json_path)
            export_all_html_and_csv(json_path=json_path, html_path=html_path, use_color=color, csv_path=csv_path)
            QMessageBox.information(self, "Успешно", "Экспорт завершён!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirewallExportApp()
    window.show()
    sys.exit(app.exec_())

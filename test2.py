import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF, QPoint
from PyQt5.QtGui import QPainter, QRegion, QPainterPath, QColor
from enum import Enum


class DragState(Enum):
    NoneState = 0
    Dragging = 1


class RoundWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Remove window decorations
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.drag_state = DragState.NoneState
        self.drag_position = QPoint()

        # Utworzenie głównego widgeta
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Utworzenie układu siatki dla przycisków
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)  # Reduce spacing between buttons
        self.central_widget.setLayout(grid_layout)

        # Utworzenie przycisku "Settings"
        settings_button = QPushButton("Settings")
        settings_button.setFixedSize(85, 40)
        settings_button.clicked.connect(self.open_settings)
        grid_layout.addWidget(settings_button, 0, 0)

        # Utworzenie przycisku "Exit"
        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(85, 40)
        exit_button.clicked.connect(lambda: sys.exit(app.exec_()))
        grid_layout.addWidget(exit_button, 0, 1)

        self.button_mapping = {}  # Mapping of tab buttons to main window buttons

    def open_settings(self):
        settings_window = SettingsWindow(self)
        settings_window.show()

    def add_button(self, name):
        button = QPushButton(name)
        button.setFixedSize(85, 40)
        button.clicked.connect(lambda: self.handle_main_button_click(button))
        grid_layout = self.central_widget.layout()
        grid_layout.addWidget(button)
        return button

    def handle_main_button_click(self, button):
        if button in self.button_mapping:
            tab_button = self.button_mapping[button]
            tab_button.click()

    def change_button_color(self, button, color):
        button.setStyleSheet(f"background-color: {color};")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 220))  # Semi-transparent white color

        # Create a rounded rectangle path using the window geometry
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 20, 20)
        painter.drawPath(path.simplified())

    def create_rounded_region(self, rect, radius):
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        return region

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_state = DragState.Dragging
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_state == DragState.Dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drag_state == DragState.Dragging:
            self.drag_state = DragState.NoneState
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class SettingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
        self.main_window = main_window

        # Utworzenie układu pionowego dla zakładek
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Utworzenie widżetu zakładek
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Dodanie pierwszej zakładki "App"
        app_tab = QWidget()
        tab_widget.addTab(app_tab, "App")

        # Dodanie drugiej zakładki "+"
        plus_tab = QWidget()
        tab_widget.addTab(plus_tab, "+")

        # Obsługa kliknięcia zakładki "+"
        tab_widget.tabBarClicked.connect(lambda index: self.handle_tab_click(tab_widget, index))

    def handle_tab_click(self, tab_widget, index):
        if index == tab_widget.count() - 1:
            new_tab_name = "New"
            new_tab, button_green, button_red = self.add_new_tab(tab_widget, new_tab_name)
            main_button = self.main_window.add_button(new_tab_name)
            self.main_window.button_mapping[main_button] = button_green, button_red

    def add_new_tab(self, tab_widget, tab_name):
        new_tab = QWidget()
        tab_widget.insertTab(tab_widget.count() - 1, new_tab, tab_name)
        tab_widget.setCurrentIndex(tab_widget.count() - 2)

        layout = QVBoxLayout(new_tab)
        layout.addWidget(QPushButton("Content"))

        button_green = QPushButton("Green")
        button_green.clicked.connect(lambda: self.change_main_button_color(button_green, "green"))
        layout.addWidget(button_green)

        button_red = QPushButton("Red")
        button_red.clicked.connect(lambda: self.change_main_button_color(button_red, "red"))
        layout.addWidget(button_red)

        return new_tab, button_green, button_red

    def change_main_button_color(self, button, color):
        main_button = None
        for btn, (btn_green, btn_red) in self.main_window.button_mapping.items():
            if button == btn_green or button == btn_red:
                main_button = btn
                break

        if main_button:
            self.main_window.change_button_color(main_button, color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoundWindow()
    window.show()
    sys.exit(app.exec_())
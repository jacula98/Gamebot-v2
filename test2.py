import sys
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLabel, QDialog, QTabWidget, QLineEdit, QInputDialog


class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.draggable = False  # Flag to track if the window is draggable
        self.offset = None  # Offset between the cursor position and the top-left corner of the window

        self.settings = QSettings('Myapps', 'Gamebot')

        self.initUI()

    def initUI(self):
        self.setWindowTitle('GameBot')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 150, 50)
        try:
            self.move(self.settings.value('window position'))
        except:
            pass

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)

        self.button_grid = QGridLayout()
        self.button_grid.setSpacing(0)
        self.main_layout.addLayout(self.button_grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)

        settings_button = QPushButton('Settings', self)
        settings_button.setObjectName('settingsButton')
        settings_button.clicked.connect(self.openSettings)  # Podłączanie sygnału kliknięcia przycisku "Settings" do otwierania okna ustawień

        exit_button = QPushButton('Exit', self)
        exit_button.setObjectName('exitButton')
        exit_button.clicked.connect(self.closeAndSave)  # Podłączanie sygnału kliknięcia przycisku "Exit" do zamykania aplikacji

        button_layout.addWidget(settings_button)
        button_layout.addWidget(exit_button)

        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)


    def closeAndSave(self):
        try:
            self.settings.setValue('window position', self.pos())
        except:
            pass
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset is not None:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            self.offset = None


    def openSettings(self):
        self.settings_window = SettingsWindow(self.tab_widget)  # Przekazujemy tab_widget jako argument do konstruktora SettingsWindow
        self.settings_window.show()  # Pokaż okno ustawień


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rounded_rect = self.rect().adjusted(0, 0, -1, -1)
        color = QColor(255, 255, 255, 200)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(rounded_rect, 10, 10)


class SettingsWindow(QDialog):
    def __init__(self, tab_widget):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setGeometry(400, 400, 600, 400)

        self.layout = QVBoxLayout()

        self.tab_widget = tab_widget  # Przechowujemy referencję do przekazanego tab_widget

        self.tab_widget.addTab(QWidget(), "App")  # Dodawanie początkowej zakładki "App"
        self.tab_widget.addTab(QWidget(), "+")  # Dodawanie zakładki "+" do dodawania nowych zakładek

        self.layout.addWidget(self.tab_widget)

        self.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())

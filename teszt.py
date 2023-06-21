import sys
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLabel, QDialog, QTabWidget, QLineEdit, QInputDialog, QTabBar, QMessageBox


class GameBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameBot")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.grid_layout = QGridLayout()
        
        self.new_button = QPushButton("New Button", self)
        self.new_button.clicked.connect(self.add_button)
        self.grid_layout.addWidget(self.new_button, 0, 0)
        
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)
        self.grid_layout.addWidget(self.exit_button, 0, 1)
        
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)
        self.grid_layout.addWidget(self.settings_button, 1, 0, 1, 2)
        
        self.buttons = []
        self.settings_window = None
        
        self.load_state()
        
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)

        self.draggable = False
        self.offset = None

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

    """
    def add_button(self):
        button = QPushButton("Button")
        self.buttons.append(button)

        row = (len(self.buttons) - 1) // 2 + 2
        column = (len(self.buttons) - 1) % 2
        self.grid_layout.addWidget(button, row, column)
    """
    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()
        
    
    def closeEvent(self, event):
        self.save_state()
        super().closeEvent(event)
    
    def save_state(self):
        state = [button.text() for button in self.buttons]
        if self.settings_window:
            settings_state = self.settings_window.get_state()
        else:
            settings_state = []
        
        data = {
            "gamebot": state,
            "settings": settings_state
        }
        
        with open("app_state.json", "w") as f:
            json.dump(data, f)
    
    def load_state(self):
        try:
            with open("app_state.json", "r") as f:
                data = json.load(f)
                if "gamebot" in data:
                    for button_text in data["gamebot"]:
                        button = QPushButton(button_text, self)
                        self.grid_layout.addWidget(button)
                        self.buttons.append(button)
        except FileNotFoundError:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rounded_rect = self.rect().adjusted(0, 0, -1, -1)
        color = QColor(255, 255, 255, 200)

        painter.setPen(Qt.black)
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(rounded_rect, 10, 10)

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        #self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(400, 400, 600, 400)

        

        self.layout = QVBoxLayout()
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)


        self.addTab("App")

        self.addTabPlusButton()

        self.tabs = []
        print('ladowanie state')
        self.load_state()
        
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
        



    def addTabPlusButton(self):
        add_tab_button = QPushButton("+")
        add_tab_button.clicked.connect(self.createNewTab)

        self.tab_widget.addTab(QWidget(), "") # prepare a placeholder tab that will later contain the button
        index = self.tab_widget.count() - 1
        self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, add_tab_button)



    def createNewTab(self):
        new_tab, ok = QInputDialog.getText(self, 'Creating new worker', 'Enter worker name:', flags=Qt.WindowCloseButtonHint)
        print('[CREATING NEW TAB]')

        if ok and new_tab not in self.tabs:
            self.tabs.append(new_tab)
            self.tab_widget.insertTab(self.tab_widget.count() - 1, QWidget(), new_tab)
        else:
            print(new_tab, 'is already in tabs list ->', self.tabs)
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Information')
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText('You already have worker with this name')
            msg_box.exec_()
        print('lista', self.tabs)

    def addTab(self, title):
        new_tab = QWidget()
        index = self.tab_widget.addTab(new_tab, title)

        if title == "App":
            self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, None)


    def load_state(self):
        try:
            print('3', self.tabs)
            with open("app_state.json", "r") as f:
                data = json.load(f)
                if "settings" in data:
                    for tab_name in data["settings"]:
                        self.addTab(tab_name)
                        self.tabs.append(tab_name)
        except FileNotFoundError:
            pass


    def save_state(self):
        state = [tab for tab in self.tabs]
        return state

    def get_state(self):
        return self.save_state()
    
    def closeEvent(self, event):
        self.save_state()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gamebot_window = GameBotWindow()
    gamebot_window.show()
    sys.exit(app.exec_())

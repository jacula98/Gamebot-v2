import sys
import pickle
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLabel, QDialog, QTabWidget, QLineEdit, QInputDialog, QTabBar, QMessageBox


class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.draggable = False  # Flag to track if the window is draggable
        self.offset = None  # Offset between the cursor position and the top-left corner of the window
        self.settings = QSettings('Myapp', 'Gamebot')
        self.dictList = []
        self.buttonsDict = {}
        self.tabsDict = {}

        try:
            with open("settings.pkl", "rb") as file:
                self.dictList = pickle.load(file)
        except:
            pass

        self.initUI()

    def initUI(self):
        self.setWindowTitle('GameBot')
        # Remove the question mark button
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 150, 50)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(8)

        self.button_grid = QGridLayout()
        self.button_grid.setSpacing(8)
        self.main_layout.addLayout(self.button_grid)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        settings_button = QPushButton('Settings', self)
        settings_button.setObjectName('settingsButton')
        settings_button.clicked.connect(self.openSettings)

        exit_button = QPushButton('Exit', self)
        exit_button.setObjectName('exitButton')
        exit_button.clicked.connect(self.closeAndSave)

        button_layout.addWidget(settings_button)
        button_layout.addWidget(exit_button)

        self.basicLoad()
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

    def basicLoad(self):
        try:
            print('[BASIC LOAD]')
            self.move(self.settings.value('window position'))
            self.buttonsDict = self.dictList[0]
            for button_label in self.buttonsDict['buttons']:
                self.addCustomButton(button_label)
                print('loaded button', button_label)
        except:
            pass

    def closeAndSave(self):
        # Save the window position
        self.settings.setValue('window position', self.pos())
        #
        print('[SAVING]')
        print('buttonsDict coming to dict list to be saved:', self.buttonsDict)
        print('tabsDict coming to dict list to be saved:', self.tabsDict)
        if len(self.dictList) == 0:
            self.dictList.append(self.buttonsDict) # buttons dict gonna be at place [0]
            self.dictList.append(self.tabsDict) # buttons dict gonna be at place [0]
        else:
            self.dictList[0] = self.buttonsDict
            self.dictList[1] = self.tabsDict
        print('saved dicts list:', self.dictList)

        with open("settings.pkl", "wb") as file:
            pickle.dump(self.dictList, file)
        # Close the window
        sys.exit(app.exec_())


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
        self.settings_window = SettingsWindow()
        self.settings_window.tabAdded.connect(self.addCustomButton)
        self.settings_window.tabClosed.connect(self.removeCustomButton)
        self.settings_window.show()
        print('[OPENING SETTINGS]')
        print('wszystkie listy:', self.dictList)
        if len(self.dictList) >= 2:
            try:
                print('tabs lista:', self.dictList[1])
                tabsDict = self.dictList[1]
                for tab in tabsDict['tabs']:
                    SettingsWindow.addTab(tab)
            except:
                pass

    def addCustomButton(self, tab_title):
        button = QPushButton(tab_title, self)
        button.setObjectName(f'{tab_title}')
        button.setCheckable(True)  # Make the button toggleable
        button.clicked.connect(self.toggleButtonColor)  # Connect the clicked signal to the toggleButtonColor slot
        button.setStyleSheet('''
            background-color: red;
            border-radius: 5px;
            font: bold 14px;
                             ''')  # Set the initial background color to red
        if "buttons" not in self.buttonsDict: # if buttonsdict is empty
            self.buttonsDict['buttons'] = [tab_title]
            print('creating new button:', tab_title)
            self.button_grid.addWidget(button)
        elif "buttons" in self.buttonsDict and tab_title not in self.buttonsDict["buttons"]: # if buttonsdict are not empty and there is no button with this name in this dict
            self.buttonsDict['buttons'].append(tab_title)
            print('creating new button:', tab_title)
            self.button_grid.addWidget(button)
        else:
            print(tab_title, 'is already in buttons dict')
            self.button_grid.addWidget(button)
        
        


    def removeCustomButton(self, tab_title):
        button_name = f'{tab_title}'
        buttons = self.findChildren(QPushButton, button_name)
        for button in buttons:
            button.setParent(None)
            button.deleteLater()
        self.adjustSize()  # Resize the window to fit the updated layout

    def toggleButtonColor(self):
        button = self.sender()
        if button.isChecked():
            button.setStyleSheet('''
                                 background-color: green; 
                                 border-radius: 5px; 
                                 font: bold 14px;
                                 ''')
        else:
            button.setStyleSheet('''
                                 background-color: red; 
                                 border-radius: 5px; 
                                 font: bold 14px;
                                 ''')

        # Adjust the palette to make the checked button have a stronger color
        palette = button.palette()
        if button.isChecked():
            palette.setColor(button.backgroundRole(), QColor(0, 255, 0))  # Green color
        else:
            palette.setColor(button.backgroundRole(), QColor(255, 0, 0))  # Red color
        button.setPalette(palette)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rounded_rect = self.rect().adjusted(0, 0, -1, -1)
        color = QColor(255, 255, 255, 200)

        painter.setPen(Qt.black)
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(rounded_rect, 10, 10)


class SettingsWindow(QDialog):
    tabAdded = pyqtSignal(str)
    tabClosed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(400, 400, 600, 400)

        self.mainWindow = CustomWindow()
        #print('tabs dict in settings window', self.mainWindow.tabsDict)

        self.layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)

        self.tab_widget.tabCloseRequested.connect(self.closeTab)
        self.tab_widget.tabBar().tabMoved.connect(self.updateButtonOrder)

        self.addTab("App")

        
        self.addTabPlusButton()

        self.layout.addWidget(self.tab_widget) # add tab widget to layout == settings window
        self.setLayout(self.layout) # put created layout to aplication

    
    def addTabPlusButton(self):
        add_tab_button = QPushButton("+")
        add_tab_button.clicked.connect(self.createNewTab)

        self.tab_widget.addTab(QWidget(), "") # prepare a placeholder tab that will later contain the button
        index = self.tab_widget.count() - 1
        self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, add_tab_button)

    def addTab(self, title):
        new_tab = QWidget()
        index = self.tab_widget.addTab(new_tab, title)

        if title == "App":
            self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, None)

    def createNewTab(self):
        new_tab, ok = QInputDialog.getText(self, 'Creating new worker', 'Enter worker name:', flags=Qt.WindowCloseButtonHint)
        #print(self.mainWindow.tabsDict)

        if ok and "tabs" not in self.mainWindow.tabsDict: # empty dict so can add anything
            self.mainWindow.tabsDict['tabs'] = [new_tab]
            print('tabs dict?:', self.mainWindow.tabsDict['tabs'])
            self.tab_widget.insertTab(self.tab_widget.count() - 1, QWidget(), new_tab)
            self.tabAdded.emit(new_tab)
            print('tabs dict in settings window creatnewtab method', self.mainWindow.tabsDict)
        elif ok and "tabs" in self.mainWindow.tabsDict and new_tab not in self.mainWindow.tabsDict["tabs"]:
            self.mainWindow.tabsDict['tabs'].append(new_tab)
            print('tabs dict?:', self.mainWindow.tabsDict['tabs'])
            self.tab_widget.insertTab(self.tab_widget.count() - 1, QWidget(), new_tab)
            self.tabAdded.emit(new_tab)
            print('tabs dict in settings window creatnewtab method', self.mainWindow.tabsDict)
        else:
            print(new_tab, 'is already in tabs dict ->', self.mainWindow.tabsDict)
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Information')
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText('You already have worker with this name')
            msg_box.exec_()


    def closeTab(self, index):
        if self.tab_widget.count() > 2:
            tab_widget = self.tab_widget.widget(index)
            tab_title = self.tab_widget.tabText(index)
            self.tab_widget.removeTab(index)
            self.tabClosed.emit(tab_title)

    def updateButtonOrder(self):
        for i in range(self.tab_widget.count()):
            tab_title = self.tab_widget.tabText(i)
            button_name = f'customButton_{tab_title}'
            buttons = self.findChildren(QPushButton, button_name)
            for button in buttons:
                self.layout.removeWidget(button)
                self.layout.addWidget(button)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())

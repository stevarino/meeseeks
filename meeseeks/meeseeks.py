import os
import sys
import platform

from PyQt5.QtCore import (QAbstractEventDispatcher, QAbstractNativeEventFilter,
                          QPoint, QRect, QSize, Qt)
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDesktopWidget,
                             QGridLayout, QLabel, QMainWindow, QMenu,
                             QSizePolicy, QSpacerItem, QStyle, QSystemTrayIcon,
                             QWidget, qApp)


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, keybinder):
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        ret = self.keybinder.handler(eventType, message)
        return ret, 0

class MainWindow(QMainWindow):
    """
            Сheckbox and system tray icons.
            Will initialize in the constructor.
    """
    check_box = None
    tray_icon = None
    
    # Override the class constructor
    def __init__(self, canvas):
        # Be sure to call the super class method
        super().__init__(None, Qt.WindowStaysOnTopHint)

        self.canvas = canvas

        self.setVisible(False)
    
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Settings - Coming Soon")
    
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mdpi.png')
        self.tray_icon.setIcon(QIcon(icon))
    
        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        activate = QAction("Activate", self)
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        activate.triggered.connect(self.canvas.show)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(activate)
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


        ui = QMainWindow()
        #ui.setWindowFlags(Qt.FramelessWindowHint)
        ui.setWindowModality(Qt.NonModal)
        ui.move(0, 0)
        ui.setMinimumSize(QSize(480, 80))
        ui.show()

    
    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_geom = QDesktopWidget().screenGeometry()
        self.setGeometry(self.screen_geom)
        self.begin = QPoint()
        self.end = QPoint()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(255, 0, 0, 255))
        qp.setBrush(br)
        width = self.screen_geom.width()
        height = self.screen_geom.height()
        offset = 10
        qp.drawRect(QRect(0, 0, offset, height))
        qp.drawRect(QRect(0, 0, width, offset))
        qp.drawRect(QRect(width-offset, 0, offset, height))
        qp.drawRect(QRect(0, height-offset, width, offset))


        begin = self.begin
        end = self.end

        diff = end - begin
        if min(diff.x(), diff.y()) < offset * 2:
            return

        if begin.x() > end.x():
            begin, end = QPoint(end.x(), begin.y()), QPoint(begin.x(), end.y())
        if begin.y() > end.y():
            begin, end = QPoint(begin.x(), end.y()), QPoint(end.x(), begin.y())


        qp.drawRect(QRect( # top
            begin - QPoint(offset,offset),
            QPoint(end.x() + offset, begin.y())
        ))
        qp.drawRect(QRect( # left
            begin - QPoint(offset,offset),
            QPoint(begin.x(), end.y() + offset)
        ))
        qp.drawRect(QRect( # bottom
            end + QPoint(offset,offset), 
            QPoint(begin.x() - offset, end.y())
        ))
        qp.drawRect(QRect( # right
            end + QPoint(offset,offset), 
            QPoint(end.x(), begin.y() - offset)
        ))
        

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()
        self.hide()

def main():
    import sys

    app = QApplication(sys.argv)

    widget = MyWidget()
    win = MainWindow(widget)


    def callback():
        widget.show()

    if 'Darwin' not in platform.system():
        from pyqtkeybind import keybinder
        keybinder.init()
        keybinder.register_hotkey(win.winId(), "Ctrl+Shift+1", callback)

        # Install a native event filter to receive events from the OS
        win_event_filter = WinEventFilter(keybinder)
        event_dispatcher = QAbstractEventDispatcher.instance()
        event_dispatcher.installNativeEventFilter(win_event_filter)

        keybinder.unregister_hotkey(win.winId(), 0x0, 0x0)
    sys.exit(app.exec())

    
if __name__ == "__main__":
    main()

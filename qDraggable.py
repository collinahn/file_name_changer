# 창의 여백을 끌어서 이동할 수 있게하는 속성

from PyQt5.QtCore import (
    Qt,
    QObject
)
from PyQt5.QtWidgets import (
    QDialog, 
    QMainWindow, 
    QWidget
)

class QMainWindow(QMainWindow):
    def mousePressEvent(self, event) :
        if event.button() == Qt.LeftButton :
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) :
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event) :
        self.offset = None
        super().mouseReleaseEvent(event)


class QWidget(QWidget):
    def mousePressEvent(self, event) :
        if event.button() == Qt.LeftButton :
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) :
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event) :
        self.offset = None
        super().mouseReleaseEvent(event)


class QDialog(QDialog):
    def mousePressEvent(self, event) :
        if event.button() == Qt.LeftButton :
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) :
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event) :
        self.offset = None
        super().mouseReleaseEvent(event)
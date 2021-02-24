from kiwoom.Kiwoom import *
import sys
from PyQt5.QtWidgets import *

class Main:
    def __init__(self):
        print("Main() Start")

        self.app = QApplication(sys.argv)
        self.kiwoom = Kiwoom()
        self.app.exec_()


if __name__ == '__main__':
    Main()

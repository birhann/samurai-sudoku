from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from time import sleep
from numpy import ma
from numpy.lib.function_base import select
from numpy.matrixlib.defmatrix import matrix


class SudokuObject():
    def __init__(self, sudokuList) -> None:
        self.allList = sudokuList
        self.topLeft = []
        self.topRight = []
        self.bottomLeft = []
        self.bottomRight = []
        self.middle = []
        self.rowsControl = 1
        self.setAllSudokuToLists()
        # self.printAllSudokutoConsole()

    def setAllSudokuToLists(self):
        for i in range(len(self.allList)):
            if i < 6:
                self.topLeft.append(self.allList[i][0:9])
                self.topRight.append(self.allList[i][9:18])
            elif i < 9:
                self.topLeft.append(self.allList[i][0:9])
                self.middle.append(self.allList[i][6:15])
                self.topRight.append(self.allList[i][12:21])
            elif i < 12:
                self.middle.append(self.allList[i][0:9])
            elif i < 15:
                self.bottomLeft.append(self.allList[i][0:9])
                self.middle.append(self.allList[i][6:15])
                self.bottomRight.append(self.allList[i][12:21])
            elif i < 21:
                self.bottomLeft.append(self.allList[i][0:9])
                self.bottomRight.append(self.allList[i][9:18])

    def printAllSudokutoConsole(self):
        print("Top Left\n")
        print(np.array(self.topLeft))
        print("\n______________________________")
        print("Top Right\n")
        print(np.array(self.topRight))
        print("\n______________________________")
        print("Middle\n")
        print(np.array(self.middle))
        print("\n______________________________")
        print("Bottom Left\n")
        print(np.array(self.bottomLeft))
        print("\n______________________________")
        print("Bottom Right\n")
        print(np.array(self.bottomRight))

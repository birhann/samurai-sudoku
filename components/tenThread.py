from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from time import sleep
from numpy import ma
from numpy.lib.function_base import select
from numpy.matrixlib.defmatrix import matrix


class SettingCellWorker(QThread):
    setNumberToCell = pyqtSignal(int, int, object)
    matrix = None
    control = 18
    counter = 1

    def run(self):
        for i in range(21):
            for j in range(self.control):
                print(self.matrix[i][j], i, j)
                if self.matrix[i][j] != '*':

                    self.setNumberToCell.emit(i, j, False)
                else:
                    self.setNumberToCell.emit(i, j, True)
                sleep(0.005)

            self.cellRowsColsControl()
            self.counter += 1

    def cellRowsColsControl(self):
        self.control = 21 if self.counter == 6 else self.control
        self.control = 9 if self.counter == 9 else self.control
        self.control = 21 if self.counter == 12 else self.control
        self.control = 18 if self.counter == 15 else self.control


class TenThreadOptions():
    def __init__(self, GUI) -> None:
        self.gui = GUI
        self.mainMatrix = self.gui.matrix

    def loadCells(self):
        self.thread = SettingCellWorker()
        self.thread.daemon = True
        self.thread.matrix = self.mainMatrix
        self.thread.setNumberToCell.connect(self.setNumberToGui)
        self.thread.finished.connect(self.loadIsDone)
        self.thread.start()

    def loadIsDone(self):
        self.gui.setInfo("Sample sudoku is loaded successfully!")
        self.gui.clearButton.setEnabled(True)
        self.gui.solveButton.setEnabled(True)

    def setNumberToGui(self, i, j, empty):
        if not empty:
            getattr(self.gui, "cell_"+str(i) +
                    "_"+str(j)).setText(self.mainMatrix[i][j])
        else:
            getattr(self.gui, "cell_"+str(i) +
                    "_"+str(j)).setText("")

    def setInfo(self, msg):
        self.gui.logScreen.insertPlainText(
            "10 Threading: {}\n".format(msg))
        self.logScreen.ensureCursorVisible()

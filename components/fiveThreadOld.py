from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from time import sleep
from threading import Thread
from components.sudoku import SudokuObject


class SettingCellWorker(QThread):
    setNumberToCell = pyqtSignal(int, int, object)
    matrix = None
    control = 18
    counter = 1

    def run(self):
        for i in range(21):
            for j in range(self.control):
                if self.matrix[i][j] != '*':

                    self.setNumberToCell.emit(i, j, False)
                else:
                    self.setNumberToCell.emit(i, j, True)
                sleep(0.002)

            self.cellRowsColsControl()
            self.counter += 1

    def cellRowsColsControl(self):
        self.control = 21 if self.counter == 6 else self.control
        self.control = 9 if self.counter == 9 else self.control
        self.control = 21 if self.counter == 12 else self.control
        self.control = 18 if self.counter == 15 else self.control


class FiveThreadOptions():
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
        self.gui.setInfo("Sample sudoku is loading..")

    def loadIsDone(self):
        self.gui.setInfo("Sample sudoku is loaded successfully!")
        self.gui.clearButton.setEnabled(True)
        self.gui.solveButton.setEnabled(True)
        self.gui.setInfo("Ready to solve with 5 thread!")

    def setNumberToGui(self, i, j, empty):
        if not empty:
            getattr(self.gui, "cell_"+str(i) +
                    "_"+str(j)).setText(self.mainMatrix[i][j])
        else:
            getattr(self.gui, "cell_"+str(i) +
                    "_"+str(j)).setText("")

    def setInfo(self, msg):
        self.gui.logScreen.insertPlainText(
            "5 Threading: {}\n".format(msg))
        self.gui.logScreen.ensureCursorVisible()

    def solveSudoku(self):
        self.setInfo("Starting to solve..")
        self.Sudoku = SudokuObject(self.mainMatrix)
        self.Threads = ThreadOperations(self.Sudoku, self.gui, self)


class ThreadOperations():
    def __init__(self, sudoku, GUI, fiveThreadObject) -> None:
        self.sudoku = sudoku
        self.gui = GUI
        self.fiveThreadObject = fiveThreadObject
        tTopLeft = Thread(target=self.solveTopLeft)
        tTopRight = Thread(target=self.solveTopRight)
        tMiddle = Thread(target=self.solveMiddle)
        tBottomLeft = Thread(target=self.solveBottomLeft)
        tBottomRight = Thread(target=self.solveBottomRight)
        self.threads = [tTopLeft, tTopRight, tMiddle,
                        tBottomLeft, tBottomRight]
        # tTopLeft.daemon = True
        # tTopRight.daemon = True
        # tMiddle.daemon = True
        # tBottomLeft.daemon = True
        # tBottomRight.daemon = True
        [thread.start() for thread in self.threads]
        [thread.join() for thread in self.threads]

        self.threadFinished()

    def threadFinished(self):
        self.gui.setClickables(True)
        self.gui.compareButton.setEnabled(False)
        self.fiveThreadObject.setInfo("All thread is done!")

    def solveTopLeft(self):
        sud = self.sudoku.topLeft
        self.solve(sud, 0, 0)

    def solveTopRight(self):
        sud = self.sudoku.topRight
        self.solve(sud, 0, 9)

    def solveMiddle(self):
        pass

    def solveBottomLeft(self):
        pass

    def solveBottomRight(self):
        pass

    def solve(self, sudoku, plusRow, plusCol):
        colControl = 0
        for r in range(9):
            for c in range(9):
                if str(sudoku[r][c]) == "*":
                    for d in range(1, 10):
                        if self.is_valid(r, c, d, sudoku):
                            if (c+plusCol) >= 9 and 5 < (r+plusRow) < 9:
                                getattr(self.gui, "cell_"+str(r+plusRow) +
                                        "_"+str(c+plusCol+3)).setText(str(d))
                            else:
                                getattr(self.gui, "cell_"+str(r+plusRow) +
                                        "_"+str(c+plusCol)).setText(str(d))
                            sudoku[r][c] = d
                            sleep(0.001)
                            if self.solve(sudoku, plusRow, plusCol):
                                return sudoku
                            if (c+plusCol) == 9 and 5 < (r+plusRow) < 9:
                                getattr(self.gui, "cell_"+str(r+plusRow) +
                                        "_"+str(c+plusCol+3)).setText("")
                            else:
                                getattr(self.gui, "cell_"+str(r+plusRow) +
                                        "_"+str(c+plusCol)).setText("")

                            sudoku[r][c] = "*"

                    return False
        print(np.array(sudoku))
        return True

    def is_valid(self, r, c, d, sudoku):
        for row in range(9):
            if str(sudoku[row][c]) == str(d):
                return False
        for col in range(9):
            if str(sudoku[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(sudoku[row][col]) == str(d):
                    return False
        return True

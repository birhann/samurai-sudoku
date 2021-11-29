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
                # sleep(0.0005)

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
        self.isTopLeftSudokuDone = False
        self.isTopRightSudokuDone = False
        self.isMiddleSudokuDone = False
        self.isBottomLeftSudokuDone = False
        self.isBottomRightSudokuDone = False

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
        self.Sudoku = SudokuObject(self.mainMatrix)
        self.createSudokuThreads()

        self.m.start()
        self.bL.start()
        # self.bR.start()
        # self.tL.start()
        # self.tR.start()

    def createSudokuThreads(self):
        self.tL = solveTopLeftWorker()
        self.tL.daemon = True
        self.tL.sudoku = self.Sudoku
        self.tL.setCell.connect(self.tLsetCell)
        self.tL.finished.connect(self.tLthreadFinished)

        self.tR = solveTopRightWorker()
        self.tR.daemon = True
        self.tR.sudoku = self.Sudoku
        self.tR.setCell.connect(self.tRsetCell)
        self.tR.finished.connect(self.tRthreadFinished)

        self.bL = solveBottomLeftWorker()
        self.bL.daemon = True
        self.bL.sudoku = self.Sudoku
        self.bL.setCell.connect(self.bLsetCell)
        self.bL.finished.connect(self.bLthreadFinished)

        self.bR = solveBottomRightWorker()
        self.bR.daemon = True
        self.bR.sudoku = self.Sudoku
        self.bR.setCell.connect(self.bRsetCell)
        self.bR.finished.connect(self.bRthreadFinished)

        self.m = solveMiddleWorker()
        self.m.daemon = True
        self.m.sudoku = self.Sudoku
        self.m.setCell.connect(self.mSetCell)
        self.m.finished.connect(self.mthreadFinished)


# --------------WHEN WORKERS FINISHED---------------

    def tLthreadFinished(self):
        print("top-left-is-done**********\n")
        print(np.array(self.Sudoku.topLeft))
        self.isTopLeftSudokuDone = True
        if not self.isMiddleSudokuDone:
            for row in range(6, 9):
                for col in range(6, 9):
                    self.Sudoku.middle[row -
                                       6][col-6] = self.Sudoku.topLeft[row][col]
            print("top-left end\n", np.array(self.Sudoku.topLeft))
            self.m.relevantSudokufinished = True

    def tRthreadFinished(self):
        print("top-right-is-done**********\n")
        print(np.array(self.Sudoku.topRight))
        self.isTopRightSudokuDone = True
        if not self.isMiddleSudokuDone:
            for row in range(6, 9):
                for col in range(0, 3):
                    self.Sudoku.middle[row -
                                       6][col+6] = self.Sudoku.topRight[row][col]
            print("top right end\n", np.array(self.Sudoku.topRight))
            self.m.relevantSudokufinished = True

    def bLthreadFinished(self):
        print("bottom-left-is-done**********\n")
        print(np.array(self.Sudoku.bottomLeft))
        self.isBottomLeftSudokuDone = True
        if not self.isMiddleSudokuDone:
            for row in range(3):
                for col in range(6, 9):
                    self.Sudoku.middle[row+6][col -
                                              6] = self.Sudoku.bottomLeft[row][col]
            print("bottom-left end\n", np.array(self.Sudoku.bottomLeft))
            self.m.relevantSudokufinished = True
            self.bR.relevantSudokufinished = True

    def bRthreadFinished(self):
        print("bottom-right-is-done**********\n")
        print(np.array(self.Sudoku.bottomRight))
        self.isBottomRightSudokuDone = True
        if not self.isMiddleSudokuDone:
            for row in range(6, 9):
                for col in range(6, 9):
                    self.Sudoku.middle[row][col] = self.Sudoku.bottomRight[row-6][col-6]
            print("bottom-right end\n", np.array(self.Sudoku.bottomRight))
            self.m.relevantSudokufinished = True
            self.bL.relevantSudokufinished = True
        self.threadsFinished()

    def mthreadFinished(self):
        print("middle-is-done**********\n")
        print(np.array(self.Sudoku.middle))
        self.isMiddleSudokuDone = True

        # SET TOP RIGHT SUDOKU FOR SAMURAI
        if not self.isTopRightSudokuDone:
            for row in range(6, 9):
                for col in range(0, 3):
                    self.Sudoku.topRight[row][col] = self.Sudoku.middle[row-6][col+6]

        # SET TOP LEFT SUDOKU FOR SAMURAI
        if not self.isTopLeftSudokuDone:
            for row in range(6, 9):
                for col in range(6, 9):
                    self.Sudoku.topLeft[row][col] = self.Sudoku.middle[row-6][col-6]

        # SET BOTTOM LEFT SUDOKU FOR SAMURAI
        if not self.isTopLeftSudokuDone:
            for row in range(0, 3):
                for col in range(6, 9):
                    self.Sudoku.bottomLeft[row][col] = self.Sudoku.middle[row+6][col-6]

        self.tR.relevantSudokufinished = True
        self.tL.relevantSudokufinished = True
        self.bL.relevantSudokufinished = True
        self.bR.relevantSudokufinished = True
        self.threadsFinished()
        print("middle end\n", np.array(self.Sudoku.middle))

    def threadsFinished(self):
        self.gui.setClickables(True)
        self.gui.compareButton.setEnabled(False)
        self.setInfo("Sudoku is solved!")

        self.isTopLeftSudokuDone = False
        self.isTopRightSudokuDone = False
        self.isBottomLeftSudokuDone = False
        self.isBottomRightSudokuDone = False
        self.isMiddleSudokuDone = False

        self.tL.relevantSudokufinished = False
        self.tR.relevantSudokufinished = False
        self.bL.relevantSudokufinished = False
        self.bR.relevantSudokufinished = False
        self.m.relevantSudokufinished = False


# --------------SETTING DIGIT TO CELL---------------

    def tLsetCell(self, r, c, d, isEmpty):
        if isEmpty:
            getattr(self.gui, "cell_"+str(r) +
                    "_"+str(c)).setText("")
        else:
            getattr(self.gui, "cell_"+str(r) +
                    "_"+str(c)).setText(str(d))

    def tRsetCell(self, r, c, d, isEmpty):
        if isEmpty:
            if 5 < r < 9:
                getattr(self.gui, "cell_"+str(r) +
                        "_"+str(c+12)).setText("")
            else:
                getattr(self.gui, "cell_"+str(r) +
                        "_"+str(c+9)).setText("")
        else:
            if 5 < r < 9:
                getattr(self.gui, "cell_"+str(r) +
                        "_"+str(c+12)).setText(str(d))
            else:
                getattr(self.gui, "cell_"+str(r) +
                        "_"+str(c+9)).setText(str(d))

    def bLsetCell(self, r, c, d, isEmpty):
        if isEmpty:
            getattr(self.gui, "cell_"+str(r+12) +
                    "_"+str(c)).setText("")
        else:
            getattr(self.gui, "cell_"+str(r+12) +
                    "_"+str(c)).setText(str(d))

    def bRsetCell(self, r, c, d, isEmpty):
        if isEmpty:
            if 0 <= r < 3:
                getattr(self.gui, "cell_"+str(r+12) +
                        "_"+str(c+12)).setText("")
            else:
                getattr(self.gui, "cell_"+str(r+12) +
                        "_"+str(c+9)).setText("")
        else:
            if 0 <= r < 3:
                getattr(self.gui, "cell_"+str(r+12) +
                        "_"+str(c+12)).setText(str(d))
            else:
                getattr(self.gui, "cell_"+str(r+12) +
                        "_"+str(c+9)).setText(str(d))

    def mSetCell(self, r, c, d, isEmpty):
        if isEmpty:
            if 0 <= r < 3 or 6 <= r < 9:
                getattr(self.gui, "cell_"+str(r+6) +
                        "_"+str(c+6)).setText("")
            else:
                getattr(self.gui, "cell_"+str(r+6) +
                        "_"+str(c)).setText("")
        else:
            if 0 <= r < 3 or 6 <= r < 9:
                getattr(self.gui, "cell_"+str(r+6) +
                        "_"+str(c+6)).setText(str(d))
            else:
                getattr(self.gui, "cell_"+str(r+6) +
                        "_"+str(c)).setText(str(d))


# --------------SUDOKU THREAD WORKERS---------------
class solveTopLeftWorker(QThread):
    relevantSudokufinished = False
    setCell = pyqtSignal(int, int, int, object)
    sudoku = None

    def run(self):
        self.solve()

    def solve(self):
        for r in range(9):
            for c in range(9):
                if str(self.sudoku.topLeft[r][c]) == "*":
                    # sleep(0.0003)
                    for d in range(1, 10):
                        if self.isValid(r, c, d):
                            if self.isValidSamurai(r, c, d):
                                self.setCell.emit(r, c, d, False)
                                self.sudoku.topLeft[r][c] = str(d)
                                if self.solve():
                                    return True
                                self.setCell.emit(r, c, d, True)
                                self.sudoku.topLeft[r][c] = "*"

                    return False
        return True

    def isValid(self, r, c, d):
        for row in range(9):
            if str(self.sudoku.topLeft[row][c]) == str(d):
                return False
        for col in range(9):
            if str(self.sudoku.topLeft[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(self.sudoku.topLeft[row][col]) == str(d):
                    return False
        return True

    def isValidSamurai(self, r, c, d):
        if r >= 6 and c >= 6:
            if not self.relevantSudokufinished:
                if str(d) in self.sudoku.middle[r-6]:
                    if self.sudoku.middle[r-6].index(str(d)) + 6 != r:
                        return False
                if str(d) in [i[c-6] for i in self.sudoku.middle]:
                    if [i[c-6] for i in self.sudoku.middle].index(str(d)) + 6 != c:
                        return False
            return True
        else:
            return True


class solveTopRightWorker(QThread):
    relevantSudokufinished = False
    setCell = pyqtSignal(int, int, int, object)
    sudoku = None

    def run(self):
        self.solve()

    def solve(self):
        for r in range(9):
            for c in range(9):
                if str(self.sudoku.topRight[r][c]) == "*":
                    for d in range(1, 10):
                        if self.isValid(r, c, d):
                            if self.isValidSamurai(r, c, d):
                                self.setCell.emit(r, c, d, False)
                                self.sudoku.topRight[r][c] = str(d)
                                if self.solve():
                                    return True
                                self.setCell.emit(r, c, d, True)
                                self.sudoku.topRight[r][c] = "*"
                    return False

        return True

    def isValid(self, r, c, d):
        for row in range(9):
            if str(self.sudoku.topRight[row][c]) == str(d):
                return False
        for col in range(9):
            if str(self.sudoku.topRight[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(self.sudoku.topRight[row][col]) == str(d):
                    return False
        return True

    def isValidSamurai(self, r, c, d):
        if r >= 6 and c < 3:
            if not self.relevantSudokufinished:
                # MIDDLE ROW
                if str(d) in self.sudoku.middle[r-6]:
                    if self.sudoku.middle[r-6].index(str(d))-6 != c:
                        return False
                # MIDDLE COL
                if str(d) in [i[c+6] for i in self.sudoku.middle]:
                    if [i[c+6] for i in self.sudoku.middle].index(str(d)) + 6 != r:
                        return False
            return True
        else:
            return True


class solveBottomLeftWorker(QThread):
    relevantSudokufinished = False
    setCell = pyqtSignal(int, int, int, object)
    sudoku = None

    def run(self):
        self.solve()

    def solve(self):
        for r in range(9):
            for c in range(9):
                if str(self.sudoku.bottomLeft[r][c]) == "*":
                    for d in range(1, 10):
                        if self.isValid(r, c, d):
                            if self.isValidSamurai(r, c, d):
                                self.setCell.emit(r, c, d, False)
                                self.sudoku.bottomLeft[r][c] = str(d)
                                if self.solve():
                                    return True
                                self.setCell.emit(r, c, d, True)
                                self.sudoku.bottomLeft[r][c] = "*"
                    return False
        return True

    def isValid(self, r, c, d):
        for row in range(9):
            if str(self.sudoku.bottomLeft[row][c]) == str(d):
                return False
        for col in range(9):
            if str(self.sudoku.bottomLeft[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(self.sudoku.bottomLeft[row][col]) == str(d):
                    return False
        return True

    def isValidSamurai(self, r, c, d):
        if r < 3 and c >= 6:
            if not self.relevantSudokufinished:
                # MIDDLE ROW
                if str(d) in self.sudoku.middle[r+6]:
                    if self.sudoku.middle[r+6].index(str(d)) != c-6:
                        return False

                # MIDDLE COL
                if str(d) in [i[c-6] for i in self.sudoku.middle]:
                    if [i[c-6] for i in self.sudoku.middle].index(str(d)) != r+6:
                        return False

                # # BOTTOM RIGHT
                if str(d) in self.sudoku.bottomRight[r][0:3]:
                    print(self.sudoku.bottomRight[r][0:3], str(d), "aynı")
                    return False

            return True
        else:
            return True


class solveBottomRightWorker(QThread):
    relevantSudokufinished = False
    setCell = pyqtSignal(int, int, int, object)
    sudoku = None

    def run(self):
        self.solve()

    def solve(self):
        for r in range(9):
            for c in range(9):
                if str(self.sudoku.bottomRight[r][c]) == "*":
                    for d in range(1, 10):
                        if self.isValid(r, c, d):
                            if self.isValidSamurai(r, c, d):
                                self.setCell.emit(r, c, d, False)
                                self.sudoku.bottomRight[r][c] = str(d)
                                if self.solve():
                                    return True
                                self.setCell.emit(r, c, d, True)
                                self.sudoku.bottomRight[r][c] = "*"
                    return False
        return True

    def isValid(self, r, c, d):
        for row in range(9):
            if str(self.sudoku.bottomRight[row][c]) == str(d):
                return False
        for col in range(9):
            if str(self.sudoku.bottomRight[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(self.sudoku.bottomRight[row][col]) == str(d):
                    return False
        return True

    def isValidSamurai(self, r, c, d):
        if r < 3 and c < 3:
            if not self.relevantSudokufinished:
               # MIDDLE ROW
                if str(d) in self.sudoku.middle[r+6]:
                    if self.sudoku.middle[r+6].index(str(d))-6 != c:
                        return False
                # MIDDLE COL
                if str(d) in [i[c+6] for i in self.sudoku.middle]:
                    if [i[c+6] for i in self.sudoku.middle].index(str(d))-6 != r:
                        return False
                # BOTTOM LEFT
                if str(d) in self.sudoku.bottomLeft[r][-4:-1]:
                    return False

            return True
        else:
            return True


class solveMiddleWorker(QThread):
    relevantSudokufinished = False
    setCell = pyqtSignal(int, int, int, object)
    sudoku = None

    def run(self):
        self.solve()

    def solve(self):
        for r in range(9):
            for c in range(9):
                if str(self.sudoku.middle[r][c]) == "*":
                    # sleep(0.0003)
                    for d in range(1, 10):
                        if self.isValid(r, c, d):
                            if self.isValidSamurai(r, c, d):
                                self.setCell.emit(r, c, d, False)
                                self.sudoku.middle[r][c] = str(d)
                                if self.solve():
                                    return True
                                self.setCell.emit(r, c, d, True)
                                self.sudoku.middle[r][c] = "*"
                    return False
        return True

    def isValid(self, r, c, d):
        for row in range(9):
            if str(self.sudoku.middle[row][c]) == str(d):
                return False
        for col in range(9):
            if str(self.sudoku.middle[r][col]) == str(d):
                return False
        for row in range((r//3)*3, (r//3+1)*3):
            for col in range((c//3)*3, (c//3+1)*3):
                if str(self.sudoku.middle[row][col]) == str(d):
                    return False
        return True

    def isValidSamurai(self, r, c, d):
        # SAMURAI CONTROL FOR TOP LEFT SUDOKU
        if r < 3 and c < 3:
            if not self.relevantSudokufinished:
                # row
                if str(d) in self.sudoku.topLeft[r+6]:
                    if self.sudoku.topLeft[r+6].index(str(d))-6 != c:
                        return False
                # col
                if str(d) in [i[c+6] for i in self.sudoku.topLeft]:
                    if [i[c+6] for i in self.sudoku.topLeft].index(str(d)) != c+6:
                        return False
            return True

        # SAMURAI CONTROL FOR TOP RIGHT SUDOKU
        elif r < 3 and c > 5:
            if not self.relevantSudokufinished:
                # row
                if str(d) in self.sudoku.topRight[r+6]:
                    if self.sudoku.topRight[r+6].index(str(d))+6 != c:
                        return False
                # col
                if str(d) in [i[c-6] for i in self.sudoku.topRight]:
                    if [i[c-6] for i in self.sudoku.topRight].index(str(d)) != c:
                        return False
            return True

        # SAMURAI CONTROL FOR BOTTOM LEFT SUDOKU
        elif r > 5 and c < 3:
            if not self.relevantSudokufinished:
                # row
                if str(d) in self.sudoku.bottomLeft[r-6]:
                    if self.sudoku.bottomLeft[r-6].index(str(d))-6 != c:
                        return False
                # col
                if str(d) in [i[c+6] for i in self.sudoku.bottomLeft]:
                    if [i[c+6] for i in self.sudoku.bottomLeft].index(str(d)) != c:
                        return False
            return True

        # SAMURAI CONTROL FOR BOTTOM RIGHT SUDOKU
        elif r > 5 and c > 5:
            if not self.relevantSudokufinished:
                # row
                if str(d) in self.sudoku.bottomRight[r-6]:
                    if self.sudoku.bottomRight[r-6].index(str(d)) != c-6:
                        return False
                # col
                if str(d) in [i[c-6] for i in self.sudoku.bottomRight]:
                    if [i[c-6] for i in self.sudoku.bottomRight].index(str(d)) != c-6:
                        return False
            return True

        else:
            return True


class ThreadOperations():
    def __init__(self, sudoku, GUI, fiveThreadObject) -> None:
        self.sudoku = sudoku
        self.gui = GUI
        self.fiveThreadObject = fiveThreadObject
        tTopLeft = Thread(target=self.solveTopLeft,
                          args=(self.sudoku.topLeft,))
        tTopRight = Thread(target=self.solveTopRight,
                           args=(self.sudoku.topRight,))
        tMiddle = Thread(target=self.solveMiddle,
                         args=(self.sudoku.middle,))
        tBottomLeft = Thread(target=self.solveBottomLeft,
                             args=(self.sudoku.bottomLeft,))
        tBottomRight = Thread(target=self.solveBottomRight,
                              args=(self.sudoku.bottomRight,))
        self.threads = [tTopLeft, tTopRight, tMiddle,
                        tBottomLeft, tBottomRight]
        # tTopLeft.daemon = True
        # tTopRight.daemon = True
        # tMiddle.daemon = True
        # tBottomLeft.daemon = True
        # tBottomRight.daemon = True
        # [thread.start() for thread in self.threads]
        # [thread.join() for thread in self.threads]
        tTopLeft.start()
        tTopRight.start()
        tTopLeft.join()
        tTopRight.join()

        self.threadFinished()

    def threadFinished(self):
        self.gui.setClickables(True)
        self.gui.compareButton.setEnabled(False)
        self.fiveThreadObject.setInfo("All thread is done!")

    def solveTopLeft(self, sudoku):
        for r in range(9):
            for c in range(9):
                if str(sudoku[r][c]) == "*":
                    for d in range(1, 10):
                        if self.is_valid(r, c, d, sudoku):
                            getattr(self.gui, "cell_"+str(r) +
                                    "_"+str(c)).setText(str(d))
                            sudoku[r][c] = d
                            if self.solveTopLeft(sudoku):
                                return sudoku
                            getattr(self.gui, "cell_"+str(r) +
                                    "_"+str(c)).setText("")
                            sudoku[r][c] = "*"
                    return False

        return True

    def solveTopRight(self, sudoku):
        for r in range(9):
            for c in range(9):
                if str(sudoku[r][c]) == "*":
                    for d in range(1, 10):
                        if self.is_valid(r, c, d, sudoku):
                            if 5 < r < 9:
                                getattr(self.gui, "cell_"+str(r) +
                                        "_"+str(c+12)).setText(str(d))
                            else:
                                getattr(self.gui, "cell_"+str(r) +
                                        "_"+str(c+9)).setText(str(d))
                            sudoku[r][c] = d
                            if self.solveTopRight(sudoku):
                                return sudoku
                            if 5 < r < 9:
                                getattr(self.gui, "cell_"+str(r) +
                                        "_"+str(c+12)).setText("")
                            else:
                                getattr(self.gui, "cell_"+str(r) +
                                        "_"+str(c+9)).setText("")
                            sudoku[r][c] = "*"
                    return False

        return True

    def solveMiddle(self, sudoku):
        return

    def solveBottomLeft(self, sudoku):
        return

    def solveBottomRight(self, sudoku):
        return

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

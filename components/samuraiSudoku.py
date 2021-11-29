import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QUrl, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog
import pyqtgraph as pg
import numpy as np
from time import sleep

from templates.Ui_main import Ui_MainWindow
from components.fiveThread import FiveThreadOptions
from components.tenThread import TenThreadOptions
from components import tenThread


class SamuraiSudoku(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.threadCount = None
        self.loadButton.clicked.connect(self.chooseFile)
        self.clearButton.clicked.connect(self.clear)
        self.solveButton.clicked.connect(self.solveSudoku)
        self.compareButton.clicked.connect(self.compareSudoku)

    def chooseFile(self):
        self.filePath, self.filetype = QFileDialog.getOpenFileName(
            self, "Select Sample Sudoku File", "", "Text Files  (*.txt)")
        self.file = QUrl.fromLocalFile(self.filePath)
        self.isFileSelected = False
        if not self.file.isEmpty():
            self.fileName = self.file.fileName()
            self.isFileSelected = True
            self.oldFilePath = self.filePath
            self.oldFile = self.file
            self.setInfo("'{}' {}".format(self.fileName, "file selected!"))
            if self.checkFile(self.filePath):
                self.setInfo("File format is true!")
                self.startLoad()
            else:
                self.setInfo("Wrong file format!")
        elif self.file.isEmpty() and self.isFileSelected:
            self.isFileSelected = True
            self.setInfo("'{}' {}".format(self.fileName, "old file selected!"))
            if self.checkFile(self.filePath):
                self.setInfo("File format is true!")
                self.startLoad()
            else:
                self.setInfo("Wrong file format!")

        else:
            self.isFileSelected = False
            self.setInfo("File not selected!")

    def checkFile(self, file):
        self.matrix = []
        sampleFile = False
        if file:
            sampleFile = True
            with open(file, 'r') as reader:
                lines = reader.readlines()
            if len(lines) == 21:
                self.counter = 1
                self.control = 18
                for line in lines:
                    if len(line.rstrip()) == self.control:
                        temp = []
                        for digit in line.rstrip():
                            temp.append(digit)
                        self.matrix.append(temp)
                        self.cellRowsColsControl()
                        self.counter += 1
                    else:
                        sampleFile = False
                        return
            else:
                sampleFile = False
        return sampleFile

    def cellRowsColsControl(self):
        self.control = 21 if self.counter == 6 else self.control
        self.control = 9 if self.counter == 9 else self.control
        self.control = 21 if self.counter == 12 else self.control
        self.control = 18 if self.counter == 15 else self.control

    def setInfo(self, msg):
        self.logScreen.insertPlainText(
            "main: {}\n".format(msg))
        self.logScreen.ensureCursorVisible()

    def compareSudoku(self):
        con = False
        with open('fiveThreadLog.txt', 'r') as file:
            con = True if file.readline() else False
        with open('tenThreadLog.txt', 'r') as file:
            con = True if file.readline() else False
        if con:
            graphObject = CompareSudokuGraph(self)

    def startLoad(self):
        if self.threadRadioButton5.isChecked():
            self.fiveThreadObject = FiveThreadOptions(self)
            self.threadCount = 5
            self.fiveThreadObject.loadCells()

        else:
            self.tenThreadObject = TenThreadOptions(self)
            self.threadCount = 10
            self.tenThreadObject.loadCells()

    def clear(self):
        self.clearThread = ClearCellWorker()
        self.clearThread.daemon = True
        self.clearThread.clearCell.connect(self.clearCell)
        self.clearThread.finished.connect(self.clearCellIsDone)
        self.clearThread.start()
        self.setClickables(False)
        self.loadButton.setEnabled(True)
        self.setInfo("Sample sudoku is clearing..")

    def clearCell(self, i, j):
        getattr(self, "cell_"+str(i) +
                "_"+str(j)).clear()

    def clearCellIsDone(self):
        self.setInfo("Sample sudoku is cleared successfully!")

    def solveSudoku(self):
        self.setClickables(False)
        self.setInfo("Starting to solve..")
        if self.threadCount == 5:
            self.fiveThreadObject.solveSudoku()
        elif self.threadCount == 10:
            self.tenThreadObject.solveSudoku()
        else:
            self.setInfo("Unknow Error!")

    def setClickables(self, status):
        self.solveButton.setEnabled(status)
        self.loadButton.setEnabled(status)
        self.clearButton.setEnabled(status)
        self.threadRadioButton5.setEnabled(status)
        self.threadRadioButton10.setEnabled(status)
        self.compareButton.setEnabled(status)


class CompareSudokuGraph():
    def __init__(self, GUI):
        self.gui = GUI
        self.SEC_AXIS_RANGE = 7
        self.fiveTGraphSeconds = []
        self.tenTGraphSeconds = []
        self.fiveTGraphCount = []
        self.tenTGraphCount = []
        self.getDatafromTxt()
        self.createGraphics()

    def getDatafromTxt(self):
        with open('fiveThreadLog.txt', 'r') as file:
            line = file.readline()
            if line[0] == 'g':
                self.fiveTGraphSeconds.append(line.split("_")[1])
                self.fiveTGraphCount.append(line.split("_")[2])
        with open('tenThreadLog.txt', 'r') as file:
            line = file.readline()
            if line[0] == 'g':
                self.tenTGraphSeconds.append(float(line.split("_")[1]))
                self.tenTGraphCount.append(float(line.split("_")[2]))

    def createGraphics(self):
        self.createAxisLabels()
        self.createPlotWidgets()

    def createAxisLabels(self):
        self.gui.sudokuGraph.setLabel(
            axis='left', text='Count')
        self.gui.sudokuGraph.setLabel(
            axis='bottom', text='Second')

    def createPlotWidgets(self):
        self.pen = pg.mkPen('r', width=3)
        self.pen2 = pg.mkPen('b', width=3)
        self.sudokuGW = self.gui.sudokuGraph

        # five thread
        self.secondFT = self.fiveTGraphSeconds
        self.cellCountFT = self.fiveTGraphCount
        self.dataLine = self.sudokuGW.plot(
            self.secondFT, self.cellCountFT, pen=self.pen)

        # ten threads
        self.secondTT = self.tenTGraphSeconds
        self.cellCountTT = self.tenTGraphCount
        self.dataLine = self.sudokuGW.plot(
            self.secondTT, self.cellCountTT, pen=self.pen2)

        if len(self.fiveTGraphSeconds) > len(self.tenTGraphSeconds):
            self.sudokuGW.setXRange(0, len(self.fiveTGraphSeconds))
        else:
            self.sudokuGW.setXRange(0, len(self.tenTGraphSeconds))


class ClearCellWorker(QThread):
    clearCell = pyqtSignal(int, int)
    control = 18
    counter = 1

    def run(self):
        for i in range(21):
            for j in range(self.control):
                self.clearCell.emit(i, j)
                # sleep(0.002)
            self.cellRowsColsControl()
            self.counter += 1

    def cellRowsColsControl(self):
        self.control = 21 if self.counter == 6 else self.control
        self.control = 9 if self.counter == 9 else self.control
        self.control = 21 if self.counter == 12 else self.control
        self.control = 18 if self.counter == 15 else self.control


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SamuraiSudoku()
    win.show()
    sys.exit(app.exec())

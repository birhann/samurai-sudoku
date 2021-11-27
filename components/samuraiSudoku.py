import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QUrl, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog

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
        self.loadButton.clicked.connect(self.chooseFile)
        self.clearButton.clicked.connect(self.clearCells)

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

    def startLoad(self):
        if self.threadRadioButton5.isChecked():
            self.fiveThreadObject = FiveThreadOptions(self)
            self.fiveThreadObject.loadCells()
        else:
            self.tenThreadObject = TenThreadOptions(self)
            self.tenThreadObject.loadCells()

    def clearCells(self):
        self.clearThread = ClearCellWorker()
        self.clearThread.daemon = True
        self.clearThread.clearCell.connect(self.clearCell)
        self.clearThread.finished.connect(self.clearCellIsDone)
        self.clearThread.start()
        self.setInfo("Sample sudoku is clearing..")

    def clearCell(self, i, j):
        getattr(self, "cell_"+str(i) +
                "_"+str(j)).clear()

    def clearCellIsDone(self):
        self.setInfo("Sample sudoku is cleared successfully!")


class ClearCellWorker(QThread):
    clearCell = pyqtSignal(int, int)
    control = 18
    counter = 1

    def run(self):
        for i in range(21):
            for j in range(self.control):
                self.clearCell.emit(i, j)
                sleep(0.002)
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

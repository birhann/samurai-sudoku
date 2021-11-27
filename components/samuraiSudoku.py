import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QFileDialog

from templates.Ui_main import Ui_MainWindow
from components import fiveThread
from components import tenThread


class SamuraiSudoku(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loadButton.clicked.connect(self.chooseFile)

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
            else:
                self.setInfo("Wrong file format!")
        elif self.file.isEmpty() and self.isFileSelected:
            self.isFileSelected = True
            self.setInfo("'{}' {}".format(self.fileName, "old file selected!"))
            if self.checkFile(self.filePath):
                self.setInfo("File format is true!")
            else:
                self.setInfo("Wrong file format!")

        else:
            self.isFileSelected = False
            self.setInfo("File not selected!")

    def checkFile(self, file):
        matrix = []
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
                        matrix.append(temp)

                        self.control = 21 if self.counter == 6 else self.control
                        self.control = 9 if self.counter == 9 else self.control
                        self.control = 21 if self.counter == 12 else self.control
                        self.control = 18 if self.counter == 15 else self.control
                        self.counter += 1

                        print(line, len(line.rstrip()),
                              self.counter, self.control)
                    else:
                        print(line, len(line.rstrip()),
                              self.counter, self.control)
                        sampleFile = False
                        return
            else:
                sampleFile = False
        return sampleFile

    def setInfo(self, msg):
        self.logScreen.insertPlainText(
            "main: {}\n".format(msg))
        self.logScreen.ensureCursorVisible()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SamuraiSudoku()
    win.show()
    sys.exit(app.exec())

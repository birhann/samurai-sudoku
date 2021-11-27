import sys
from PyQt5.QtWidgets import QApplication
from components import samuraiSudoku

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = samuraiSudoku.SamuraiSudoku()
    window.show()
    sys.exit(app.exec_())

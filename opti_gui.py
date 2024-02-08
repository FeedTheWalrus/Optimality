import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QCheckBox, QHBoxLayout
import constraints

class OTTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.constraints = [func.__name__ for func in constraints.get_constraint_functions()]
        self.words = []  # To store input-output word pairs
        self.selected_constraints = []  # To store selected constraints
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OT Violation Chart')
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        mainLayout = QVBoxLayout()
        inputLayout = QHBoxLayout()
        constraintsLayout = QHBoxLayout()

        # Input fields for words
        self.inputWord = QLineEdit(self)
        self.outputWord = QLineEdit(self)
        inputLayout.addWidget(QLabel("Input Word:"))
        inputLayout.addWidget(self.inputWord)
        inputLayout.addWidget(QLabel("Output Word:"))
        inputLayout.addWidget(self.outputWord)

        # Add Word button
        addWordButton = QPushButton("Add Word Pair", self)
        addWordButton.clicked.connect(self.addWordPair)
        inputLayout.addWidget(addWordButton)

        # Constraint checkboxes
        for constraint_name in self.constraints:
            checkBox = QCheckBox(constraint_name, self)
            checkBox.stateChanged.connect(self.updateSelectedConstraints)
            constraintsLayout.addWidget(checkBox)

        # Table for showing data
        self.tableWidget = QTableWidget(self)
        self.updateTable()

        # Update Table button
        updateTableButton = QPushButton("Update Table", self)
        updateTableButton.clicked.connect(self.updateTable)

        # Add widgets to layout
        mainLayout.addLayout(inputLayout)
        mainLayout.addLayout(constraintsLayout)
        mainLayout.addWidget(updateTableButton)
        mainLayout.addWidget(self.tableWidget)

        # Set the layout
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def addWordPair(self):
        input_word = self.inputWord.text()
        output_word = self.outputWord.text()
        if input_word and output_word:
            self.words.append((input_word, output_word))
            self.inputWord.clear()
            self.outputWord.clear()
            self.updateTable()

    def updateSelectedConstraints(self, state):
        sender = self.sender()
        if state == 2:  # Checked
            if sender.text() not in self.selected_constraints:
                self.selected_constraints.append(sender.text())
        elif state == 0:  # Unchecked
            if sender.text() in self.selected_constraints:
                self.selected_constraints.remove(sender.text())

    def updateTable(self):
        # Set table dimensions
        self.tableWidget.setRowCount(len(self.words))
        self.tableWidget.setColumnCount(len(self.selected_constraints) + 2)  # Additional columns for input and output words

        # Set table headers
        headers = ["Input", "Output"] + self.selected_constraints
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Populate the table
        for i, (input_word, output_word) in enumerate(self.words):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(input_word))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(output_word))

            # Calculate constraint violations
            for j, constraint_name in enumerate(self.selected_constraints, start=2):
                # Retrieve the function object using its name
                constraint_func = getattr(constraints, constraint_name)
                violation_count = constraint_func(input_word, output_word)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(violation_count)))


            

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = OTTableWindow()
    mainWin.show()
    sys.exit(app.exec_())

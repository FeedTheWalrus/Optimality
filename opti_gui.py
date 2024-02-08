import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QCheckBox, QHBoxLayout
import constraints
import inspect

class OTTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.constraints = [func.__name__ for func in constraints.get_constraint_functions()]
        self.words = []  # To store input-output word pairs
        self.selected_constraints = []  # To store selected constraints
        self.input_words = 'snow' # To store input word
        self.output_words = ['snow', 'sno', 'sow', 'so', 'no']
        self.initUI()


    def initUI(self):
        self.setWindowTitle('OT Violation Chart')
        self.setGeometry(200, 100, 1000, 500)

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
        # Assume self.inputWord is a QLineEdit that holds the single input word
        if self.input_word is None:
            self.input_word = self.inputWord.text()  # Only set the input_word once

        output_word = self.outputWord.text()
        if output_word:
            self.output_words.append(output_word)
            self.outputWord.clear()
            self.updateTable()  # Update the table to reflect the new word pair

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
        self.tableWidget.setRowCount(len(self.output_words))
        self.tableWidget.setColumnCount(len(self.selected_constraints) + 2)  # Additional columns for input and output words

        # Set table headers
        headers = ["Input", "Output"] + self.selected_constraints
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Populate the table
        for i, output_word in enumerate(self.output_words):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(self.input_words))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(output_word))

            # Calculate constraint violations
            for j, constraint_name in enumerate(self.selected_constraints, start=2):
                # Retrieve the function object using its name
                constraint_func = getattr(constraints, constraint_name)
                
                # Check the number of arguments the constraint function expects
                num_args = len(inspect.signature(constraint_func).parameters)
                
                # Call the constraint function with the correct number of arguments
                if num_args == 1:
                    violation_count = constraint_func(output_word)
                elif num_args == 2:
                    violation_count = constraint_func(self.input_words, output_word)
                else:
                    raise ValueError(f"Constraint function {constraint_name} has an unexpected number of arguments.")
                
                # Set the item in the table (assuming you want to display the violation count)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(violation_count)))



# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = OTTableWindow()
    mainWin.show()
    sys.exit(app.exec_())

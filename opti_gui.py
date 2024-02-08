import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QCheckBox, QHBoxLayout, QComboBox, QGridLayout
import constraints
import inspect
import qdarkstyle

class OTTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.constraints = [func.__name__ for func in constraints.get_constraint_functions()]
        self.words = []  # To store input-output word pairs
        self.selected_constraints = []  # To store selected constraints
        self.inputWords = 'snow' # To store input word
        self.outputWords = ['snow', 'sno', 'sow', 'so', 'no']
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

        # Winner Selection Dropdown
        self.winnerSelection = QComboBox(self)
        self.winnerSelection.addItems(self.outputWords)
        self.winnerSelection.currentIndexChanged.connect(self.updateWLTable)
        inputLayout.addWidget(QLabel("Select Winner:"))
        inputLayout.addWidget(self.winnerSelection)

        # Table for Winners/Losers table
        self.tableWidget_2 = QTableWidget(self)
        self.updateWLTable()

        # Update Table button
        updateTableButton = QPushButton("Update Table", self)
        updateTableButton.clicked.connect(self.updateTable)

        # Clear Table button
        clearTableButton = QPushButton("Clear Table", self)
        clearTableButton.clicked.connect(self.clearTable)

        # Add widgets to layout
        mainLayout.addLayout(inputLayout)
        mainLayout.addLayout(constraintsLayout)
        mainLayout.addWidget(updateTableButton)
        mainLayout.addWidget(self.tableWidget)
        mainLayout.addWidget(self.tableWidget_2)
        mainLayout.addWidget(clearTableButton)

        # Set the layout
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def addWordPair(self):
        output_word = self.outputWord.text()
        if output_word:
            self.outputWords.append(output_word)  # Use the correct variable name
            self.outputWord.clear()
            self.winnerSelection.clear()
            self.winnerSelection.addItems(self.outputWords)
        self.updateTable()

    def updateSelectedConstraints(self, state):
        sender = self.sender()
        if state == 2:  # Checked
            if sender.text() not in self.selected_constraints:
                self.selected_constraints.append(sender.text())
        elif state == 0:  # Unchecked
            if sender.text() in self.selected_constraints:
                self.selected_constraints.remove(sender.text())
        self.updateTable()

    def clearTable(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.output_words = []

    def updateWLTable(self):
        # Set table dimensions
        self.tableWidget_2.setRowCount(len(self.outputWords))
        self.tableWidget_2.setColumnCount(len(self.selected_constraints) + 2)  # Additional columns for input and output words

        # Set table headers
        headers = ["Winner", "Loser"] + self.selected_constraints
        self.tableWidget_2.setHorizontalHeaderLabels(headers)

        selected_winner = self.winnerSelection.currentText()

        for i, output_word in enumerate(self.outputWords):
            if output_word == selected_winner:
                winner_label = "Winner"
            else:
                winner_label = "Loser"

            self.tableWidget_2.setItem(i, 0, QTableWidgetItem(winner_label))
            self.tableWidget_2.setItem(i, 1, QTableWidgetItem(output_word))

            # Determine whether the constraint favours the winner (input) or loser (output), for each constraint
            for j, constraint_name in enumerate(self.selected_constraints, start=2):
                # Retrieve the function object using its name
                constraint_func = getattr(constraints, constraint_name)

                # Check the number of arguments the constraint function expects
                num_args = len(inspect.signature(constraint_func).parameters)

                # Call the constraint function with the correct number of arguments
                if num_args == 1:
                    favours_winner = constraint_func(output_word)
                elif num_args == 2:
                    favours_winner = constraint_func(self.inputWords, output_word)
                else:
                    raise ValueError(f"Constraint function {constraint_name} has an unexpected number of arguments.")

                if favours_winner:
                    self.tableWidget_2.setItem(i, j, QTableWidgetItem("Winner"))
                else:
                    self.tableWidget_2.setItem(i, j, QTableWidgetItem("Loser"))


    def updateTable(self):
        # Set table dimensions
        self.tableWidget.setRowCount(len(self.outputWords))
        self.tableWidget.setColumnCount(len(self.selected_constraints) + 2)  # Additional columns for input and output words

        # Set table headers
        headers = ["Input", "Output"] + self.selected_constraints
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Populate the table
        for i, output_word in enumerate(self.outputWords):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(self.inputWords))
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
                    violation_count = constraint_func(self.inputWords, output_word)
                else:
                    raise ValueError(f"Constraint function {constraint_name} has an unexpected number of arguments.")
                
                # Set the item in the table (assuming you want to display the violation count)
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(violation_count)))

custom_stylesheet = """
QWidget {
    color: #D3D7CF; /* Text color */
    background-color: #2E3436; /* Background color */
}

QLabel, QCheckBox, QLineEdit, QTextEdit, QSpinBox, QComboBox, QListWidget {
    background-color: #393939; /* Lighter background for some widgets */
    border: 1px solid #555; /* Border for input widgets */
}

QHeaderView::section {
    background-color: #505050; /* Header background color */
    color: #D3D7CF; /* Header text color */
    border: 1px solid #404040; /* Header border color */
    padding: 4px; /* Header padding */
    font-size: 10pt; /* Header font size */
}

QPushButton {
    background-color: #555753; /* Button background */
    border: 1px solid #333;
}

QPushButton:hover {
    background-color: #729FCF; /* Button hover color */
}

QPushButton:pressed {
    background-color: #3465A4; /* Button pressed color */
}

QCheckBox {
    spacing: 5px; /* Spacing around checkbox text */
}

QCheckBox::indicator {
    width: 18px; /* Width of checkbox */
    height: 18px; /* Height of checkbox */
}

QCheckBox::indicator:unchecked {
    image: url(:/checkbox_unchecked.svg); /* Custom image for unchecked state */
}

QCheckBox::indicator:checked {
    image: url(:/checkbox_checked.svg); /* Custom image for checked state */
}

QTableWidget {
    gridline-color: #444; /* Color of grid lines in tables */
    border: 1px solid #222; /* Table border */
}

QTableWidget::item {
    padding: 5px; /* Padding for table items */
    border: 1px solid #222; /* Table item border */
}

QTableWidget::item:selected {
    background-color: #404040; /* Selected item background color */
    color: #D3D7CF; /* Selected item text color */
    border: 1px solid #222; /* Selected item border */
}

QScrollBar:vertical, QScrollBar:horizontal {
    border: 1px solid #222; /* Scrollbar border */
    background: #333; /* Scrollbar background */
    width: 10px; /* Width of vertical scrollbar */
    height: 10px; /* Height of horizontal scrollbar */
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #555; /* Scrollbar handle color */
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #777; /* Scrollbar handle hover color */
}

/* Add more custom styles for other widgets as needed */
"""

# Run the application
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + custom_stylesheet)

        mainWin = OTTableWindow()
        mainWin.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QVBoxLayout, QWidget, 
                             QLabel, QCheckBox, QHBoxLayout, QComboBox, 
                             QGridLayout, QRadioButton, QSizePolicy, QSpacerItem
                            )
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import constraints
import inspect
import qdarkstyle

default_input = 'snow'
default_output = ['snow', 'sno', 'sow', 'so', 'no']

class OTTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        self.constraints = [func.__name__ for func in constraints.get_constraint_functions()]
        self.words = []  # To store input-output word pairs
        self.selected_constraints = []  # To store selected constraints
        self.inputWords = default_input
        self.outputWords = default_output
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Optimality Chart')
        self.setGeometry(200, 100, 1000, 800)

        # Horizontal Layout for input and constraints
        topLayout = QHBoxLayout()
        # Layouts
        mainLayout = QVBoxLayout()
        inputLayout = QVBoxLayout()
        constraintsLayout = QGridLayout()
        

        # Input fields for words
        self.inputWord = QLineEdit(self)
        self.outputWord = QLineEdit(self)
        inputLayout.addWidget(QLabel("Input Word:"))
        inputLayout.addWidget(self.inputWord)
        self.inputWord.setFixedWidth(200)
        inputLayout.addWidget(QLabel("Output Word:"))
        inputLayout.addWidget(self.outputWord)
        self.outputWord.setFixedWidth(200)

        # Add Word button
        addWordButton = QPushButton("Add Word Pair", self)
        addWordButton.clicked.connect(self.addWordPair)
        inputLayout.addWidget(addWordButton)
        addWordButton.setFixedWidth(200)

        row, col = 0, 0
        max_cols = 2
        max_rows = 6
        # Constraint checkboxes. Start activated.
        for i, constraint_name in enumerate(self.constraints):
            checkBox = QCheckBox(constraint_name, self)
            checkBox.stateChanged.connect(self.updateSelectedConstraints)
            checkBox.setMaximumWidth(115)
            # set alignment to left

            constraintsLayout.addWidget(checkBox, row, col, 1,1, Qt.AlignLeft)

            row += 1
            if row >= max_rows:
                row = 0
                col += 1

            # col += 1
            # if col >= max_cols:
            #     col = 0
            #     row += 1

        constraintsLayout.setHorizontalSpacing(30)
        constraintsLayout.setVerticalSpacing(10)
        constraintsLayout.setColumnMinimumWidth(1, 10)

        topLayout.addLayout(inputLayout, 0)
        topLayout.addLayout(constraintsLayout, 0)
        
        # add spacer
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        topLayout.addItem(spacerItem)

        # Table for showing data
        self.tableWidget = QTableWidget(self)
        self.updateTable()

        # Winner Selection Dropdown
        self.winnerSelection = QComboBox(self)
        self.winnerSelection.addItems(self.outputWords)
        self.winnerSelection.currentIndexChanged.connect(self.updateWLTable)
        # Change size of dropdown
        self.winnerSelection.setFixedWidth(200)

        # Table for Winners/Losers table
        self.tableWidget_WL = QTableWidget(self)
        self.updateWLTable()

        # Update Table button
        updateTableButton = QPushButton("Update Tables", self)
        updateTableButton.clicked.connect(self.updateTable)
        updateTableButton.setFixedWidth(200)

        # Clear Table button
        clearTableButton = QPushButton("Clear Tables", self)
        clearTableButton.clicked.connect(self.clearTable)
        clearTableButton.setFixedWidth(200)

        # Add widgets to layout
        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(updateTableButton)
        mainLayout.addWidget(clearTableButton)
        mainLayout.addWidget(self.tableWidget)
        mainLayout.addWidget(QLabel("Select Winner:"))
        mainLayout.addWidget(self.winnerSelection)
        mainLayout.addWidget(self.tableWidget_WL)

        # Set the layout
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def addWordPair(self):
        input_word = self.inputWord.text()
        output_word = self.outputWord.text()
        if input_word:
            self.inputWords = input_word
        #check if input word is in output word list. If not, add it to first index
        if input_word not in self.outputWords:
            self.outputWords.insert(0, input_word)

        if output_word:
            self.outputWords.append(output_word)  # Use the correct variable name
            self.outputWord.clear()
            self.winnerSelection.clear()
            self.winnerSelection.addItems(self.outputWords)
        self.updateTable()
        self.updateWLTable()

    def updateSelectedConstraints(self, state):
        sender = self.sender()
        if state == 2:  # Checked
            if sender.text() not in self.selected_constraints:
                self.selected_constraints.append(sender.text())
        elif state == 0:  # Unchecked
            if sender.text() in self.selected_constraints:
                self.selected_constraints.remove(sender.text())
        self.updateTable()
        self.updateWLTable()

    def clearTable(self):
        #clear default words
        self.inputWords = ''
        self.outputWords = []

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget_WL.clearContents()
        self.tableWidget_WL.setRowCount(0)
    

    def updateWLTable(self):
        # Set table dimensions
        self.tableWidget_WL.setRowCount(len(self.outputWords) - 1)  # Exclude the winner word
        self.tableWidget_WL.setColumnCount(len(self.selected_constraints) + 2)  # Additional columns for Winner and Loser

        # Set table headers
        headers = ["Selected Winner", "Loser"] + self.selected_constraints
        self.tableWidget_WL.setHorizontalHeaderLabels(headers)

        selected_winner = self.winnerSelection.currentText()
        loser_words = [word for word in self.outputWords if word != selected_winner]

        row = 0
        for loser_word in loser_words:
            # Set Winner and Loser words in each row
            self.tableWidget_WL.setItem(row, 0, QTableWidgetItem(selected_winner))
            self.tableWidget_WL.setItem(row, 1, QTableWidgetItem(loser_word))

            # Compare each constraint against Winner and Loser
            for j, constraint_name in enumerate(self.selected_constraints, start=2):
                constraint_func = getattr(constraints, constraint_name)
                num_args = len(inspect.signature(constraint_func).parameters)

                if num_args == 1:
                    favours_winner = constraint_func(selected_winner)
                    favours_loser = constraint_func(loser_word)
                elif num_args == 2:
                    favours_winner = constraint_func(self.inputWords, selected_winner)
                    favours_loser = constraint_func(self.inputWords, loser_word)
                else:
                    raise ValueError(f"Constraint function {constraint_name} has an unexpected number of arguments.")

                if favours_winner and not favours_loser:
                    self.tableWidget_WL.setItem(row, j, QTableWidgetItem("Winner"))
                    self.tableWidget_WL.item(row, j).setBackground(QtGui.QColor(0, 255, 0))  # Green for Winner
                elif not favours_winner and favours_loser:
                    self.tableWidget_WL.setItem(row, j, QTableWidgetItem("Loser"))
                    self.tableWidget_WL.item(row, j).setBackground(QtGui.QColor(255, 0, 0))  # Red for Loser
                else:
                    self.tableWidget_WL.setItem(row, j, QTableWidgetItem("E"))


            row += 1


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

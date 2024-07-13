import sys
import os
import zipfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QListWidgetItem, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from subtitle_processor import SubtitleProcessor
from PyQt5 import QtGui

class SubtitleFixer(QWidget):
    def __init__(self):
        """
        Initializes the SubtitleFixer application window with all the necessary widgets and functionality.
        Sets up the layout, buttons, and connects signals to slots.
        """
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('winicon.png'))  # Set the application window icon
        self.setWindowTitle("SRT Fixer")  # Set the window title
        self.setGeometry(100, 100, 600, 400)  # Set the window size and position
        self.setAcceptDrops(True)  # Allow drag and drop functionality

        # Set up the layout for the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add a label instructing users to drag and drop files or use the button
        self.label = QLabel("Drag and drop .srt files here or use the button below to add files.")
        self.layout.addWidget(self.label)

        # Create a list widget to display the added files
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        # Button to choose files via a file dialog
        self.choose_button = QPushButton("Choose file(s)")
        self.choose_button.clicked.connect(self.choose_files)  # Connect button click to the choose_files method
        self.layout.addWidget(self.choose_button)

        # Button to clear all files from the list
        self.clear_all_files_button = QPushButton("Clear all files")
        self.clear_all_files_button.clicked.connect(self.clear_all_files)  # Connect button click to the clear_all_files method
        self.clear_all_files_button.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.clear_all_files_button)

        # Button to fix the selected files
        self.fix_button = QPushButton("Fix file(s)")
        self.fix_button.clicked.connect(self.fix_files)  # Connect button click to the fix_files method
        self.layout.addWidget(self.fix_button)

        # Button to save the fixed files as a zip archive
        self.save_button = QPushButton("Save file(s)")
        self.save_button.clicked.connect(self.save_files)  # Connect button click to the save_files method
        self.save_button.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.save_button)

        # Footer label displaying creator information
        self.footer_label = QLabel("Made by Arhan Goncalı | © Grizzly Industries | Github: ArhanGoncaliOfficial")
        self.footer_label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)  # Center align and place at the bottom
        self.footer_label.setStyleSheet("background-color: orange; font-weight:400;")  # Style the footer
        self.layout.addWidget(self.footer_label)

        self.fixed_files = []  # List to store tuples of (file_path, content) for fixed files
        self.fixed_contents = []  # List to store fixed contents (not used in the current version but could be useful for further extensions)
        self.subtitle_processor = SubtitleProcessor("character_mapping.csv")  # Instantiate SubtitleProcessor with character mappings CSV file

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handles the drag enter event to accept only files being dragged onto the window.
        
        Parameters:
        event (QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # Accept the drag event if it contains URLs

    def dropEvent(self, event: QDropEvent):
        """
        Handles the drop event to add the dropped files to the list.
        
        Parameters:
        event (QDropEvent): The drop event.
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()  # Convert the URL to a local file path
            self.add_file(file_path)  # Add the file to the list

    def clear_all_files(self):
        """
        Clears all files from the list and disables the 'Clear all files' button.
        """
        self.file_list.clear()  # Clear the list widget
        self.clear_all_files_button.setEnabled(False)  # Disable the 'Clear all files' button

    def choose_files(self):
        """
        Opens a file dialog to choose .srt files and adds them to the list.
        """
        files, _ = QFileDialog.getOpenFileNames(self, "Choose file(s)", "", "Subtitle Files (*.srt)")
        for file in files:
            self.add_file(file)  # Add each selected file to the list

    def add_file(self, file_path):
        """
        Adds a file to the list, ensuring it is a .srt file and not already added.
        
        Parameters:
        file_path (str): The path to the .srt file.
        """
        if not file_path.endswith(".srt"):
            QMessageBox.critical(self, "Error", "Only .srt files are allowed!")  # Show error if the file is not a .srt file
            return
        
        existing_items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if file_path in existing_items:
            QMessageBox.warning(self, "Warning", f"The file '{file_path}' is already added.")  # Show warning if the file is already added
            return

        # Create a new list item for the file and add a checkbox for selection
        item = QListWidgetItem(file_path)
        checkbox = QCheckBox()
        checkbox.setChecked(True)  # Check the checkbox by default
        self.file_list.addItem(item)  # Add the item to the list
        self.file_list.setItemWidget(item, checkbox)  # Set the checkbox as the item widget
        self.clear_all_files_button.setEnabled(True)  # Enable the 'Clear all files' button

    def fix_files(self):
        """
        Fixes the selected .srt files and stores the fixed contents in memory.
        """
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "No files found to fix!")  # Show warning if there are no files to fix
            return

        self.fixed_files = []
        self.fixed_contents = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            checkbox = self.file_list.itemWidget(item)
            if checkbox.isChecked():  # Check if the file is selected for fixing
                file_path = item.text()
                try:
                    fixed_content = self.subtitle_processor.fix_corrupted_srt_file(file_path)  # Fix the corrupted subtitle file
                    fixed_file_path = file_path.replace(".srt", "_tr.srt")  # Create a new file path for the fixed file
                    self.fixed_files.append((fixed_file_path, fixed_content))  # Add the fixed file to the list
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to fix file: {file_path}\n{str(e)}")  # Show error if fixing fails
                    return

        if self.fixed_files:
            self.save_button.setEnabled(True)  # Enable the 'Save file(s)' button if there are fixed files
            QMessageBox.information(self, "Success", "Files fixed successfully. Click 'Save file(s)' to save them as a zip archive.\n\nThe files are temporarily stored in memory. They will be deleted if you close the program now, so please save your files!")  # Show success message

    def save_files(self):
        """
        Opens a file dialog to save the fixed files as a zip archive.
        """
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file(s)", "subtitle", "Zip Files (*.zip)")
        if save_path:
            try:
                with zipfile.ZipFile(save_path, 'w') as zipf:
                    for fixed_file_path, fixed_content in self.fixed_files:
                        with zipf.open(os.path.basename(fixed_file_path), 'w') as file:
                            file.write(fixed_content.encode('utf-8'))  # Write the fixed content to the zip file
                QMessageBox.information(self, "Success", f"Files saved successfully to {save_path}")  # Show success message
                self.save_button.setEnabled(False)  # Disable the 'Save file(s)' button
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save files: {str(e)}")  # Show error if saving fails

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application instance
    window = SubtitleFixer()  # Create an instance of the SubtitleFixer class
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application

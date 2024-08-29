import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QSettings, QFileInfo
from ultralytics import YOLO

class FractureDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fracture Detection")
        self.setFixedSize(1240, 980)
        self.setStyleSheet("background-color: #e0f7fa;")

        # Load YOLO model
        self.model = YOLO("D:/ACM AI ML/project/FINAL/best.pt")

        # Set up UI components
        self.title = QLabel("  FINGER FRACTURE DETECTION SYSTEM  ", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 28px; font-family: 'Times New Roman', Times, serif;  color: #FFFFFF; font-weight: bold; font-style: italic; background: #4682B4")

        self.label = QLabel("Click the button below to select an image to detect fractures", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333")

        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setStyleSheet("border: 2px solid #4682B4; background: #f0f0f0;")
        self.canvas.setFixedSize(920, 680)

        self.load_button = QPushButton("Load Image", self)
        self.load_button.setStyleSheet("font-size: 26px; padding: 10px; background-color: #0288D1; color: #FFFFFF; border: none; border-radius: 25px; font-style: italic")
        self.load_button.clicked.connect(self.load_image)

        # Top layout
        top_layout = QVBoxLayout()
        self.title.setContentsMargins(0, 0, 0, 20)
        self.label.setContentsMargins(0, 0, 0, 20)
        top_layout.addWidget(self.title)
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.load_button)
        top_layout.setAlignment(Qt.AlignCenter)

        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.setAlignment(Qt.AlignCenter)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(canvas_layout)
        main_layout.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize QSettings
        self.settings = QSettings("YourCompany", "YourApp")

    def load_image(self):
        # Retrieve last used directory
        last_directory = self.settings.value("last_directory", "")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", last_directory, "Images (*.png *.xpm *.jpg *.jpeg)")
         
        if file_path:
            current_directory = QFileInfo(file_path).path()
            self.settings.setValue("last_directory", current_directory)

            # Load and process the image
            image = cv2.imread(file_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            results = self.model(image_rgb)

            if len(results) == 0 or len(results[0].boxes) == 0:
                self.label.setText("NO FRACTURE DETECTED")
                self.label.setStyleSheet("font-size: 26px; font-weight: bold; color: green")
            else:
                self.label.setText("FRACTURE DETECTED")
                self.label.setStyleSheet("font-size: 26px; font-weight: bold; color: red")

                # Iterate over detected boxes
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    confidence = box.conf[0]  # Confidence score

                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    label = f"{confidence:.2f}"
                    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Resize the image to fit within the fixed canvas size
            image_resized = cv2.resize(image, (self.canvas.width(), self.canvas.height()))
            height, width, _ = image_resized.shape
            bytes_per_line = 3 * width
            q_image = QImage(image_resized.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Update the canvas
            self.canvas.setPixmap(QPixmap.fromImage(q_image))
            self.canvas.setScaledContents(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FractureDetectionApp()
    window.show()
    sys.exit(app.exec_())

# main.py
# Responsible for initializing and running the main application window, managing user interactions, and orchestrating the overall functionality of the 3D viewer.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSlider, QDockWidget, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDoubleSpinBox, QCheckBox
from PyQt5.QtCore import Qt
from opengl_widget import OpenGLWidget
from apply_dark_theme import apply_dark_theme

class SimpleObjViewer(QMainWindow):
    def __init__(self):
        super(SimpleObjViewer, self).__init__()
        self.setWindowTitle("Vince's 3D Viewer")
        self.near_clip = 0.1
        self.far_clip = 100.0
        self.init_gui()
        self.obj_file = None

    def change_background_shade(self, value):
        shade = value / 255.0
        self.opengl_widget.bg_color = [shade, shade, shade, 1.0]
        self.opengl_widget.update()
        
    def change_near_clip(self, value: float):
        self.opengl_widget.change_near_clip(value)

    def change_far_clip(self, value: float):
        self.opengl_widget.change_far_clip(value)

    def toggle_wireframe_mode(self, state):
        self.opengl_widget.set_wireframe_mode(state == Qt.Checked)

    def change_wireframe_thickness(self, value):
        self.opengl_widget.set_wireframe_thickness(value)

    def init_gui(self):
        self.opengl_widget = OpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)
        self.resize(800, 600)
        self.create_menu_bar()
        self.create_dock_widgets()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.load_obj)

    def load_obj(self):
        self.obj_file, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj)")
        if self.obj_file:
            self.opengl_widget.load_model(self.obj_file)

    def create_dock_widgets(self):
        # Creating a dock widget
        dock = QDockWidget("Controls", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)

        # Creating a widget to hold controls
        controls_widget = QWidget()
        layout = QVBoxLayout()

        # Creating a horizontal layout for the background color control
        bg_layout = QHBoxLayout()
        bg_label = QLabel("Background Color")
        bg_slider = QSlider(Qt.Horizontal)
        bg_slider.setMinimum(0)
        bg_slider.setMaximum(255)
        bg_slider.setValue(128)
        bg_slider.valueChanged.connect(self.change_background_shade)
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(bg_slider)
        layout.addLayout(bg_layout)

        # Creating a horizontal layout for the near clip control
        near_clip_layout = QHBoxLayout()
        near_clip_label = QLabel("Near Clip Plane")
        near_clip_spinbox = QDoubleSpinBox()
        near_clip_spinbox.setRange(0.01, 10.0)
        near_clip_spinbox.setSingleStep(0.01)
        near_clip_spinbox.setValue(0.1)
        near_clip_spinbox.valueChanged.connect(self.change_near_clip)
        near_clip_layout.addWidget(near_clip_label)
        near_clip_layout.addWidget(near_clip_spinbox)
        layout.addLayout(near_clip_layout)

        # Creating a horizontal layout for the far clip control
        far_clip_layout = QHBoxLayout()
        far_clip_label = QLabel("Far Clip Plane")
        far_clip_spinbox = QDoubleSpinBox()
        far_clip_spinbox.setRange(10.0, 1000.0)
        far_clip_spinbox.setSingleStep(1.0)
        far_clip_spinbox.setValue(500.0)
        far_clip_spinbox.valueChanged.connect(self.change_far_clip)
        far_clip_layout.addWidget(far_clip_label)
        far_clip_layout.addWidget(far_clip_spinbox)
        layout.addLayout(far_clip_layout)

        # Creating a checkbox for wireframe mode
        self.wireframe_checkbox = QCheckBox("Wireframe Mode")
        self.wireframe_checkbox.stateChanged.connect(self.toggle_wireframe_mode)
        layout.addWidget(self.wireframe_checkbox)

        # Creating a slider for wireframe thickness
        wireframe_thickness_label = QLabel("Wireframe Thickness")
        self.wireframe_thickness_slider = QSlider(Qt.Horizontal)
        self.wireframe_thickness_slider.setMinimum(1)
        self.wireframe_thickness_slider.setMaximum(10)  # Adjust max value as needed
        self.wireframe_thickness_slider.setValue(1)  # Default thickness
        self.wireframe_thickness_slider.valueChanged.connect(self.change_wireframe_thickness)
        
        wireframe_thickness_layout = QHBoxLayout()
        wireframe_thickness_layout.addWidget(wireframe_thickness_label)
        wireframe_thickness_layout.addWidget(self.wireframe_thickness_slider)
        layout.addLayout(wireframe_thickness_layout)

        # Ensuring the layout expands from top to bottom
        layout.addStretch()
        controls_widget.setLayout(layout)
        dock.setWidget(controls_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    viewer = SimpleObjViewer()
    viewer.show()
    sys.exit(app.exec_())
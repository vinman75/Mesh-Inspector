# main.py
# Responsible for initializing and running the main application window, managing user interactions, and orchestrating the overall functionality of the 3D viewer.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSlider, QDockWidget, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDoubleSpinBox, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt
from opengl_widget import OpenGLWidget
from apply_dark_theme import apply_dark_theme
from PyQt5.QtGui import QFont,  QIcon


class SimpleObjViewer(QMainWindow):
    def __init__(self):
        super(SimpleObjViewer, self).__init__()
        self.setWindowTitle("Mesh Inspector")
        self.setWindowIcon(QIcon('graphics/icon.png'))  
        self.near_clip = 0.1
        self.far_clip = 100.0
        self.init_gui()
        self.obj_file = None

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.2f}")
        
    
    def change_background_shade(self, value):
        # Convert the slider value to a shade in the range [0, 0.25]
        shade = value * 0.02  # 0.25 / 50
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

    def toggle_hud_visibility(self, state):
        if hasattr(self, 'hud_widget'):
            self.hud_widget.setVisible(state)
            self.hud_visibility_checkbox.setChecked(state)

    def init_gui(self):
        self.opengl_widget = OpenGLWidget(self)
        self.opengl_widget.fps_updated.connect(self.update_fps)
        self.setCentralWidget(self.opengl_widget)
        self.resize(1280, 720)
        self.create_menu_bar()
        self.create_dock_widgets()
        self.init_hud()

    def resizeEvent(self, event):
        super(SimpleObjViewer, self).resizeEvent(event)
        if hasattr(self, 'hud_widget'):
            self.hud_widget.move(0, 0)  # Move it to the top-left corner

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.load_obj)

    def load_obj(self):
        self.obj_file, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj)")
        if self.obj_file:
            self.opengl_widget.load_model(self.obj_file)
            self.update_hud(self.opengl_widget.vertex_count, 
                self.opengl_widget.edge_count, 
                self.opengl_widget.face_count)

    def init_hud(self):
        self.hud_widget = QWidget(self.opengl_widget)
        self.hud_widget.setFixedSize(200, 150)  # Increase the height as needed
        self.hud_widget.move(0, 0)  # Position it on the top-left
        self.hud_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hud_widget.setStyleSheet("background: transparent;")

        self.hud_layout = QVBoxLayout(self.hud_widget)
        self.hud_layout.setAlignment(Qt.AlignTop)

        # Header for Counts
        counts_header = QLabel("Counts")
        counts_header.setFont(QFont("Arial", 10, QFont.Bold))
        counts_header.setStyleSheet("color: yellow;")
        self.hud_layout.addWidget(counts_header)

        self.vertex_count_label = QLabel("Verts: 0")
        self.vertex_count_label.setFont(QFont("Arial", 10))
        self.vertex_count_label.setStyleSheet("color: white;")
        self.hud_layout.addWidget(self.vertex_count_label)

        self.edges_count_label = QLabel("Edges: 0")
        self.edges_count_label.setFont(QFont("Arial", 10))
        self.edges_count_label.setStyleSheet("color: white;")
        self.hud_layout.addWidget(self.edges_count_label)

        self.faces_count_label = QLabel("Faces: 0")
        self.faces_count_label.setFont(QFont("Arial", 10))
        self.faces_count_label.setStyleSheet("color: white;")
        self.hud_layout.addWidget(self.faces_count_label)

        # Separator
        separator = QLabel(" ")
        self.hud_layout.addWidget(separator)

        # Header for Performance
        performance_header = QLabel("Performance")
        performance_header.setFont(QFont("Arial", 10, QFont.Bold))
        performance_header.setStyleSheet("color: yellow;")
        self.hud_layout.addWidget(performance_header)

        # Create the FPS label
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setFont(QFont("Arial", 10))
        self.fps_label.setStyleSheet("color: lightblue;")
        self.hud_layout.addWidget(self.fps_label)

    def update_hud(self, verts, edges, faces):
        self.vertex_count_label.setText(f"Verts: {verts}")
        self.edges_count_label.setText(f"Edges: {edges}")
        self.faces_count_label.setText(f"Faces: {faces}")

    def create_dock_widgets(self):
        # Creating a dock widget
        dock = QDockWidget("Controls", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)

        # Creating a widget to hold controls
        controls_widget = QWidget()
        layout = QVBoxLayout()

        # Viewport Controls
        viewport_group_box = QGroupBox("Viewport Controls")
        viewport_layout = QVBoxLayout()

        bg_label = QLabel("Background Color")
        bg_slider = QSlider(Qt.Horizontal)
        bg_slider.setMinimum(0)
        bg_slider.setMaximum(20)
        bg_slider.setValue(10)
        bg_slider.valueChanged.connect(self.change_background_shade)
        viewport_layout.addWidget(bg_label)
        viewport_layout.addWidget(bg_slider)

        near_clip_label = QLabel("Near Clip Plane")
        near_clip_spinbox = QDoubleSpinBox()
        near_clip_spinbox.setRange(0.01, 10.0)
        near_clip_spinbox.setSingleStep(0.01)
        near_clip_spinbox.setValue(0.1)
        near_clip_spinbox.valueChanged.connect(self.change_near_clip)
        viewport_layout.addWidget(near_clip_label)
        viewport_layout.addWidget(near_clip_spinbox)

        far_clip_label = QLabel("Far Clip Plane")
        far_clip_spinbox = QDoubleSpinBox()
        far_clip_spinbox.setRange(10.0, 1000.0)
        far_clip_spinbox.setSingleStep(1.0)
        far_clip_spinbox.setValue(500.0)
        far_clip_spinbox.valueChanged.connect(self.change_far_clip)
        viewport_layout.addWidget(far_clip_label)
        viewport_layout.addWidget(far_clip_spinbox)

        viewport_group_box.setLayout(viewport_layout)
        layout.addWidget(viewport_group_box)

        # Geometry Controls
        geometry_group_box = QGroupBox("Geometry Controls")
        geometry_layout = QVBoxLayout()

        self.wireframe_checkbox = QCheckBox("Wireframe Mode")
        self.wireframe_checkbox.stateChanged.connect(self.toggle_wireframe_mode)
        geometry_layout.addWidget(self.wireframe_checkbox)

        wireframe_thickness_label = QLabel("Wireframe Thickness")
        self.wireframe_thickness_slider = QSlider(Qt.Horizontal)
        self.wireframe_thickness_slider.setMinimum(1)
        self.wireframe_thickness_slider.setMaximum(10)
        self.wireframe_thickness_slider.setValue(1)
        self.wireframe_thickness_slider.valueChanged.connect(self.change_wireframe_thickness)
        geometry_layout.addWidget(wireframe_thickness_label)
        geometry_layout.addWidget(self.wireframe_thickness_slider)

        geometry_group_box.setLayout(geometry_layout)
        layout.addWidget(geometry_group_box)

        # HUD Control
        hud_group_box = QGroupBox("HUD Control")
        hud_layout = QVBoxLayout()

        self.hud_visibility_checkbox = QCheckBox("Show Poly Count")
        self.hud_visibility_checkbox.setChecked(True)
        self.hud_visibility_checkbox.stateChanged.connect(self.toggle_hud_visibility)
        hud_layout.addWidget(self.hud_visibility_checkbox)

        hud_group_box.setLayout(hud_layout)
        layout.addWidget(hud_group_box)

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
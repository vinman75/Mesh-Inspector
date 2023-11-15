# navigation_controls.py

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

class NavigationHandler:
    def __init__(self, opengl_widget):
        self.opengl_widget = opengl_widget
        self.last_pos = None

    def handle_mouse_press(self, event):
        if event.modifiers() & Qt.AltModifier:
            self.last_pos = event.pos()

    def handle_mouse_move(self, event):
        if self.last_pos and event.modifiers() & Qt.AltModifier:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            if event.buttons() & Qt.LeftButton:
                self.opengl_widget.rotation_x += dy * 0.5
                self.opengl_widget.rotation_y += dx * 0.5
            elif event.buttons() & Qt.MiddleButton:
                self.pan_camera(dx, dy)
            elif event.buttons() & Qt.RightButton:
                self.zoom_camera(dy)

            self.last_pos = event.pos()
            self.opengl_widget.update()

    def handle_wheel_event(self, event):
        zoom_speed = 0.1
        zoom_amount = event.angleDelta().y() / 10.0 * zoom_speed
        if event.modifiers() & Qt.AltModifier:
            self.opengl_widget.camera_pos[2] -= zoom_amount
        else:
            self.opengl_widget.camera_pos[2] -= zoom_amount
        self.opengl_widget.update()

    def handle_key_press(self, event):
        if event.key() == Qt.Key_F:
            print(f"Key pressed: {event.key()}") 
            self.opengl_widget.focus_model()
        elif event.key() == Qt.Key_W:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.wireframe_mode = not self.opengl_widget.wireframe_mode
            self.opengl_widget.parent().wireframe_checkbox.setChecked(self.opengl_widget.wireframe_mode)
            self.opengl_widget.update()
        elif event.key() == Qt.Key_H:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.parent().toggle_hud_visibility(not self.opengl_widget.parent().hud_visibility_checkbox.isChecked())
        elif event.key() == Qt.Key_Left:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.rotation_y -= 5
            self.opengl_widget.update() 
        elif event.key() == Qt.Key_Right:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.rotation_y += 5
            self.opengl_widget.update() 
        elif event.key() == Qt.Key_Up:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.rotation_x -= 5
            self.opengl_widget.update() 
        elif event.key() == Qt.Key_Down:
            print(f"Key pressed: {event.key()}")
            self.opengl_widget.rotation_x += 5
            self.opengl_widget.update() 

        self.opengl_widget.update()

    def pan_camera(self, dx, dy):
        pan_speed = 0.01
        self.opengl_widget.camera_pos[0] -= dx * pan_speed
        self.opengl_widget.camera_pos[1] += dy * pan_speed

    def zoom_camera(self, dy):
        zoom_speed = 0.1
        self.opengl_widget.camera_pos[2] -= dy * zoom_speed

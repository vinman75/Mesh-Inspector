# opengl_widget.py
# Handles the creation and management of the OpenGL widget, including the rendering of 3D models, handling user inputs for camera control, and managing OpenGL 

import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

def check_gl_error():
    err = glGetError()
    if err != GL_NO_ERROR:
        print('GL error: %s' % gluErrorString(err))

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.pan_x = 0
        self.pan_y = 0
        self.vbo = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self.zoom = 1.0
        self.camera_pos = [0.0, 0.0, 5.0]  # Initial camera position [x, y, z]
        self.camera_front = [0.0, 0.0, -1.0]  # The direction that the camera is facing
        self.camera_up = [0.0, 1.0, 0.0]  # The 'up' direction for the camera
        self.bg_color = [0.5, 0.5, 0.5, 1.0]
        self.near_clip = 0.1  # Define the near clip plane distance here
        self.far_clip = 500.0  # Initialize the far clip attribute here
        self.wireframe_mode = False  # Add this line
        self.wireframe_thickness = 1.0  # Default thickness

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glShadeModel(GL_SMOOTH)  # Change to smooth shading
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1, 0])  # Simple directional light

    def set_wireframe_mode(self, enabled):
        self.wireframe_mode = enabled
        self.update()

    def set_wireframe_thickness(self, thickness):
        self.wireframe_thickness = thickness
        self.update()

    def draw_model(self):
        if self.vbo:
            self.vbo.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)

            stride = 6 * np.dtype('float32').itemsize
            glVertexPointer(3, GL_FLOAT, stride, self.vbo)
            glNormalPointer(GL_FLOAT, stride, self.vbo + (3 * np.dtype('float32').itemsize))

            glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) // 6)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
            self.vbo.unbind()   
    
    def set_perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  # Reset the projection matrix
        aspect_ratio = self.width() / self.height() if self.height() > 0 else 1
        gluPerspective(45 / self.zoom, aspect_ratio, self.near_clip, self.far_clip)
        glMatrixMode(GL_MODELVIEW)
        check_gl_error()  # Check for any errors

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        self.set_perspective()

    def change_near_clip(self, value: float):
        self.near_clip = value
        self.set_perspective()
        self.update()

    def change_far_clip(self, value: float):
        self.far_clip = value
        self.set_perspective()
        self.update()

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.AltModifier:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.modifiers() & Qt.AltModifier:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()

            if event.buttons() & Qt.LeftButton:  # Rotate
                self.rotation_x += dy * 0.5
                self.rotation_y += dx * 0.5
            elif event.buttons() & Qt.MiddleButton:  # Pan
                self.pan_camera(dx, dy)
            elif event.buttons() & Qt.RightButton:  # Zoom, with right mouse button
                self.zoom_camera(dy)

            self.last_pos = event.pos()
            self.update()

    def pan_camera(self, dx, dy):
        pan_speed = 0.01  # Adjust this value as needed
        self.camera_pos[0] -= dx * pan_speed
        self.camera_pos[1] += dy * pan_speed

    def zoom_camera(self, dy):
        zoom_speed = 0.1  # Adjust this value as needed
        self.camera_pos[2] -= dy * zoom_speed
        self.update()

    def wheelEvent(self, event):
        zoom_speed = 0.1  # Adjust this value as needed
        # Determine the amount of zoom based on the wheel movement
        zoom_amount = event.angleDelta().y() / 10.0 * zoom_speed
        if event.modifiers() & Qt.AltModifier:  # If Alt key is pressed, adjust the zoom
            self.camera_pos[2] -= zoom_amount
        else:
            # Implement the same functionality as Alt + RMB zoom here if needed
            # For example, you can just replicate the zoom without requiring Alt key
            self.camera_pos[2] -= zoom_amount
        self.update()

    def paintGL(self):
        glClearColor(*self.bg_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = self.width() / self.height() if self.height() > 0 else 1
        gluPerspective(45 / self.zoom, aspect_ratio, self.near_clip, self.far_clip)  # Use the far_clip attribute
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(
            self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
            self.camera_pos[0] + self.camera_front[0],
            self.camera_pos[1] + self.camera_front[1],
            self.camera_pos[2] + self.camera_front[2],
            self.camera_up[0], self.camera_up[1], self.camera_up[2]
        )

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glTranslatef(self.pan_x, self.pan_y, 0)

        if self.vbo:
            self.vbo.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)

            stride = 6 * np.dtype('float32').itemsize
            glVertexPointer(3, GL_FLOAT, stride, self.vbo)
            glNormalPointer(GL_FLOAT, stride, self.vbo + (3 * np.dtype('float32').itemsize))

            glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) // 6)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
            self.vbo.unbind()

        self.draw_model()

        # Draw wireframe over the model if wireframe mode is on
        if self.wireframe_mode:
            
            glLineWidth(self.wireframe_thickness)  # Set wireframe thickness
            glPolygonMode(GL_FRONT, GL_LINE)  
            glDisable(GL_LIGHTING)  # Disable lighting for wireframe
            glColor4f(0.0, 0.0, 0.0, 1.0)  # Set wireframe color, e.g., black
            self.draw_model()
            glEnable(GL_LIGHTING)  # Re-enable lighting
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Restore fill mode

    def focus_model(self):
        if len(self.vertex_coords) == 0:
            return

        min_corner = np.min(self.vertex_coords, axis=0)
        max_corner = np.max(self.vertex_coords, axis=0)
        bounding_box_center = (max_corner + min_corner) / 2
        bounding_box_size = max_corner - min_corner
        self.camera_pos[2] = max(bounding_box_size) * 1.5
        self.camera_pos[0] = bounding_box_center[0]
        self.camera_pos[1] = bounding_box_center[1]
        
        self.update()

    def load_model(self, file_path):
        self.vertex_coords = []
        normal_coords = []
        vertex_data = []
        self.quads = []

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    self.vertex_coords.append([float(val) for val in line.split()[1:4]])
                elif line.startswith('vn '):
                    normal_coords.append([float(val) for val in line.split()[1:4]])

        self.vertex_coords = np.array(self.vertex_coords, dtype=np.float32)
        normal_coords = np.array(normal_coords, dtype=np.float32)

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('f '):
                    vertices = line.split()[1:]
                    face_vertex_indices = [list(map(int, v.split('/'))) for v in vertices]

                    # Check if the face is a quad
                    if len(face_vertex_indices) == 4:
                        # Store quad vertex indices for wireframe rendering
                        quad = [idx[0] - 1 for idx in face_vertex_indices]
                        self.quads.append(quad)

                    # Tessellate quads (and polygons) into triangles
                    for i in range(1, len(face_vertex_indices) - 1):
                        indices = [face_vertex_indices[0], face_vertex_indices[i], face_vertex_indices[i + 1]]
                        
                        for idx in indices:
                            # OBJ format uses 1-based indexing, so we need to subtract 1
                            vertex_index = idx[0] - 1
                            normal_index = idx[2] - 1 if len(idx) > 2 else vertex_index
                            
                            vertex_data.extend(self.vertex_coords[vertex_index])
                            vertex_data.extend(normal_coords[normal_index])

        # Flatten the vertex_data list and create a VBO
        vertex_data = np.array(vertex_data, dtype=np.float32)
        self.vbo = vbo.VBO(vertex_data)
        self.vbo.bind()
        self.focus_model()  # Call the focus_model function to center the model

    def keyPressEvent(self, event):
        self.setFocus()  # Set focus to the widget.

        if event.key() == Qt.Key_F:
            self.focus_model()
        elif event.key() == Qt.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            self.parent().wireframe_checkbox.setChecked(self.wireframe_mode)
            self.update()
        else:
            # Handle other key events
            if event.key() == Qt.Key_Left:
                self.rotation_y -= 5
            elif event.key() == Qt.Key_Right:
                self.rotation_y += 5
            elif event.key() == Qt.Key_Up:
                self.rotation_x -= 5
            elif event.key() == Qt.Key_Down:
                self.rotation_x += 5

        self.update()  # Ensure this is outside the else block
# opengl_widget.py
# Handles the creation and management of the OpenGL widget, including the rendering of 3D models, handling user inputs for camera control, and managing OpenGL 

import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtCore import Qt, pyqtSignal,  QTimer  
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import time



vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.0, 1.0, 1.0, 1.0); // Fragment color
}
"""


def check_gl_error():
    err = glGetError()
    if err != GL_NO_ERROR:
        print('GL error: %s' % gluErrorString(err))

class OpenGLWidget(QOpenGLWidget):
    fps_updated = pyqtSignal(float)  # This will emit the FPS value

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
        self.bg_color = [0.273, 0.273, 0.273, 1.0]
        self.near_clip = 0.1  # Define the near clip plane distance here
        self.far_clip = 500.0  # Initialize the far clip attribute here
        self.wireframe_mode = False  # Add this line
        self.wireframe_thickness = 1.0  # Default thickness
        self.wireframe_vbo_tris = None
        self.wireframe_vbo_quads = None
        self.wireframe_vbo_ngons = None
        format = QSurfaceFormat()
        format.setSamples(4)  # Set the number of samples for multisampling
        self.setFormat(format)  # Apply the format with multisampling
        self.last_frame_time = 0
        self.frame_count = 0
        self.fps = 0.0
        self.redraw_timer = QTimer(self)
        self.redraw_timer.timeout.connect(self.trigger_update)
        self.redraw_timer.start(16)  # about 60 times per second


    def trigger_update(self):
        # Calculate FPS
        current_time = time.time()
        self.frame_count += 1
        time_difference = current_time - self.last_frame_time
        if time_difference >= 1.0:
            self.fps = self.frame_count / time_difference
            self.frame_count = 0
            self.last_frame_time = current_time
            self.fps_updated.emit(self.fps)  # Emit the signal to update the FPS

    def initializeGL(self):
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glShadeModel(GL_SMOOTH)  # Change to smooth shading
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1, 0])  # Simple directional light


        # Shader Program Setup
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)
        # Check for shader compile errors...

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)
        # Check for shader compile errors...

        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, vertex_shader)
        glAttachShader(self.shader_program, fragment_shader)
        glLinkProgram(self.shader_program)
        # Check for linking errors...

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)


    def set_wireframe_mode(self, enabled):
        self.wireframe_mode = enabled
        self.update()

    def create_wireframe_vbo(self, faces):
        wireframe_data = []
        for face in faces:
            for i in range(len(face)):
                start_vertex = self.vertex_coords[face[i]]
                end_vertex = self.vertex_coords[face[(i + 1) % len(face)]]
                wireframe_data.extend(start_vertex)
                wireframe_data.extend(end_vertex)
        return vbo.VBO(np.array(wireframe_data, dtype=np.float32))

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
        gluPerspective(45 / self.zoom, aspect_ratio, self.near_clip, self.far_clip)
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

        # Render the main model
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

        # Draw wireframe over the model if wireframe mode is on
        if self.wireframe_mode:
            glDisable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(self.wireframe_thickness)
            glDepthFunc(GL_LEQUAL)

            # Set wireframe color to black
            glColor3f(0.0, 0.0, 0.0)

            # Check and render wireframe VBOs if they exist
            if self.wireframe_vbo_quads is not None:
                self.wireframe_vbo_quads.bind()
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glDrawArrays(GL_LINES, 0, len(self.wireframe_vbo_quads) // 3)
                glDisableClientState(GL_VERTEX_ARRAY)
                self.wireframe_vbo_quads.unbind()

            if self.wireframe_vbo_tris is not None:
                self.wireframe_vbo_tris.bind()
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glDrawArrays(GL_LINES, 0, len(self.wireframe_vbo_tris) // 3)
                glDisableClientState(GL_VERTEX_ARRAY)
                self.wireframe_vbo_tris.unbind()

            glDepthFunc(GL_LESS)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glEnable(GL_LIGHTING)


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
        self.tris = []
        self.quads = []
        self.ngons = []
        unique_edges = set()

        # First pass to read vertex and normal coordinates
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue  # Skip comments and empty lines

                if line.startswith('v '):
                    self.vertex_coords.append([float(val) for val in line.split()[1:4]])
                elif line.startswith('vn '):
                    normal_coords.append([float(val) for val in line.split()[1:4]])

        self.vertex_coords = np.array(self.vertex_coords, dtype=np.float32)
        normal_coords = np.array(normal_coords, dtype=np.float32)

        # Check if normals are provided, if not generate them
        generate_normals = len(normal_coords) == 0
        if generate_normals:
            normal_coords = np.zeros_like(self.vertex_coords)

        # Second pass to read face data
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue  # Skip comments and empty lines

                if line.startswith('f '):
                    vertices = line.split()[1:]
                    face_vertex_indices = [list(map(int, v.split('/'))) for v in vertices]

                    # Create edges and add to set for uniqueness
                    for i in range(len(face_vertex_indices)):
                        idx1 = face_vertex_indices[i][0] - 1
                        idx2 = face_vertex_indices[(i + 1) % len(face_vertex_indices)][0] - 1
                        edge = tuple(sorted((idx1, idx2)))
                        unique_edges.add(edge)

                    face_indices = [idx[0] - 1 for idx in face_vertex_indices]
                    if len(face_vertex_indices) == 3:  # Triangles
                        self.tris.append(face_indices)
                    elif len(face_vertex_indices) == 4:  # Quads
                        self.quads.append(face_indices)
                    else:  # Ngons (5 or more vertices)
                        self.ngons.append(face_indices)

                    # Generate normals if needed
                    if generate_normals:
                        v0, v1, v2 = [self.vertex_coords[i] for i in face_indices[:3]]
                        face_normal = np.cross(v1 - v0, v2 - v0)
                        face_normal /= np.linalg.norm(face_normal)  # Normalize the normal
                        for i in face_indices:
                            normal_coords[i] += face_normal

                    for i in range(1, len(face_vertex_indices) - 1):
                        indices = [face_vertex_indices[0], face_vertex_indices[i], face_vertex_indices[i + 1]]
                        for idx in indices:
                            vertex_index = idx[0] - 1
                            normal_index = idx[2] - 1 if len(idx) == 3 else vertex_index
                            if vertex_index < len(self.vertex_coords) and (normal_index < len(normal_coords) or generate_normals):
                                vertex_data.extend(self.vertex_coords[vertex_index])
                                vertex_data.extend(normal_coords[normal_index])

        # Normalize the generated normals
        if generate_normals:
            for i in range(len(normal_coords)):
                normal_coords[i] /= np.linalg.norm(normal_coords[i])  # Normalize to length 1
                normal_coords[i] *= 0.3  # Scale to 30% of original length

        vertex_data = np.array(vertex_data, dtype=np.float32)
        self.vbo = vbo.VBO(vertex_data)
        self.vbo.bind()

        # Create VBOs for wireframes after vertices have been parsed
        self.wireframe_vbo_tris = self.create_wireframe_vbo(self.tris)
        self.wireframe_vbo_quads = self.create_wireframe_vbo(self.quads)
        self.wireframe_vbo_ngons = self.create_wireframe_vbo(self.ngons)

        self.vertex_count = len(self.vertex_coords)
        self.edge_count = len(unique_edges)
        self.face_count = len(self.tris) + len(self.quads) + len(self.ngons)

        self.focus_model()

    def keyPressEvent(self, event):
        self.setFocus()  # Set focus to the widget.

        if event.key() == Qt.Key_F:
            self.focus_model()
        elif event.key() == Qt.Key_4 or event.key() == Qt.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            self.parent().wireframe_checkbox.setChecked(self.wireframe_mode)
            self.update()

        elif event.key() == Qt.Key_H:
            # Toggle the HUD visibility and the state of the checkbox in the GUI
            current_state = self.parent().hud_visibility_checkbox.isChecked()
            self.parent().toggle_hud_visibility(not current_state)
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
        
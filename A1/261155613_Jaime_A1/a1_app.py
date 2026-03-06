import numpy as np
from pathlib import Path
import moderngl as mgl
import trimesh
from PyQt5 import QtOpenGL
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QComboBox, QStackedWidget, QVBoxLayout, QPushButton, QSplitter, QLabel, QApplication
import random
from pyglm import glm

from controllers import all_controllers
from stats import Recorder, Record
from helpers import Timer

# geometry and colours for drawing the axis arrows
data = {
    'X': { 'file': 'data/arrow-x.obj', 'colour': np.array((1, 0, 0), dtype='f4') },
    'Y': { 'file': 'data/arrow-y.obj', 'colour': np.array((0, 1, 0), dtype='f4') },
    'Z': { 'file': 'data/arrow-z.obj', 'colour': np.array((0, 0, 1), dtype='f4') }
}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A1 solution")
        self.timer = Timer()
        
        # Init canvases
        self.target = TargetCanvas()
        self.main = MainCanvas(self.target, self.timer)  # give main canvas access to the timer, and target

        # give trackball controller the window so it can query the window size
        all_controllers[-1].window = self.main
        
        control_panel = QVBoxLayout() 
        control_panel.addWidget( self.timer.time_label )
        control_panel.addWidget( self.main.error_label )
        control_panel.addWidget( self.main.count_label)
        start_button = QPushButton("Restart Timer / Skip")
        start_button.pressed.connect(self.start_button)
        control_panel.addWidget(start_button)

        self.combo = QComboBox()
        self.combo.addItems([c.name for c in all_controllers])
        control_panel.addWidget(self.combo)
        self.stack = QStackedWidget()
        for c in all_controllers:               
            self.stack.addWidget(c.makeWidget())
        self.combo.currentIndexChanged.connect(self.on_selection_changed)
        control_panel.addWidget(self.stack)
        control_panel.addStretch()
        control_panel_widget = QWidget()
        control_panel_widget.setLayout(control_panel)   
        
        splitter = QSplitter(Qt.Orientation.Horizontal)        
        splitter.addWidget(self.target)
        splitter.addWidget(self.main)
        splitter.addWidget(control_panel_widget)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
    
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.timer_update)
        self.anim_timer.start(16)
        
    def timer_update(self):
        self.main.update_animation()        
        self.target.update_animation()
        self.timer.getElapsed()

    def on_selection_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        self.main.setController(all_controllers[index])

    def start_button(self):
        self.target.generate_random_rotation()
        self.timer.resetAndStart()


class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        self.ctx = None     # ModernGL context
        self.prog = None    # Hold shaders, buffers, output, etc
        self.vao = {}       # Vertex array
        self.P = None
        self.V = None        
        self.aspect_ratio = 1.0
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)
    
    def update_animation(self):
        self.update()
    
    def initializeGL(self):
        self.ctx = mgl.create_context()
        
        # set up the GLSL programs for drawing
        current_dir = Path(__file__).parent  # glsl folder in same directory as this code
        self.prog = self.ctx.program(
            vertex_shader=open(current_dir / 'glsl/vert.glsl').read(),
            fragment_shader=open(current_dir / 'glsl/frag.glsl').read())
        
        for arrow in data:
            # load geometry from current directory (can also use member resource_dir)
            mesh = trimesh.load_mesh(current_dir / data[arrow]['file'])
        
            # get relevant mesh information
            vertices = mesh.vertices.astype('f4')  # shape: (N, 3)
            indices = mesh.faces.flatten().astype('i4')
            normals = trimesh.geometry.mean_vertex_normals(vertices.shape[0], mesh.faces, mesh.face_normals).astype('f4')
            
            # vertex data buffers
            vbo1 = self.ctx.buffer(vertices.tobytes())
            vbo2 = self.ctx.buffer(normals.tobytes())
            
            # and the index buffer
            ibo = self.ctx.buffer(indices.tobytes())
            self.vao[arrow] = self.ctx.vertex_array(self.prog, [(vbo1, '3f', 'in_position'), (vbo2, '3f', 'in_normal')], index_buffer=ibo)
            
        # set up the camera and projection          
        self.V = glm.lookAt(glm.vec3(0, 0, 8), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        self.P = glm.perspective(glm.radians(25), self.aspect_ratio, 2, 15)
        self.prog['P'].write(self.P)
        self.prog['V'].write(self.V)
    
    def resizeGL(self, w, h):
        self.ctx.viewport = (0, 0, w, h)
        self.aspect_ratio = w / h
        # need to update projection matrix
        self.P = glm.perspective(glm.radians(25), self.aspect_ratio, 2, 15)
        self.prog['P'].write(self.P)
    
    def paintGL(self):
        self.ctx.clear(0, 0, 0)
        self.ctx.enable(mgl.DEPTH_TEST)
        self.setUpRotation()
        for arrow in data:
            self.prog['colour'] = data[arrow]['colour']
            self.vao[arrow].render(mode=mgl.TRIANGLES)

    def setUpRotation(self):
        """ Set up rotation differently depending on canvas"""
        pass


class TargetCanvas(QGLControllerWidget):
    def __init__(self):
        super().__init__()
        label = QLabel("Target Canvas",  parent=self)
        label.setStyleSheet("background-color: white; color: black;")
        self.generate_random_rotation()

    def generate_random_rotation(self):
        q = np.array([random.gauss(0, 1) for i in range(4)])
        self.q = q/np.linalg.norm(q)
        self.matrix = glm.mat4(glm.quat(self.q))

    def setUpRotation(self):
        self.prog['M'].write(self.matrix)  # transpose and flatten to get in Opengl Column-major format


class MainCanvas(QGLControllerWidget):
    def __init__(self, target_canvas: TargetCanvas, timer: Timer):
        super().__init__()
        label = QLabel("Main Canvas",  parent=self)
        label.setStyleSheet("background-color: white; color: black;")
        self.controller = all_controllers[0]
        self.target = target_canvas
        self.matrix = glm.mat4(1)
        self.error = 0
        self.recorder = Recorder()
        self.timer = timer
        self.error_label = QLabel(f"Error: {self.error:.3f} degrees", parent=self)
        self.count_label = QLabel(f"Count: {self.recorder.type_counts[self.controller.name]['count']}", parent=self)

    def setController(self, controller ):
        self.controller = controller
        self.count_label.setText(f"Count: {self.recorder.type_counts[self.controller.name]['count']}")

    def setUpRotation(self):
        matrix = self.controller.get_rotation()
        self.matrix = matrix
        self.prog['M'].write(matrix)
    
    def mousePressEvent(self, event):        
        self.controller.mousePressEvent(event)

    def mouseMoveEvent(self, event):        
        self.controller.mouseMoveEvent(event)

    def evaluate_rotation(self):
        error_matrix = glm.mat3(self.matrix) * glm.transpose(glm.mat3(self.target.matrix))
        rotation_quat = glm.quat_cast(error_matrix)
        self.error = glm.degrees(glm.angle(rotation_quat))
        self.error_label.setText(f"Error: {self.error:.3f} degrees")
        if self.error < 10 and self.timer.running:
            self.timer.stop()
            self.recorder.add(Record(self.controller.name, self.timer.getElapsed(), self.error))
            self.count_label.setText(f"Count: {self.recorder.type_counts[self.controller.name]['count']}")
        
    def update_animation(self):
        super().update_animation()
        self.evaluate_rotation()
    
    def paintGL(self):
        super().paintGL()
        if not self.timer.running:
            self.ctx.clear(0, 0.65, 0)  # green when the error is small enough
            self.ctx.enable(mgl.DEPTH_TEST)
            self.setUpRotation()
            for arrow in data:
                self.prog['colour'] = data[arrow]['colour']
                self.vao[arrow].render(mode=mgl.TRIANGLES)


app = QApplication([])
window = MainWindow()
window.resize(1500, 500)
window.show()
app.exec_()
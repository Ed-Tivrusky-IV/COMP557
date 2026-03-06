import numpy as np
from pathlib import Path
import moderngl as mgl
from PyQt5 import QtCore
from PyQt5 import QtOpenGL, QtWidgets
import time
import trimesh
from PyQt5.QtCore import QTimer

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.gl_widget = QGLControllerWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.gl_widget, stretch=1)        
        self.setLayout(main_layout)
        
class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        self.aspect_ratio = 1.0
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def update_animation(self):
        self.update()

    def initializeGL(self):
        self.ctx = mgl.create_context()

        # set up the GLSL programs for drawing
        current_dir = Path(__file__).parent # glsl folder in same directory as this code
        self.prog = self.ctx.program( 
            vertex_shader = open(current_dir / 'glsl/vert.glsl').read(), 
            fragment_shader = open(current_dir / 'glsl/frag.glsl').read() )

        # load geometry from current directory (can also use member resource_dir)
        mesh = trimesh.load(current_dir / 'data/monkey.obj', force='mesh')
        vertices = mesh.vertices.astype('f4')  # shape: (N, 3)
        vbo = self.ctx.buffer(vertices.tobytes())
        # self.vao = self.ctx.vertex_array(self.prog, vbo, 'in_position' )

        # and the index buffer
        indices = mesh.faces.flatten().astype('i4')
        ibo = self.ctx.buffer(indices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [(vbo, '3f', 'in_position')], index_buffer=ibo)

        # set up the camera and projection               
        self.V = self.create_look_at(eye=(0, 0, 8), target=(0, 0, 0), up=(0, 1, 0))
        self.P = self.create_perspective_projection(25.0, self.aspect_ratio, 2, 15)
        self.prog['P'].write( self.P.T.flatten() )
        self.prog['V'].write( self.V.T.flatten() )

    def create_perspective_projection(self, fovy, aspect, near, far):
        f = 1.0 / np.tan(fovy * np.pi / 180 / 2.0)
        return np.array([[f / aspect, 0, 0, 0],
                         [0, f, 0, 0],
                         [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
                         [0, 0, -1, 0]], dtype='f4')

    def create_look_at(self, eye, target, up):
        eye = np.array(eye, dtype='f4')
        target = np.array(target, dtype='f4')
        up = np.array(up, dtype='f4')
        w = eye - target
        w /= np.linalg.norm(w)
        u = np.cross(up, w)
        u /= np.linalg.norm(u)
        v = np.cross(w, u)
        # return inverse of rigid transformation [ u, v, w, eye ]
        return np.array([[u[0], u[1], u[2], -np.dot(u, eye)],
                         [v[0], v[1], v[2], -np.dot(v, eye)],
                         [w[0], w[1], w[2], -np.dot(w, eye)],
                         [0, 0, 0, 1]], dtype='f4') 

    def resizeGL(self, w, h):
        self.ctx.viewport = (0, 0, w, h)
        self.aspect_ratio = w / h 

    def paintGL(self):
        self.ctx.clear(0,0,0)
        self.ctx.wireframe = True

        t = time.time()

        s = np.sin(t)
        M = np.array(
            [[1,0,0,s], 
             [0,1,0,0], 
             [0,0,1,0], 
             [0,0,0,1]], dtype='f4')    
        c = np.cos(t)
        M2 = np.array(
            [[c,-s,0,0], 
             [s,c,0,0], 
             [0,0,1,0], 
             [0,0,0,1]], dtype='f4')    

        T = M2 @ M  # Use @ to multiply numpy matrices

        self.prog['M'].write( T.T.flatten() ) # transpose and flatten to get in Opengl Column-major format

        self.vao.render(mode=mgl.TRIANGLES)

app = QtWidgets.QApplication([])
window = MainWindow()
window.resize(800, 600)
window.show()
app.exec_()
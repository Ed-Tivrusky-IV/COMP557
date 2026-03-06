import numpy as np
from pathlib import Path
import moderngl as mgl
from PyQt5 import QtOpenGL, QtWidgets

class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)

    def initializeGL(self):
        self.ctx = mgl.create_context()        
        # set up the GLSL programs for drawing
        current_dir = Path(__file__).parent # glsl folder in same directory as this code
        self.prog = self.ctx.program( 
            vertex_shader = open(current_dir / 'glsl/vert.glsl').read(), 
            fragment_shader = open(current_dir / 'glsl/frag.glsl').read() )
        # create per vertex data for 2D triangle with RGB colours at each vertex
        pvd = np.array([
            0.0, 0.8, 1.0, 0.0, 0.0,
            -0.6, -0.8, 0.0, 1.0, 0.0,
            0.6, -0.8, 0.0, 0.0, 1.0,
        ], dtype='f4')
        # create the vertex buffer object
        vbo = self.ctx.buffer(pvd.tobytes())
        # create a vertex array object for the triangle
        self.vao_triangle = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert', 'in_colour')

    def resizeGL(self, w, h):
        self.ctx.viewport = (0, 0, w, h)

    def paintGL(self):
        self.ctx.clear(0,0,0)
        self.vao_triangle.render()
        self.ctx.finish()

app = QtWidgets.QApplication([])
window = QGLControllerWidget()
window.resize(800, 600)
window.show()
app.exec_()

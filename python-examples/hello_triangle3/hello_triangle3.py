import numpy as np
from pathlib import Path
import moderngl as mgl
from PyQt5 import QtCore
from PyQt5 import QtOpenGL, QtWidgets

class SliderControl(QtWidgets.QWidget):
    def __init__(self, label, min_val, max_val, init_val, callback, scale=1.0):
        super().__init__()
        self.callback = callback
        self.scale = scale

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(label)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(int(min_val / scale), int(max_val / scale))
        self.slider.setValue(int(init_val / scale))
        self.slider.valueChanged.connect(self.on_value_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def on_value_changed(self, value):
        scaled_value = value * self.scale
        self.callback(scaled_value)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello Triangle 3")
        self.gl_widget = QGLControllerWidget()

        # Control panel layout (vertical)
        control_panel = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout()
        control_layout.addWidget(SliderControl("Vertex X Position", -1.0, 1.0, 0.0, self.update_vertex_position, scale=0.01))
        control_layout.addWidget(SliderControl("Vertex Red Color", 0.0, 1.0, 1.0, self.update_vertex_color, scale=0.01))
        control_layout.addStretch()  # Push controls to top
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(200)

        # Main layout (horizontal)
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.gl_widget, stretch=1)
        main_layout.addWidget(control_panel)
        self.setLayout(main_layout)

    def update_vertex_position(self, x):
        self.gl_widget.pvd[0, 0] = x
        self.gl_widget.vbo.write(self.gl_widget.pvd.tobytes())
        self.gl_widget.update()

    def update_vertex_color(self, red):
        self.gl_widget.pvd[0, 2] = red
        self.gl_widget.vbo.write(self.gl_widget.pvd.tobytes())
        self.gl_widget.update()

class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(QGLControllerWidget, self).__init__(fmt, None)

    def initializeGL(self):
        self.ctx = mgl.create_context()

        current_dir = Path(__file__).parent # glsl folder in same directory as this code
        self.prog = self.ctx.program( 
            vertex_shader = open(current_dir / 'glsl/vert.glsl').read(), 
            fragment_shader = open(current_dir / 'glsl/frag.glsl').read() )
        # create per vertex data for 2D triangle with RGB colours at each vertex
        self.pvd = np.array([
            [0.0, 0.8, 1.0, 0.0, 0.0],
            [-0.6, -0.8, 0.0, 1.0, 0.0],
            [0.6, -0.8, 0.0, 0.0, 1.0],
        ], dtype='f4')
        # create the vertex buffer object
        self.vbo = self.ctx.buffer(self.pvd.tobytes())
        # create a vertex array object for the triangle
        self.vao_triangle = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert', 'in_colour')

    def paintGL(self):
        self.ctx.clear(1,0,0)
        self.vao_triangle.render()  # TODO: why is this not drawing!!
        self.ctx.finish()

    def resizeGL(self, w, h):
        self.ctx.viewport = (0, 0, w, h)

app = QtWidgets.QApplication([])
window = MainWindow()
window.resize(800, 600)
window.show()
app.exec_()
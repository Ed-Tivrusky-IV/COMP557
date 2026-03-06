import math
from pyglm import glm
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton
from helpers import SliderControl

class Controller:
    def __init__(self):
        self.name = None # this string should be set in the subclass
    
    def makeWidget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()        
        self.get_controls(layout)        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        """ Setup the different control parameters (sliders), adding them to the provided layout."""
        pass
    
    def get_rotation(self) -> glm.mat4:
        """ Get the rotation matrix (4x4) corresponding to the current controller parameters."""
        return glm.mat4(1) # identity matrix by default, but should be overridden in subclass

    def mousePressEvent(self, event):
        """ Handle mouse movement events (for TrackBall and XYBall only)"""
        pass

    def mouseMoveEvent(self, event):
        """ Handle mouse movement events (for TrackBall and XYBall only)"""
        pass

class XYZController(Controller):
    def __init__(self):
        self.name = "XYZ"
        self.x = self.y = self.z = 0
        self.x_slider = None
        self.y_slider = None
        self.z_slider = None

    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        self.x_slider = SliderControl("Rotate X", -180, 180, self.x, lambda x: setattr(self, 'x', x), scale=0.1)
        self.y_slider = SliderControl("Rotate Y", -180, 180, self.y, lambda y: setattr(self, 'y', y), scale=0.1)
        self.z_slider = SliderControl("Rotate Z", -180, 180, self.z, lambda z: setattr(self, 'z', z), scale=0.1)
        layout.addWidget(self.x_slider)
        layout.addWidget(self.y_slider)
        layout.addWidget(self.z_slider)  

        #Add a reset button
        reset_button = QPushButton("Reset")
        def reset(self):
            self.x = self.y = self.z = 0
            self.x_slider.reset_slider()
            self.y_slider.reset_slider()
            self.z_slider.reset_slider()
        reset_button.pressed.connect(lambda: reset(self))
        layout.addWidget(reset_button)

    def get_rotation(self):
        axis_x = glm.vec3(1, 0, 0)
        axis_y = glm.vec3(0, 1, 0)
        axis_z = glm.vec3(0, 0, 1)

        rz = glm.rotate(glm.mat4(1), glm.radians(self.z), axis_z)
        axis_y = glm.vec3(rz * glm.vec4(axis_y, 0))  # rotate y axis by z rotation
        axis_x = glm.vec3(rz * glm.vec4(axis_x, 0))
        ry = glm.rotate(glm.mat4(1), glm.radians(self.y), axis_y)
        axis_x = glm.vec3(ry * glm.vec4(axis_x, 0))  # rotate x axis by y rotation
        rx = glm.rotate(glm.mat4(1), glm.radians(self.x), axis_x)
        return rx * ry * rz
      

class XYXController(Controller):
    def __init__(self):
        self.name = "XYX"
        self.x1 = self.y = self.x2 = 0
        self.x1_slider = None
        self.y_slider = None
        self.x2_slider = None

    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        self.x1_slider = SliderControl("Rotate X1", -180, 180, self.x1, lambda x: setattr(self, 'x1', x), scale=0.1)
        self.y_slider = SliderControl("Rotate Y", -180, 180, self.y, lambda y: setattr(self, 'y', y), scale=0.1)
        self.x2_slider = SliderControl("Rotate X2", -180, 180, self.x2, lambda x: setattr(self, 'x2', x), scale=0.1)
        layout.addWidget(self.x1_slider)
        layout.addWidget(self.y_slider)
        layout.addWidget(self.x2_slider)  

        #Add a reset button
        reset_button = QPushButton("Reset")
        def reset(self):
            self.x1 = self.y = self.x2 = 0
            self.x1_slider.reset_slider()
            self.y_slider.reset_slider()
            self.x2_slider.reset_slider()
        reset_button.pressed.connect(lambda: reset(self))
        layout.addWidget(reset_button)

    def get_rotation(self):
        axis_x = glm.vec3(1, 0, 0)
        axis_y = glm.vec3(0, 1, 0)

        rx1 = glm.rotate(glm.mat4(1), glm.radians(self.x1), axis_x)
        axis_y = glm.vec3(rx1 * glm.vec4(axis_y, 0))  # rotate y axis by x1 rotation
        ry = glm.rotate(glm.mat4(1), glm.radians(self.y), axis_y)
        axis_x = glm.vec3(ry * glm.vec4(axis_x, 0))  # rotate x axis by y rotation
        rx2 = glm.rotate(glm.mat4(1), glm.radians(self.x2), axis_x)
        return rx2 * ry * rx1

    
class WorldLeftController(Controller):
    def __init__(self):
        self.name = "World/Left"
        self.current_total_rotation = glm.mat4(1)
        self.accumulated_rotation = glm.mat4(1)
        self.last_x_value = 0
        self.last_y_value = 0
        self.last_z_value = 0
    
    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        self.x_slider = SliderControl("Rotate X", -180, 180, 0, self.update_x, scale=0.1)
        self.y_slider = SliderControl("Rotate Y", -180, 180, 0, self.update_y, scale=0.1)
        self.z_slider = SliderControl("Rotate Z", -180, 180, 0, self.update_z, scale=0.1)
        layout.addWidget(self.x_slider)
        layout.addWidget(self.y_slider)
        layout.addWidget(self.z_slider)

    def update_x(self, value):
        self.y_slider.reset_slider()
        self.z_slider.reset_slider()
        self.last_y_value = 0
        self.last_z_value = 0
        delta = value - self.last_x_value
        if delta != 0:
            self.accumulated_rotation = glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(1, 0, 0)
            ) * self.accumulated_rotation
            self.current_total_rotation = self.accumulated_rotation
        self.last_x_value = value

    def update_y(self, value):
        self.x_slider.reset_slider()
        self.z_slider.reset_slider()
        self.last_x_value = 0
        self.last_z_value = 0
        delta = value - self.last_y_value
        if delta != 0:
            self.accumulated_rotation = glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(0, 1, 0)
            ) * self.accumulated_rotation
            self.current_total_rotation = self.accumulated_rotation
        self.last_y_value = value

    def update_z(self, value):
        self.x_slider.reset_slider()
        self.y_slider.reset_slider()
        self.last_x_value = 0
        self.last_y_value = 0
        delta = value - self.last_z_value
        if delta != 0:
            self.accumulated_rotation = glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(0, 0, 1)
            ) * self.accumulated_rotation
            self.current_total_rotation = self.accumulated_rotation
        self.last_z_value = value

    def get_rotation(self):
        return self.current_total_rotation

class LocalRightController(Controller):
    def __init__(self):
        self.name = "Local/Right"
        self.current_total_rotation = glm.mat4(1)
        self.accumulated_rotation = glm.mat4(1)
        self.last_x_value = 0
        self.last_y_value = 0
        self.last_z_value = 0
    
    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        self.x_slider = SliderControl("Rotate X", -180, 180, 0, self.update_x, scale=0.1)
        self.y_slider = SliderControl("Rotate Y", -180, 180, 0, self.update_y, scale=0.1)
        self.z_slider = SliderControl("Rotate Z", -180, 180, 0, self.update_z, scale=0.1)
        layout.addWidget(self.x_slider)
        layout.addWidget(self.y_slider)
        layout.addWidget(self.z_slider)

    def update_x(self, value):
        self.y_slider.reset_slider()
        self.z_slider.reset_slider()
        self.last_y_value = 0
        self.last_z_value = 0
        delta = value - self.last_x_value
        if delta != 0:
            self.accumulated_rotation = self.accumulated_rotation * glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(1, 0, 0)
            )
            self.current_total_rotation = self.accumulated_rotation
        self.last_x_value = value

    def update_y(self, value):
        self.x_slider.reset_slider()
        self.z_slider.reset_slider()
        self.last_x_value = 0
        self.last_z_value = 0
        delta = value - self.last_y_value
        if delta != 0:
            self.accumulated_rotation = self.accumulated_rotation * glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(0, 1, 0)
            )
            self.current_total_rotation = self.accumulated_rotation
        self.last_y_value = value

    def update_z(self, value):
        self.x_slider.reset_slider()
        self.y_slider.reset_slider()
        self.last_x_value = 0
        self.last_y_value = 0
        delta = value - self.last_z_value
        if delta != 0:
            self.accumulated_rotation = self.accumulated_rotation * glm.rotate(
                glm.mat4(1),
                glm.radians(delta),
                glm.vec3(0, 0, 1)
            )
            self.current_total_rotation = self.accumulated_rotation
        self.last_z_value = value

    def get_rotation(self):
        return self.current_total_rotation
    

class QuatController(Controller):
    def __init__(self):
        self.name = "Quaternion"
        self.q = glm.quat()
        self.matrix = glm.mat4_cast(self.q)
        
    # TODO: implement get_controls, callbacks, and get_rotation methods for this controller
    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        self.w_slider = SliderControl("Quat W", -1, 1, 1, lambda w: self.update_quat(w, None, None, None), scale=0.01)
        self.x_slider = SliderControl("Quat X", -1, 1, 0, lambda x: self.update_quat(None, x, None, None), scale=0.01)
        self.y_slider = SliderControl("Quat Y", -1, 1, 0, lambda y: self.update_quat(None, None, y, None), scale=0.01)
        self.z_slider = SliderControl("Quat Z", -1, 1, 0, lambda z: self.update_quat(None, None, None, z), scale=0.01)
        layout.addWidget(self.w_slider)
        layout.addWidget(self.x_slider)
        layout.addWidget(self.y_slider)
        layout.addWidget(self.z_slider)

    def update_quat(self, w, x, y, z):
        if w is not None:
            self.q.w = w
        if x is not None:
            self.q.x = x
        if y is not None:
            self.q.y = y
        if z is not None:
            self.q.z = z

        self.q = glm.normalize(self.q)  # Normalize the quaternion to avoid drift

        threshold_up = 1e-1
        threshold_low = 1e-3
        if abs(self.q.w) < threshold_up and abs(self.q.w) > threshold_low: # set the components the same if they are very small
            if abs(self.q.x) < threshold_up and abs(self.q.x) > threshold_low:
                self.q.x = self.q.w
            if abs(self.q.y) < threshold_up and abs(self.q.y) > threshold_low:
                self.q.y = self.q.w
            if abs(self.q.z) < threshold_up and abs(self.q.z) > threshold_low:
                self.q.z = self.q.w
        elif abs(self.q.x) < threshold_up and abs(self.q.x) > threshold_low:
            if abs(self.q.y) < threshold_up and abs(self.q.y) > threshold_low:
                self.q.y = self.q.x
            if abs(self.q.z) < threshold_up and abs(self.q.z) > threshold_low:
                self.q.z = self.q.x
        elif abs(self.q.y) < threshold_up and abs(self.q.y) > threshold_low:
            if abs(self.q.z) < threshold_up and abs(self.q.z) > threshold_low:
                self.q.z = self.q.y

        self.w_slider.setValue(self.q.w)
        self.x_slider.setValue(self.q.x)
        self.y_slider.setValue(self.q.y)
        self.z_slider.setValue(self.q.z)

        self.matrix = glm.mat4_cast(self.q)

    def get_rotation(self):
        return self.matrix

class XYBallController(Controller):
    def __init__(self):
        self.name = "XYBall"
        # The mouse motion in pixels will be multiplied by this value before applying a rotation in radians.
        self.gain = 0.01
        self.last_mouse_pos = None
        self.rotation_matrix = glm.mat4(1)
    
    def get_controls(self, layout: QtWidgets.QVBoxLayout):        
        layout.addWidget(SliderControl("Change Gain", 0.005, 0.1, self.gain, lambda g: setattr(self, 'gain', g), scale=0.001))        

    def mousePressEvent(self, event):
        self.last_mouse_pos = (event.x(), event.y())

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            new_x, new_y = event.x(), event.y()
            delta_x = new_x - self.last_mouse_pos[0]
            delta_y = new_y - self.last_mouse_pos[1]
           
            if delta_x != 0:
                self.rotation_matrix = glm.rotate(
                    glm.mat4(1),
                    self.gain * delta_x,
                    glm.vec3(0, 1, 0)
                ) * self.rotation_matrix
            if delta_y != 0:
                self.rotation_matrix = glm.rotate(
                    glm.mat4(1),
                    self.gain * delta_y,
                    glm.vec3(1, 0, 0)
                ) * self.rotation_matrix

            self.last_mouse_pos = (new_x, new_y)

    def get_rotation(self):
        return self.rotation_matrix


class TrackBallController(Controller):
    def __init__(self, window=None):
        self.name = "TrackBall"
        # The fit parameter describes how big the ball is relative to
        # the smallest screen dimension. With a square window and fit of 2,
        # the ball will fit just touch the edges of the screen.
        # Values less than 2 will give a ball larger than the window
        # while smaller values will give a ball contained entirely inside.
        self.gain = 1.2
        self.fit = 2.0
        self.window = window
        self.last_mouse_pos = None
        self.rotation_matrix = glm.mat4(1)
        self.rotation_quat = glm.quat()  # Identity quaternion
    
    def get_controls(self, layout: QtWidgets.QVBoxLayout):
        layout.addWidget(SliderControl("Change Gain", 0.1, 5, self.gain, lambda g: setattr(self, 'gain', g), scale=0.1))
        layout.addWidget(SliderControl("Change Fit", 0.1, 5, self.fit, lambda f: setattr(self, 'fit', f), scale=0.1))
        
    def mousePressEvent(self, event):
        self.last_mouse_pos = (event.x(), event.y())

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            new_x, new_y = event.x(), event.y()

            last_sphere_pos = self.get_sphere_coordinates(self.last_mouse_pos[0], self.last_mouse_pos[1])
            new_sphere_pos = self.get_sphere_coordinates(new_x, new_y)

            # Continue only if the mouse has moved
            if last_sphere_pos != new_sphere_pos:
                # Use glm.dot to compute the angle
                dot_product = glm.dot(last_sphere_pos, new_sphere_pos)
                angle = glm.acos(glm.clamp(dot_product, -1.0, 1.0))
                
                if angle != 0:
                    axis = glm.normalize(glm.cross(last_sphere_pos, new_sphere_pos))
                    step_rotation = glm.angleAxis(self.gain * angle, axis)
                    self.rotation_quat = step_rotation * self.rotation_quat
            
            self.rotation_matrix = glm.mat4_cast(self.rotation_quat)
            # I think using glm.rotate repeatedly will accumulate numerical errors
            # and the rotation matrix will no longer be orthogonal after some time. That's what GPT recommended.
            # So I convert the quaternion to a rotation matrix directly instead of using glm.rotate here.
            self.last_mouse_pos = (new_x, new_y)
            
    def get_sphere_coordinates(self, x, y):  # x and y being mouse coords
        # get window size
        width = self.window.ctx.viewport[2]
        height = self.window.ctx.viewport[3]

        radius = min(width, height) / self.fit
        x_normalized = (2 * x - width) / radius
        y_normalized = (height - 2 * y) / radius # Invert y axis for screen coordinates

        length_squared = x_normalized**2 + y_normalized**2
        if length_squared <= 1.0:
            z = math.sqrt(1.0 - length_squared)
            return glm.vec3(x_normalized, y_normalized, z)
        else:
            length = math.sqrt(length_squared)
            x_normalized /= length
            y_normalized /= length
            return glm.vec3(x_normalized, y_normalized, 0.0)
       
    def get_rotation(self):
        return self.rotation_matrix

all_controllers = [
    XYZController(), 
    XYXController(),
    WorldLeftController(), 
    LocalRightController(),
    XYBallController(), 
    QuatController(),
    TrackBallController()
]        
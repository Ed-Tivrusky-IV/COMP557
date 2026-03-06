import time
from PyQt5 import QtWidgets, QtCore

class Timer:
    def __init__(self):
        self.elapsed = 0
        self.running = False
        self.start_time = 0
        self.time_label = QtWidgets.QLabel("Timer: 0.000 s")
        self.start()
    
    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter()

    def stop(self):
        if self.running:
            self.elapsed = time.perf_counter() - self.start_time
            self.running = False
            
    def reset(self):
        self.elapsed = 0
        if self.running:
            self.start_time = time.perf_counter()

    def resetAndStart(self):
        self.reset()
        self.start()
        
    def getElapsed(self):
        if self.running:
            self.elapsed = time.perf_counter() - self.start_time
        self.time_label.setText(f"Timer: {self.elapsed:.3f} s")
        return self.elapsed


class SliderControl(QtWidgets.QWidget):
    """Wrapper for creating sliders in UI."""
    
    def __init__(self, label, min_val, max_val, init_val, callback1, scale=1.0):
        super().__init__()
        self.callback_val_update = callback1
        self.scale = scale
        self.value = init_val
        
        layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(label)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(int(min_val / scale), int(max_val / scale))
        self.slider.setValue(int(init_val / scale))
        self.slider.valueChanged.connect(self.on_value_changed)
        self.value_label = QtWidgets.QLabel(f"{init_val:.2f}")
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

        self.setLayout(layout)
    
    def getValue(self):
        return self.value
    
    def setValue(self, val):
        self.slider.blockSignals(True)
        self.slider.setValue(int(val / self.scale))
        self.value_label.setText(f"{val:.2f}")
        self.slider.blockSignals(False)

    def on_value_changed(self, value_scaled):
        self.value = value_scaled * self.scale
        self.value_label.setText(f"{self.value:.2f}")
        self.callback_val_update(self.value)

    #Add a reset function to reset the slider to 0, although I found that using setValue(0) directly is fine
    def reset_slider(self):
        self.setValue(0)


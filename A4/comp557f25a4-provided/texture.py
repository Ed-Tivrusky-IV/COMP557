import taichi as ti
import taichi.math as tm
import numpy as np

# Sorry I don't have the time to implement texture sampling in the given time frame.
texture_width = 1024
texture_height = 1024
textures_data = ti.Vector.field(3, dtype=ti.f32, shape=(10, texture_width * texture_height)) # support up to 10 textures
image_np = np.zeros((texture_height, texture_width, 3), dtype=np.float32)

@ti.kernel
def load_texture(texture_id: int, image: ti.types.ndarray()):
    for i, j in ti.ndrange(image.shape[0], image.shape[1]):
        textures_data[texture_id, i * image.shape[1] + j] = tm.vec3(image[i, j, 0], image[i, j, 1], image[i, j, 2])
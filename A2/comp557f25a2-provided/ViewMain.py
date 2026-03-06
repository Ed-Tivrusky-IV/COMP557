import moderngl as mgl
from pyglm import glm
from Scene import Scene, Camera

class ViewMain():
	def __init__(self, scene: Scene, camera: Camera, ctx: mgl.Context):
		self.scene = scene
		self.camera = camera
		self.ctx = ctx

	def paintGL(self, aspect_ratio: float):
		self.ctx.clear(0,0,0)
		self.ctx.enable(mgl.DEPTH_TEST)
		
		# set up projection and view matrix for the main camera vew
		fov = glm.radians(self.scene.controls.main_view_fov)
		self.camera.V = glm.translate(glm.mat4(1), glm.vec3(0, 0, -self.camera.distance)) * self.camera.R
		n,f = self.scene.compute_nf_from_view(self.camera.V)		
		self.camera.P = glm.perspective(fov, aspect_ratio, n, f)

		cam_mvp = self.camera.P * self.camera.V 
		cam_mv = self.camera.V 

		self.scene.prog_shadow_map['u_mv'].write(cam_mv)
		self.scene.prog_shadow_map['u_mvp'].write(cam_mvp)
		light_pos = self.scene.get_light_pos_in_view( self.camera.V )		 
		self.scene.prog_shadow_map['u_light_pos'].write(light_pos)
		self.scene.prog_shadow_map['u_use_lighting'] = True		
		self.scene.render_for_view()

		if self.scene.controls.cheap_shadows:

			ground_plane_in_world_coords = self.scene.get_ground_plane()
			light_pos_in_world_coords = self.scene.get_light_pos_in_world()

			n = glm.vec3(ground_plane_in_world_coords)
			n = glm.normalize(n)
			light_to_world_w = n
			# I found that w is actually the (0,1,0) vector for the ground plane
			# this is definitely a special case for a horizontal ground plane
			# otherwise, I should construct u and v using cross products from w
			d = glm.dot( glm.vec3(ground_plane_in_world_coords), glm.vec3(light_pos_in_world_coords) ) + ground_plane_in_world_coords.w

			light_to_world = glm.mat4((1,0,0,0),(0,0,-1,0),(light_to_world_w.x, light_to_world_w.y, light_to_world_w.z,0),(light_pos_in_world_coords.x, light_pos_in_world_coords.y, light_pos_in_world_coords.z,1))
			shadow_projection = glm.mat4((d,0,0,0), (0,d,0,0), (0,0,d-1e-4,-1),(0,0,0,0))
			world_to_light = glm.inverse(light_to_world)
			cheap_shadow_modelling_transformation = light_to_world * shadow_projection * world_to_light

			cam_mvp = self.camera.P * self.camera.V * cheap_shadow_modelling_transformation
			self.scene.prog_shadow_map['u_mvp'].write(cam_mvp)
			self.scene.prog_shadow_map['u_use_lighting'] = False
			self.scene.prog_shadow_map['u_use_shadow_map'] = False
			self.scene.render_cheap_shadows()
			self.scene.prog_shadow_map['u_use_lighting'] = True
			self.scene.prog_shadow_map['u_use_shadow_map'] = self.scene.controls.use_shadow_map

	  
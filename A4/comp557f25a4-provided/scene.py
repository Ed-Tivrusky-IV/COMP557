import geometry as geom
from helperclasses import Ray, Intersection, getRayDistance
from camera import Camera

import numpy as np

import taichi as ti
import taichi.math as tm

shadow_epsilon = 10**(-2)

@ti.data_oriented
class Scene:
    def __init__(self,
                 jitter: bool,
                 samples: int,
                 camera: Camera,
                 ambient: tm.vec3,
                 lights: ti.template(),
                 nb_lights: int,
                 spheres: ti.template(),
                 nb_spheres: int,
                 cylinders: ti.template(),
                 nb_cylinders: int,
                 planes: ti.template(),
                 nb_planes: int,
                 rings: ti.template(),
                 nb_rings: int,
                 aaboxes: ti.template(),
                 nb_aaboxes: int,
                 meshes: ti.template(),
                 nb_meshes: int,
                 meshes_verts: np.array,
                 meshes_faces: np.array,
                 ):
        self.jitter = jitter  # should rays be jittered
        self.samples = samples  # number of rays per pixel
        self.camera = camera
        self.ambient = ambient  # ambient lighting
        self.lights = lights  # all lights in the scene
        self.nb_lights = nb_lights
        self.spheres = spheres
        self.cylinders = cylinders
        self.planes = planes
        self.rings = rings
        self.aaboxes = aaboxes
        self.meshes = meshes
        self.nb_spheres = nb_spheres
        self.nb_cylinders = nb_cylinders
        self.nb_planes = nb_planes
        self.nb_rings = nb_rings
        self.nb_aaboxes = nb_aaboxes
        self.nb_meshes = nb_meshes

        self.meshes_verts = ti.Vector.field(3, shape=(max(1, meshes_verts.shape[0])), dtype=float)
        self.meshes_verts.from_numpy(meshes_verts)
        self.meshes_faces = ti.Vector.field(3, shape=(max(1, meshes_faces.shape[0])), dtype=int)
        self.meshes_faces.from_numpy(meshes_faces)

        self.image = ti.Vector.field( n=3, dtype=float, shape=(self.camera.width, self.camera.height) )

        self.offsets = ti.field(dtype=ti.f32, shape=((self.samples - 1) * (self.samples - 1) + 1, 2))


    @ti.kernel
    def render( self, iteration_count: int ):
        for x,y in ti.ndrange(self.camera.width, self.camera.height):
            if (y == x) and x%10 == 0: print(".",end='')
            ray = self.camera.create_ray( x, y, self.jitter )
            intersect = self.intersect_scene(ray, 0, float('inf'))
            sample_colour = tm.vec3(0, 0, 0) # background colour
            if intersect.is_hit:
                sample_colour = self.compute_shading(intersect, ray)
            self.image[x,y] += (sample_colour - self.image[x,y]) / iteration_count
        print() # end of line after one dot per 10 rows


    @ti.func
    def intersect_scene(self, ray: Ray, t_min: float, t_max: float) -> Intersection:
        best = Intersection() # default is no intersection (is_hit = False)        
        ti.loop_config(serialize=True) 
        for i in range(self.nb_spheres):
            hit = geom.intersectSphere(self.spheres[i], ray, t_min, t_max )
            if hit.is_hit: best = hit; t_max = hit.t # keep best hit only
        ti.loop_config(serialize=True) 
        for i in range(self.nb_cylinders):
            hit = geom.intersectCylinder(self.cylinders[i], ray, t_min, t_max )
            if hit.is_hit: best = hit; t_max = hit.t
        ti.loop_config(serialize=True) 
        for i in range(self.nb_planes):
            hit = geom.intersectPlane(self.planes[i], ray, t_min, t_max )
            if hit.is_hit: best = hit; t_max = hit.t
        ti.loop_config(serialize=True) 
        for i in range(self.nb_rings):
            hit = geom.intersectRing(self.rings[i], ray, t_min, t_max )
            if hit.is_hit: best = hit; t_max = hit.t                
        ti.loop_config(serialize=True) 
        for i in range(self.nb_aaboxes):
            hit = geom.intersectAABox(self.aaboxes[i], ray, t_min, t_max )
            if hit.is_hit: best = hit; t_max = hit.t
        ti.loop_config(serialize=True) 
        for i in range(self.nb_meshes):
            hit = geom.intersectMesh(self.meshes[i], self.meshes_verts, self.meshes_faces, ray, t_min, t_max)
            if hit.is_hit: best = hit; t_max = hit.t
        
        return best


    @ti.func
    def compute_shading(self, intersect: Intersection, ray: Ray) -> tm.vec3:
        sample_colour = tm.vec3(0, 0, 0)

        # Ambient shading
        sample_colour += self.ambient * intersect.mat.diffuse

        ti.loop_config(serialize=True) 
        for l in range(self.nb_lights):
            # TODO: Objective 3: Implement diffuse and specular shading
            light = self.lights[l]
            shadow_ray_origin = intersect.position + intersect.normal * shadow_epsilon
            shadow_ray = Ray( shadow_ray_origin, tm.normalize( light.vector - intersect.position ) if light.ltype == 1 else -light.vector )
            shadow_intersect = self.intersect_scene( shadow_ray, 0, float('inf') )
            if shadow_intersect.is_hit == False or ( light.ltype == 1 and getRayDistance( shadow_ray, shadow_intersect.position ) > getRayDistance( shadow_ray, light.vector ) ):
                view_vec = -1 * ray.direction
                light_vec = tm.normalize(light.vector) if light.ltype == 0 else tm.normalize(light.vector - intersect.position)
                half_vec = tm.normalize(light_vec + view_vec)

                light_distance = tm.length(light.vector - intersect.position)
                light_intensity = light.colour * (1.0 / (light.attenuation.x + light.attenuation.y * light_distance + light.attenuation.z * light_distance * light_distance))
                light_specular = intersect.mat.specular * light_intensity * (tm.pow( tm.max( tm.dot( half_vec, intersect.normal ), 0.0 ), intersect.mat.shininess ))
                if intersect.mat.mirror:
                    mirror_ray_dir = tm.normalize( ray.direction - 2 * tm.dot( ray.direction, intersect.normal ) * intersect.normal )
                    mirror_ray_origin = intersect.position + mirror_ray_dir * shadow_epsilon
                    mirror_ray = Ray( mirror_ray_origin, mirror_ray_dir )
                    mirror_intersect = self.intersect_scene( mirror_ray, 0, float('inf') )
                    if mirror_intersect.is_hit:
                        light_specular = intersect.mat.specular * (mirror_intersect.mat.diffuse * light_intensity * tm.max( tm.dot( light_vec, mirror_intersect.normal ), 0.0 ) 
                                        + mirror_intersect.mat.specular * light_intensity * (tm.pow( tm.max( tm.dot( tm.normalize( light_vec + (-1 * mirror_ray.direction) ), mirror_intersect.normal ), 0.0 ), mirror_intersect.mat.shininess )))
                light_diffuse = intersect.mat.diffuse * light_intensity * tm.max( tm.dot( light_vec, intersect.normal ), 0.0 )
                sample_colour += light_diffuse + light_specular


            
            # TODO: Objective 6: Implement shadow rays

        return sample_colour
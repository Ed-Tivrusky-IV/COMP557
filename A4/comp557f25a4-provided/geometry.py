from helperclasses import Ray, Intersection, Material, changeRayFrame, getRayPoint, changeIntersectFrame, find_texture_colour

import taichi as ti
import taichi.math as tm

EPSILON = 10 ** (-5)

@ti.dataclass
class Sphere:
    id: int
    material: Material
    texture_id: int
    radius: float
    M: tm.mat4
    M_inv: tm.mat4

@ti.func
def intersectSphere(sphere: Sphere, ray: Ray, t_min: float, t_max: float) -> Intersection:
    ''' Ray-sphere intersection  
    Args:
        sphere (Sphere): sphere to intersect with
        ray (Ray): ray in world space
        t_min (float): minimum t value for valid intersection
        t_max (float): maximum t value for valid intersection
    Returns:
        Intersection: intersection data (is_hit, t, normal, point, material)
        
        Note, nominally the intersection will be computed with the sphere
        at the origin with the specified radius.  For a sphere away from 
        the origin, the M and M_inv members of the Sphere class must be used to 
        transform the ray into the sphere's local frame for intersection, and
        likewise used to transform the resulting intersection data back to world space
        (TODO: See Objective ?).
    '''
    ray_local = changeRayFrame(ray, sphere.M_inv)
    p = ray_local.origin
    d = ray_local.direction
    delta = (tm.dot(p, d))**2 - (tm.dot(p, p) - sphere.radius**2) * (tm.dot(d, d))
    hit = Intersection() # default is no intersection (is_hit = False)
    if abs(delta) < EPSILON:
        t_hit = -tm.dot(p, d) / tm.dot(d, d)
        if t_max >= t_hit >= t_min and t_hit > 0:
            hit_point_local = getRayPoint(ray_local, t_hit)
            normal_local = tm.normalize(hit_point_local)
            if sphere.texture_id != -1:
                u = 0.5 + (tm.atan2(normal_local.z, normal_local.x) / (2 * tm.pi))
                v = 0.5 - (tm.asin(normal_local.y) / tm.pi)
                sphere.material.diffuse = find_texture_colour(sphere.texture_id, u, v)
            hit = Intersection( True, t_hit, normal_local, hit_point_local, sphere.material )
            hit = changeIntersectFrame(hit, sphere.M, sphere.M_inv)
    elif delta > EPSILON:
        sqrt_delta = tm.sqrt(delta)
        t1 = (-tm.dot(p, d) - sqrt_delta) / tm.dot(d, d)
        t2 = (-tm.dot(p, d) + sqrt_delta) / tm.dot(d, d)
        t_hit = t1 if t_max >= t1 >= t_min and t1 > 0 else (t2 if t_max >= t2 >= t_min and t2 > 0 else -1)
        if t_hit != -1: 
            hit_point_local = getRayPoint(ray_local, t_hit)
            normal_local = tm.normalize(hit_point_local)
            if sphere.texture_id != -1:
                u = 0.5 + (tm.atan2(normal_local.z, normal_local.x) / (2 * tm.pi))
                v = 0.5 - (tm.asin(normal_local.y) / tm.pi)
                sphere.material.diffuse = find_texture_colour(sphere.texture_id, u, v)
            hit = Intersection( True, t_hit, normal_local, hit_point_local, sphere.material )
            hit = changeIntersectFrame(hit, sphere.M, sphere.M_inv)
        
    return hit
    # TODO: Objective 2: Implement ray-sphere intersection


@ti.dataclass
class Plane:
    id: int
    two_materials: bool     # true if plane uses two materials for a checkerboard pattern
    material1: Material
    material2: Material
    normal: tm.vec3         # only plane normal (goes through origin in local space)
    M: tm.mat4              # transformation matrix to world space  
    M_inv: tm.mat4          # inverse transformation matrix to local space  

@ti.func
def intersectPlane(plane: Plane, ray: Ray, t_min: float, t_max: float) -> Intersection:
    ''' Ray-plane intersection
    Args:
        plane (Plane): plane to intersect with
        ray (Ray): ray in world space
        t_min (float): minimum t value for valid intersection
        t_max (float): maximum t value for valid intersection
    Returns:
        Intersection: intersection data (is_hit, t, normal, point, material)
        
        Note, nominally the intersection will be computed with the plane
        at the origin with the specified normal.  For a plane away from 
        the origin, the M and M_inv members of the Plane class must be used to 
        transform the ray into the plane's local frame for intersection, and
        likewise used to transform the resulting intersection data back to world space.

        Note, the plane can have two materials (when two_materials is true) which
        are applied in a checkerboard pattern in the plane's local XZ plane.
    '''

    hit = Intersection() # default is no intersection (is_hit = False)

    # TODO: Objective 5: Implement ray-plane intersection
    ray_local = changeRayFrame(ray, plane.M_inv)
    o = ray_local.origin
    d = ray_local.direction
    denom = tm.dot(plane.normal, d)
    if abs(denom) > EPSILON:
        t_hit = -tm.dot(plane.normal, o) / denom
        if t_max >= t_hit >= t_min and t_hit > 0:
            hit_point_local = getRayPoint(ray_local, t_hit)
            normal_local = plane.normal
            material = plane.material1
            if plane.two_materials:
                checker_x = int(tm.floor(hit_point_local.x))
                checker_z = int(tm.floor(hit_point_local.z))
                if (checker_x + checker_z) % 2 == 0:
                    material = plane.material1
                else:
                    material = plane.material2

            hit = Intersection( True, t_hit, normal_local, hit_point_local, material )
            hit = changeIntersectFrame(hit, plane.M, plane.M_inv)


    return hit

@ti.dataclass
class Ring:
    id: int
    material: Material
    inner_radius: float
    outer_radius: float
    normal: tm.vec3         # only ring normal (goes through origin in local space)
    M: tm.mat4              # transformation matrix to world space  
    M_inv: tm.mat4          # inverse transformation matrix to local space
@ti.func
def intersectRing(ring: Ring, ray: Ray, t_min: float, t_max : float) -> Intersection:
    hit = Intersection() # default is no intersection (is_hit = False)

    ray_local = changeRayFrame(ray, ring.M_inv)
    o = ray_local.origin
    d = ray_local.direction
    denom = tm.dot(ring.normal, d)
    if abs(denom) > EPSILON:
        t_hit = -tm.dot(ring.normal, o) / denom
        if t_max >= t_hit >= t_min and t_hit > 0:
            hit_point_local = getRayPoint(ray_local, t_hit)
            dist2 = hit_point_local.x * hit_point_local.x + hit_point_local.z * hit_point_local.z
            if ring.inner_radius * ring.inner_radius <= dist2 <= ring.outer_radius * ring.outer_radius:
                normal_local = tm.normalize(ring.normal)
                hit = Intersection( True, t_hit, normal_local, hit_point_local, ring.material )
                hit = changeIntersectFrame(hit, ring.M, ring.M_inv)

    return hit


@ti.dataclass
class AABox:
    id: int
    material: Material
    minpos: tm.vec3     # lower left corner
    maxpos: tm.vec3     # upper right corner
    M: tm.mat4
    M_inv: tm.mat4

@ti.func
def intersectAABox(aabox: AABox, ray: Ray, t_min: float, t_max: float) -> Intersection:
    hit = Intersection() # default is no intersection (is_hit = False)

    # TODO: Objective 7: Implement ray-box intersection
    ray_local = changeRayFrame(ray, aabox.M_inv)
    o = ray_local.origin
    d = ray_local.direction
    t1 = (aabox.minpos - o) / d #element-wise division
    t2 = (aabox.maxpos - o) / d
    tmin = tm.max( tm.max( tm.min(t1.x, t2.x), tm.min(t1.y, t2.y) ), tm.min(t1.z, t2.z) )
    tmax = tm.min( tm.min( tm.max(t1.x, t2.x), tm.max(t1.y, t2.y) ), tm.max(t1.z, t2.z) )
    if tmax >= tmin and tmax >= 0:
        t_hit = tmin if tmin >= 0 else tmax
        if t_max >= t_hit >= t_min and t_hit > 0:
            hit_point_local = getRayPoint(ray_local, t_hit)
            # Determine normal
            normal_local = tm.vec3(0.0, 0.0, 0.0)
            for i in range(3):
                if abs(hit_point_local[i] - aabox.minpos[i]) < EPSILON:
                    normal_local = tm.vec3(0.0, 0.0, 0.0)
                    normal_local[i] = -1.0
                    break
                elif abs(hit_point_local[i] - aabox.maxpos[i]) < EPSILON:
                    normal_local = tm.vec3(0.0, 0.0, 0.0)
                    normal_local[i] = 1.0
                    break

            hit = Intersection( True, t_hit, normal_local, hit_point_local, aabox.material )
            hit = changeIntersectFrame(hit, aabox.M, aabox.M_inv)


    return hit


@ti.dataclass
class Mesh:
    id: int
    material: Material
    faces_ids_start: ti.i32  # index of the first face in the global face array
    faces_ids_count: ti.i32  # number of faces in this mesh
    M: tm.mat4
    M_inv: tm.mat4

@ti.func
def intersectMesh(mesh: Mesh,                  # data for this mesh (start face and number of faces, etc.)
                  meshes_verts: ti.template(), # all vertices (for all meshes)
                  meshes_faces: ti.template(), # all faces (for all meshes)
                  ray: Ray,
                  t_min: float,
                  t_max: float
) -> Intersection:
    
    out_intersect = Intersection() # default is no intersection (is_hit = False)

    # TODO: Objective 8: Implement ray-mesh intersection
    ray_local = changeRayFrame(ray, mesh.M_inv)
    o = ray_local.origin
    d = ray_local.direction
    for i in range(mesh.faces_ids_start, mesh.faces_ids_start + mesh.faces_ids_count):
        face = meshes_faces[i]
        v0 = meshes_verts[face.x]
        v1 = meshes_verts[face.y]
        v2 = meshes_verts[face.z]

        edge1 = v1 - v0
        edge2 = v2 - v0
        h = tm.cross(d, edge2)
        a = tm.dot(edge1, h)
        edge_test = tm.dot(tm.cross(edge1, edge2), d)
        if abs(a) > EPSILON and edge_test < - EPSILON:
            f = 1.0 / a
            s = o - v0
            u = f * tm.dot(s, h)
            if 0.0 <= u <= 1.0:
                q = tm.cross(s, edge1)
                v = f * tm.dot(d, q)
                if 0.0 <= v <= 1.0 and u + v <= 1.0:
                    t_hit = f * tm.dot(edge2, q)
                    if t_max >= t_hit >= t_min and t_hit > 0:
                        hit_point_local = getRayPoint(ray_local, t_hit)
                        normal_local = tm.normalize(tm.cross(edge1, edge2))
                        intersect = Intersection( True, t_hit, normal_local, hit_point_local, mesh.material )
                        intersect = changeIntersectFrame(intersect, mesh.M, mesh.M_inv)
                        if not out_intersect.is_hit or intersect.t < out_intersect.t:
                            out_intersect = intersect


    return out_intersect

@ti.dataclass
class Cylinder:
    id: int
    material: Material
    radius: float
    height: float
    M: tm.mat4
    M_inv: tm.mat4

@ti.func
def intersectCylinder(cylinder: Cylinder, ray: Ray, t_min: float, t_max: float) -> Intersection:
    hit = Intersection()  # default no hit

    ray_local = changeRayFrame(ray, cylinder.M_inv)
    o = ray_local.origin
    d = ray_local.direction

    a = d.x * d.x + d.z * d.z
    b = 2.0 * (o.x * d.x + o.z * d.z)
    c = o.x * o.x + o.z * o.z - cylinder.radius * cylinder.radius

    delta = b * b - 4.0 * a * c

    if delta >= 0.0:
        sqrt_delta = tm.sqrt(delta)
        t1 = (-b - sqrt_delta) / (2 * a)
        t2 = (-b + sqrt_delta) / (2 * a)

        # check each root explicitly (Taichi-safe)
        # -------------------------------
        # First try t1
        if t_min <= t1 <= t_max and t1 > 0:
            p1 = getRayPoint(ray_local, t1)
            if 0.0 <= p1.y <= cylinder.height:        # within cylinder height?
                n1 = tm.normalize(tm.vec3(p1.x, 0.0, p1.z))
                hit_local = Intersection(True, t1, n1, p1, cylinder.material)
                hit = changeIntersectFrame(hit_local, cylinder.M, cylinder.M_inv)

        # Then try t2
        elif t_min <= t2 <= t_max and t2 > 0:
            p2 = getRayPoint(ray_local, t2)
            if 0.0 <= p2.y <= cylinder.height:
                n2 = tm.normalize(tm.vec3(p2.x, 0.0, p2.z))
                hit_local = Intersection(True, t2, n2, p2, cylinder.material)
                hit = changeIntersectFrame(hit_local, cylinder.M, cylinder.M_inv)

    return hit


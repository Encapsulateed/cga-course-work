from numba import cuda
from math import sqrt
from .common import *
from scene.scene import *



@cuda.jit(device=True)
def intersect_ray_parabaloid(ray_origin: tuple, ray_dir: tuple, parabaloid_origin: tuple, a: float, b: float, p_orient: float,h:float):
    k = (b/a)**2
    e = (a/b)**2
    
    
    rx = ray_origin[0]
    ry = ray_origin[1]
    rz = ray_origin[2]
    
    x = ray_dir[0]
    y = ray_dir[1]
    z = ray_dir[2]
    
    xc = parabaloid_origin[0]
    yc = parabaloid_origin[1]
    zc = parabaloid_origin[2]
    
    REVERS = p_orient
    
    a = k*x**2 + e*y**2
    
    b = 2*k * (rx * x - x*xc) + 2*e * (ry*y - y*yc) - z * REVERS
    
    c = k *(rx**2 +xc**2 -2 * rx*xc) + e* (ry**2 +yc**2 -2 * ry*yc) -REVERS*(rz -zc)

    discriminant = b * b - 4 * a * c

    if discriminant < 0.0:
        return -999.9
    else:
        numerator = -b - sqrt(discriminant)

        if numerator > 0.0:
            t = numerator / (2*a)
            z = ray_origin[2] + t*ray_dir[2]
            
            less_than_h = z <= h
            if p_orient == -1:
                less_than_h = z >= h
            
            if less_than_h:
                return t

        numerator = -b + sqrt(discriminant)
        
        if numerator > 0.0:
            t = numerator / (2*a)
            z = ray_origin[2] + t*ray_dir[2]
            
            less_than_h = z <= h
            if p_orient == -1:
                less_than_h = z >= h
            if less_than_h:
                return t


    return -999.0
    

@cuda.jit(device=True)
def intersect_ray_sphere(ray_origin: tuple, ray_dir: tuple, sphere_origin: tuple, sphere_radius: float) -> float:
   
    R = normalize(ray_dir)

    L = vector_difference(sphere_origin, ray_origin)

    a = dot(R, R)
    b = 2 * dot(L, R)
    c = dot(L, L) - sphere_radius * sphere_radius

    discriminant = b * b - 4 * a * c

    if discriminant < 0.0:
        return -999.9
    else:
        numerator = -b - sqrt(discriminant)

        if numerator > 0.0:
            return numerator / (2 * a)

        numerator = -b + sqrt(discriminant)

        if numerator > 0.0:
            return numerator / (2 * a)
        else:
            return -999.0


@cuda.jit(device=True)
def intersect_ray_plane(ray_origin: tuple, ray_dir: tuple, plane_origin: tuple, plane_normal: tuple) -> float:
    EPS = 0.0001

    N = plane_normal[0:3]

    denom = dot(ray_dir, plane_normal)

    if abs(denom) <= EPS:
        return -999.9

    LP = vector_difference(ray_origin, plane_origin)

    nominator = dot(LP, N)

    dist = nominator / denom

    if dist > 0:
        return dist
    else:
        return -999.0
    
@cuda.jit(device=True)
def intersect_ray_rectangle(ray_origin: tuple, ray_dir: tuple, rect_origin:tuple,u:tuple,v:tuple, N: tuple) -> float:
    EPS = 0.001
    denom = dot(N,ray_dir)
    
    if(abs(denom) <= EPS):
        return -999.0

    D = dot(N,rect_origin)
    t = (D-dot(N,ray_origin)) / denom

    inter0 = ray_origin[0] + t*ray_dir[0]
    inter1 = ray_origin[1] + t*ray_dir[1]
    inter2 = ray_origin[2] + t*ray_dir[2]

    intersection:tuple = (inter0,inter1,inter2)
    hit_vector = vector_difference(intersection, rect_origin)
    

    NN = cross_product(u,v)
    s = dot(NN,NN)
    w = (NN[0] * 1/s, NN[1] * 1/s, NN[2] * 1/s)
    
    a = dot(w,cross_product(hit_vector, v))
    b = dot(w,cross_product(u , hit_vector))
    
    if not( 0 < a < 1 and 0 < b < 1):
        return -999.0
    

    if t > 0:
        return t
    else:
        return -999.0
    

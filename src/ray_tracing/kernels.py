from numba import cuda
from .trace import sample
from .common import matmul, normalize, linear_comb, clip_color_vector


@cuda.jit
def render(pixel_loc, result, camera_origin, camera_rotation, spheres, lights, planes, amb, lamb, refl, refl_depth, aliasing,rectangles,parabaloids,CAMERA):
    R = camera_rotation
    (R0, R1, R2) = R[0, :], R[1, :], R[2, :]
    x, y = cuda.grid(2)

    if x <= pixel_loc.shape[1] and y <= pixel_loc.shape[2]:

        ray_origin = camera_origin[0], camera_origin[1], camera_origin[2]

        P = pixel_loc[0:3, x, y]

        ray_dir = matmul((R0, R1, R2), P)
        ray_dir = normalize(ray_dir)

        (R, G, B) = sample(ray_origin, ray_dir, spheres, lights, planes, amb, lamb, refl, refl_depth,rectangles,parabaloids,CAMERA)

        if aliasing and x+1 <= pixel_loc.shape[1] and x-1 >= 0 and y+1 <= pixel_loc.shape[2] and y-1 >= 0:

            P_left = pixel_loc[0:3, x-1, y]
            P_right = pixel_loc[0:3, x+1, y]
            P_top = pixel_loc[0:3, x, y+1]
            P_bot = pixel_loc[0:3, x, y-1]

            P_topleft = pixel_loc[0:3, x-1, y+1]
            P_topright = pixel_loc[0:3, x+1, y+1]
            P_bottomleft = pixel_loc[0:3, x-1, y-1]
            P_bottomright = pixel_loc[0:3, x+1, y-1]

            P_left = linear_comb(P, P_left, 0.5, 0.5)
            P_right = linear_comb(P, P_right, 0.5, 0.5)
            P_top = linear_comb(P, P_top, 0.5, 0.5)
            P_bot = linear_comb(P, P_bot, 0.5, 0.5)
            P_topleft = linear_comb(P, P_topleft, 0.5, 0.5)
            P_topright = linear_comb(P, P_topright, 0.5, 0.5)
            P_bottomleft = linear_comb(P, P_bottomleft, 0.5, 0.5)
            P_bottomright = linear_comb(P, P_bottomright, 0.5, 0.5)

            for P in [P_left, P_right, P_top, P_bot, P_topleft, P_topright, P_bottomleft, P_bottomright]:
                ray_dir = matmul((R0, R1, R2), P)
                ray_dir = normalize(ray_dir)
                (R_s, G_s, B_s) = sample(ray_origin, ray_dir, spheres, lights, planes, amb, lamb, refl, refl_depth,rectangles,parabaloids,CAMERA)

                R += R_s
                G += B_s
                B += G_s

            R = R / 9
            G = G / 9
            B = B / 9


        (R, G, B) = clip_color_vector((R, G, B))

        result[0, x, y] = R
        result[1, x, y] = G
        result[2, x, y] = B
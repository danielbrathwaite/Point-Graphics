import math
import random

import pygame as pg

CAMERA_POS = 0, -100, 0
CAMERA_MOVE_SPEED = 0.4
CAMERA_TILT_SPEED = 0.01

WIN = pg.display.set_mode((0, 0), pg.FULLSCREEN, 64)
WIN_WIDTH = pg.display.get_window_size()[0]
WIN_HEIGHT = pg.display.get_window_size()[1]
pg.display.set_caption("Projection of 3D points onto 2D screen")

MOUSE_POS = (WIN_WIDTH/2, WIN_HEIGHT/2)


def point_sorter(p):
    return -p.cords.distance_to(camera.pos)


def rotate(pointlist, axisvect, rotationamt):

    for p in pointlist:
        p.cords = p.cords.rotate_rad(rotationamt, axisvect)


def project(vector_a, vector_b):
    return (vector_a.dot(vector_b) / vector_b.dot(vector_b)) * vector_b


def calculate_pos_on_screen(camera_perspective, point_pos):
    displacement = point_pos - camera_perspective.pos

    true_focal_length = camera_perspective.focal_length / math.cos(math.pi * camera_perspective.dir.angle_to(displacement) / 180)

    ratio = true_focal_length / displacement.length()

    if project(displacement, camera_perspective.sidedir).magnitude() == 0:
        x_pos = 0
    elif camera_perspective.sidedir.dot(project(displacement, camera_perspective.sidedir)) < 0:
        x_pos = (ratio * project(displacement, camera_perspective.sidedir)).magnitude()
    else:
        x_pos = -(ratio * project(displacement, camera_perspective.sidedir)).magnitude()

    if project(displacement, camera_perspective.updir).magnitude() == 0:
        y_pos = 0
    elif camera_perspective.updir.dot(project(displacement, camera_perspective.updir)) < 0:
        y_pos = (ratio * project(displacement, camera_perspective.updir)).length()
    else:
        y_pos = -(ratio * project(displacement, camera_perspective.updir)).length()

    return x_pos + WIN_WIDTH/2, y_pos + WIN_HEIGHT/2


class Point:

    def __init__(self, position, color, a):
        self.cords = position
        self.color = color


class Camera:

    def __init__(self, positionvect, dirvect, upvect):
        self.pos = positionvect
        self.dir = dirvect
        self.updir = upvect
        self.sidedir = dirvect.cross(upvect)
        self.focal_length = 700


def drawWindow(win, ps, cam):

    pg.draw.rect(win, (21, 21, 21), (0, 0, WIN_WIDTH, WIN_HEIGHT))

    for point in ps:

        pos = calculate_pos_on_screen(cam, point.cords)

        displacement = point.cords - cam.pos

        size = round(10/(displacement.magnitude()/30) + 0.5)

        draw_color = pg.Color(point.color).lerp(pg.Color(0, 0, 0), min(displacement.magnitude(), 500)/500)

        if displacement.dot(cam.dir) > 0:
            pg.draw.circle(win, draw_color, pos, size)

    f_vector = (project(cam.dir * 40, pg.Vector3(1, 0, 0)).x, project(cam.dir * 40, pg.Vector3(0, 0, 1)).z)
    u_vector = (project(cam.updir * 40, pg.Vector3(1, 0, 0)).x, project(cam.updir * 40, pg.Vector3(0, 0, 1)).z)
    l_vector = (project(cam.sidedir * 40, pg.Vector3(1, 0, 0)).x, project(cam.sidedir * 40, pg.Vector3(0, 0, 1)).z)

    pg.draw.line(win, (200, 255, 255), (50, 50), (50 - u_vector[0], 50 - u_vector[1]), 3)
    pg.draw.line(win, (255, 255, 200), (50, 50), (50 - l_vector[0], 50 - l_vector[1]), 3)
    pg.draw.line(win, (255, 200, 255), (50, 50), (50 - f_vector[0], 50 - f_vector[1]), 3)

    pg.display.update()


if __name__ == '__main__':

    pg.mouse.set_visible(False)
    pg.mouse.set_pos([MOUSE_POS[0], MOUSE_POS[1]])

    circles_up = pg.Vector3(0, 0, 1)

    va = pg.Vector3(1, 0, 0)
    vb = pg.Vector3(-1, 0, 0)

    points = list()

    campos = pg.Vector3(0, 0, 100)
    camdir = pg.Vector3(0, 0, -1)
    camdirup = pg.Vector3(1, 0, 0)

    camera = Camera(campos, camdir, camdirup)

    amt = 50

    for x in range(amt):
        for y in range(amt):
            """color = ((math.sin(float(y) / amt * 2 * math.pi) + 1) * 255 / 2,
                     (math.sin(float(x) / amt * 2 * math.pi) + 1) * 255 / 2, 255)
            points.append(Point(pg.Vector3(x/amt*30, y/amt*30, 0), color, 1))"""
            vect = pg.Vector3(random.random()-0.5, random.random()-0.5, random.random()-0.5).normalize()*50
            points.append(Point(vect, (255, 200, 255), 1))
            points.append(Point(-vect*0.7, (200, 200, 255), 1))

    points.append(Point(pg.Vector3(0, 0, 0), (255, 255, 255), 1))

    iterations = 0
    over = back = forward = left = up = down = right = tright = tleft = tup = tdown = False
    while not over:

        iterations += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                over = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    over = True
                if event.key == pg.K_s:
                    back = True
                elif event.key == pg.K_w:
                    forward = True
                if event.key == pg.K_d:
                    right = True
                elif event.key == pg.K_a:
                    left = True
                if event.key == pg.K_LSHIFT:
                    down = True
                elif event.key == pg.K_SPACE:
                    up = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_s:
                    back = False
                elif event.key == pg.K_w:
                    forward = False
                if event.key == pg.K_d:
                    right = False
                elif event.key == pg.K_a:
                    left = False
                if event.key == pg.K_LSHIFT:
                    down = False
                elif event.key == pg.K_SPACE:
                    up = False

        if back:
            camera.pos -= camera.dir * CAMERA_MOVE_SPEED
        elif forward:
            camera.pos += camera.dir * CAMERA_MOVE_SPEED
        if right:
            camera.pos -= camera.sidedir * CAMERA_MOVE_SPEED
        elif left:
            camera.pos += camera.sidedir * CAMERA_MOVE_SPEED
        if up:
            camera.pos += camera.updir * CAMERA_MOVE_SPEED
        elif down:
            camera.pos -= camera.updir * CAMERA_MOVE_SPEED

        horizontal_rotation = (pg.mouse.get_pos()[0] - MOUSE_POS[0]) * CAMERA_TILT_SPEED / 5
        vertical_rotation = (MOUSE_POS[1] - pg.mouse.get_pos()[1]) * CAMERA_TILT_SPEED / 5

        camera.dir = camera.dir.rotate_rad(horizontal_rotation, pg.Vector3(0, 0, 1))
        camera.sidedir = camera.sidedir.rotate_rad(horizontal_rotation, pg.Vector3(0, 0, 1))
        camera.updir = camera.updir.rotate_rad(horizontal_rotation, pg.Vector3(0, 0, 1))

        camera.dir = camera.dir.rotate_rad(vertical_rotation, camera.sidedir)
        camera.updir = camera.updir.rotate_rad(vertical_rotation, camera.sidedir)

        pg.mouse.set_pos([MOUSE_POS[0], MOUSE_POS[1]])

        """for point in points:
            point.cords.z = math.sin(iterations/100 + point.cords.x/10)*10
            point.cords.z = point.cords.z + math.cos(iterations / 100 + point.cords.y / 10) * 10"""

        for point in points:
            if point.cords.magnitude() > 47:
                point.cords = point.cords.rotate_rad(0.01, pg.Vector3(1, 0, 1))
            else:
                point.cords = point.cords.rotate_rad(-0.01, pg.Vector3(0, 1, 1))

        points.sort(key=point_sorter)
        drawWindow(WIN, points, camera)



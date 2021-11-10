import math
import random

import pygame as pg
import pygame.time

CAMERA_POS = 0, -100, 0
CAMERA_MOVE_SPEED = 0.4
CAMERA_TILT_SPEED = 0.01
CAMERA_FOCAL_DISTANCE = 700

SPHERE_POINTS = 100

BALL_RADIUS = 2

GRAVITY = 0.0002
FRICTION = 0.0005

WIN = pg.display.set_mode((0, 0), pg.FULLSCREEN, 64)
WIN_WIDTH = pg.display.get_window_size()[0]
WIN_HEIGHT = pg.display.get_window_size()[1]

pg.init()
pg.display.set_caption("Projection of 3D points onto 2D screen")
font = pg.font.SysFont('Comic Sans MS', 30)

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

    true_focal_length = CAMERA_FOCAL_DISTANCE / math.cos(math.pi * camera_perspective.dir.angle_to(displacement) / 180)

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

    def __init__(self, position, color, vel, lock):
        self.cords = position
        self.color = color
        self.velocity = vel
        self.locked = lock

    def move(self, ps, gravity):
        if self.locked:
            return False
        if gravity:
            self.velocity = self.velocity + pg.Vector3(0, 0, -GRAVITY)

        accuracy = 1
        for x in range(accuracy):
            for point in ps:
                if not point == self:
                    if (point.cords - self.cords - self.velocity).magnitude() <= BALL_RADIUS * 2:
                        reflect_velocity_taken = project(point.velocity, point.cords - self.cords)
                        reflect_velocity_given = project(self.velocity, point.cords - self.cords)

                        self.velocity = self.velocity - reflect_velocity_given
                        point.velocity = point.velocity - reflect_velocity_taken

                        self.velocity = self.velocity + reflect_velocity_taken
                        point.velocity = point.velocity + reflect_velocity_given
        for point in ps:
            if (self.cords + self.velocity - point.cords).magnitude() <= BALL_RADIUS * 2 and not point == self:
                if self.velocity.dot(point.cords - self.cords) > 0:
                    self.velocity = self.velocity - project(self.velocity, point.cords - self.cords)

        self.cords += self.velocity


class Camera:

    def __init__(self, positionvect, dirvect, upvect):
        self.pos = positionvect
        self.dir = dirvect
        self.updir = upvect
        self.sidedir = dirvect.cross(upvect)


def drawWindow(win, ps, cam):

    pg.draw.rect(win, (21, 21, 21), (0, 0, WIN_WIDTH, WIN_HEIGHT))

    for point in ps:

        pos = calculate_pos_on_screen(cam, point.cords)

        displacement = point.cords - cam.pos

        size = max(BALL_RADIUS / displacement.magnitude() * CAMERA_FOCAL_DISTANCE, 1) + 1
        #size = max(BALL_RADIUS * 10 / (displacement.magnitude()/30), 1)

        draw_color = pg.Color(point.color).lerp(pg.Color(0, 0, 0), min(displacement.magnitude(), 1000)/1000)

        if displacement.dot(cam.dir) > 0:
            pg.draw.circle(win, draw_color, pos, size)

    f_vector = (project(cam.dir * 40, pg.Vector3(1, 0, 0)).x, project(cam.dir * 40, pg.Vector3(0, 0, 1)).z)
    u_vector = (project(cam.updir * 40, pg.Vector3(1, 0, 0)).x, project(cam.updir * 40, pg.Vector3(0, 0, 1)).z)
    l_vector = (project(cam.sidedir * 40, pg.Vector3(1, 0, 0)).x, project(cam.sidedir * 40, pg.Vector3(0, 0, 1)).z)

    pg.draw.line(win, (200, 255, 255), (50, 50), (50 - u_vector[0], 50 - u_vector[1]), 3)
    pg.draw.line(win, (255, 255, 200), (50, 50), (50 - l_vector[0], 50 - l_vector[1]), 3)
    pg.draw.line(win, (255, 200, 255), (50, 50), (50 - f_vector[0], 50 - f_vector[1]), 3)


if __name__ == '__main__':

    currentTime = 2
    prevTime = 1

    pg.mouse.set_visible(False)
    pg.mouse.set_pos([MOUSE_POS[0], MOUSE_POS[1]])

    circles_up = pg.Vector3(0, 0, 1)

    points = list()
    static_points = list()
    static_points.append(Point(pg.Vector3(0, 0, 0), (255, 255, 255), pg.Vector3(0, 0, 0), True))

    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians
    for i in range(SPHERE_POINTS):
        y = 1 - (i / float(SPHERE_POINTS - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y

        theta = phi * i  # golden angle increment

        x = math.cos(theta) * radius
        z = math.sin(theta) * radius

        static_points.append(Point(pg.Vector3(x, y, z).normalize() * (75 + BALL_RADIUS*2), (255, 255, 255), pg.Vector3(0, 0, 0), True))

    campos = pg.Vector3(-200, 0.001, 0)
    camdir = pg.Vector3(1, 0, 0)
    camdirup = pg.Vector3(0, 0, 1)

    camera = Camera(campos, camdir, camdirup)

    iterations = 0
    over = back = forward = left = up = down = right = tright = tleft = tup = tdown = making_points = False
    pg.mouse.set_pos((WIN_WIDTH/2, WIN_HEIGHT/2))
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
                if event.key == pg.K_q:
                    making_points = True
                if event.key == pg.K_e:
                    points.clear()
                if event.key == pg.K_f:
                    GRAVITY = -GRAVITY
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
                if event.key == pg.K_q:
                    making_points = False

        if making_points and iterations % 80 == 0:
            points.append(Point(pg.Vector3(0, 0, 0), (random.random() * 255, random.random() * 255,
                                random.random() * 255), pg.Vector3(random.random() - 0.5, random.random() - 0.5,
                                random.random() - 0.5).normalize() * 0.3, False))

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

        for point in points:
            point.move(points, True)
            point.velocity = point.velocity * (1 - FRICTION)
            if point.cords.magnitude() > 75:
                point.cords = point.cords.normalize() * 75
                point.velocity = point.velocity.reflect(point.cords)

        draw_points = points + static_points
        draw_points.sort(key=point_sorter)
        drawWindow(WIN, draw_points, camera)

        text = font.render(str(len(points)), False, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.topright = (WIN_WIDTH - textRect.width, textRect.height)
        WIN.blit(text, textRect)
        pg.display.update()



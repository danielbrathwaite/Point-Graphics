import math
import pygame as pg

WIN_WIDTH = 800
WIN_HEIGHT = 600

CAMERA_POS = 0, -100, 0
CAMERA_MOVE_SPEED = 0.2
CAMERA_TILT_SPEED = 0.01

WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.DOUBLEBUF, 64)
pg.display.set_caption("Projection of 3D points onto 2D screen")


def point_sorter(p):
    return -p.cords.distance_to(camera.pos)


def vector_to_theta(positionvect):
    x = positionvect.x
    y = positionvect.y
    z = positionvect.z

    theta1 = math.atan(y / x)

    xy_len = math.sqrt((x * x) + (y * y))
    theta2 = math.atan(z / xy_len)
    if x < 0:
        theta1 += math.pi
    """theta1 %= math.pi*2
    if theta1 > math.pi/2 or theta1 < -math.pi:
        theta2 += math.pi"""

    len = math.sqrt((x * x) + (y * y) + (z * z))

    return pg.Vector3(theta1, theta2, len)


def theta_to_vector(positionangles):
    theta1 = positionangles.x
    theta2 = positionangles.y
    len = positionangles.z

    z = math.sin(theta2) * len

    xy_len = math.cos(theta2) * len
    x = math.cos(theta1) * xy_len
    y = math.sin(theta1) * xy_len

    return pg.Vector3(x, y, z)


def rotate(points, axisvect, rotationamt):

    for p in points:
        p.cords = p.cords.rotate_rad(rotationamt, axisvect)


def project(vector_a, vector_b):
    return (vector_a.dot(vector_b) / vector_b.dot(vector_b)) * vector_b


def calculate_pos_on_screen(camera_perspective, point_pos):
    displacement = point_pos - camera_perspective.pos

    true_focal_length = camera_perspective.focal_length / math.cos(math.pi * camera_perspective.dir.angle_to(displacement) / 180)

    ratio = true_focal_length / displacement.length()

    #distance of the mild distortion along x-and y-axis
    accuracy = 0.001

    if project(displacement, camera_perspective.sidedir).magnitude() == 0:
        x_pos = 0
    elif (camera_perspective.sidedir * accuracy + project(displacement, camera_perspective.sidedir)).magnitude() < project(displacement, camera_perspective.sidedir).magnitude():
        x_pos = (ratio * project(displacement, camera_perspective.sidedir)).magnitude()
    else:
        x_pos = -(ratio * project(displacement, camera_perspective.sidedir)).magnitude()

    if project(displacement, camera_perspective.updir).magnitude() == 0:
        y_pos = 0
    elif (camera_perspective.updir * accuracy + project(displacement, camera_perspective.updir)).magnitude() < project(displacement, camera_perspective.updir).magnitude():
        y_pos = (ratio * project(displacement, camera_perspective.updir)).length()
    else:
        y_pos = -(ratio * project(displacement, camera_perspective.updir)).length()

    return x_pos, y_pos


class Point:

    def __init__(self, positionangles, color):
        self.cords = theta_to_vector(positionangles)
        self.color = color


class Camera:

    def __init__(self, positionvect, dirvect, upvect):
        self.pos = positionvect
        self.dir = dirvect
        self.updir = upvect
        self.sidedir = dirvect.cross(upvect)
        self.focal_length = 700


def drawWindow(win, ps, cam):

    pg.draw.rect(win, (100, 200, 100), (0, 0, WIN_WIDTH, WIN_HEIGHT))

    for point in ps:

        pos = calculate_pos_on_screen(cam, point.cords)

        position = (pos[0] + WIN_WIDTH/2, pos[1] + WIN_HEIGHT/2)

        displacement = point.cords - cam.pos

        size = round(10/(displacement.magnitude()/30) + 1)
        if displacement.angle_to(cam.dir) < 90:
            pg.draw.circle(win, point.color, position, size)

    f_vector = (project(cam.dir * 40, pg.Vector3(1, 0, 0)).x, project(cam.dir * 40, pg.Vector3(0, 0, 1)).z)
    u_vector = (project(cam.updir * 40, pg.Vector3(1, 0, 0)).x, project(cam.updir * 40, pg.Vector3(0, 0, 1)).z)
    l_vector = (project(cam.sidedir * 40, pg.Vector3(1, 0, 0)).x, project(cam.sidedir * 40, pg.Vector3(0, 0, 1)).z)

    pg.draw.line(win, (200, 255, 255), (50, 50), (50 - u_vector[0], 50 - u_vector[1]), 3)
    pg.draw.line(win, (255, 255, 200), (50, 50), (50 - l_vector[0], 50 - l_vector[1]), 3)
    pg.draw.line(win, (255, 200, 255), (50, 50), (50 - f_vector[0], 50 - f_vector[1]), 3)

    pg.display.update()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    va = pg.Vector3(1, 0, 0)
    vb = pg.Vector3(-1, 0, 0)

    points = list()

    campos = pg.Vector3(0, -100, 0)
    camdir = pg.Vector3(0, 1, 0)
    camdirup = pg.Vector3(0, 0, 1)

    camera = Camera(campos, camdir, camdirup)

    amt = 60

    points.append(Point(pg.Vector3(-math.pi / 4, -math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(-math.pi / 4, math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(math.pi / 4, -math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(math.pi / 4, math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(-math.pi * 0.75, -math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(-math.pi * 0.75, math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(math.pi * 0.75, -math.pi / 4, 40), pg.Vector3(255, 0, 0)))
    points.append(Point(pg.Vector3(math.pi * 0.75, math.pi / 4, 40), pg.Vector3(255, 0, 0)))

    for x in range(amt):

        for y in range(amt):

            angles = pg.Vector3((x*math.pi/amt, y*2.0 * math.pi/amt, 40))
            color = ((math.sin(float(y)/amt*2*math.pi) + 1) * 255 / 2, (math.sin(float(x)/amt*2*math.pi) + 1) * 255 / 2, 255)
            points.append(Point(angles, color))

    iterations = 0
    over = False
    back = False
    forward = False
    left = False
    up = False
    down = False
    right = False
    tright = False
    tleft = False
    tup= False
    tdown = False
    while(not over):

        iterations += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                over = True
            if event.type == pg.KEYDOWN:
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
                if event.key == pg.K_LEFT:
                    tleft = True
                elif event.key == pg.K_RIGHT:
                    tright = True
                if event.key == pg.K_UP:
                    tup = True
                elif event.key == pg.K_DOWN:
                    tdown = True
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
                if event.key == pg.K_LEFT:
                    tleft = False
                elif event.key == pg.K_RIGHT:
                    tright = False
                if event.key == pg.K_UP:
                    tup = False
                elif event.key == pg.K_DOWN:
                    tdown = False

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
        if tleft:
            camera.dir = camera.dir.rotate_rad(-CAMERA_TILT_SPEED, camera.updir)
            camera.sidedir = camera.sidedir.rotate_rad(-CAMERA_TILT_SPEED, camera.updir)
        elif tright:
            camera.dir = camera.dir.rotate_rad(CAMERA_TILT_SPEED, camera.updir)
            camera.sidedir = camera.sidedir.rotate_rad(CAMERA_TILT_SPEED, camera.updir)
        if tup:
            camera.dir = camera.dir.rotate_rad(CAMERA_TILT_SPEED, camera.sidedir)
            camera.updir = camera.updir.rotate_rad(CAMERA_TILT_SPEED, camera.sidedir)
        elif tdown:
            camera.dir = camera.dir.rotate_rad(-CAMERA_TILT_SPEED, camera.sidedir)
            camera.updir = camera.updir.rotate_rad(-CAMERA_TILT_SPEED, camera.sidedir)

        rotate(points, pg.Vector3(1, 1, 1), 0.01)

        points.sort(key=point_sorter)
        drawWindow(WIN, points, camera)



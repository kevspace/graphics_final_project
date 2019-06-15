from display import *
from matrix import *
from gmath import *
import re

def draw_scanline(x0, z0, x1, z1, y, screen, zbuffer, color):
    if x0 > x1:
        tx = x0
        tz = z0
        x0 = x1
        z0 = z1
        x1 = tx
        z1 = tz

    x = x0
    z = z0
    delta_z = (z1 - z0) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0

    while x <= x1:
        plot(screen, zbuffer, color, x, y, z)
        x += 1
        z += delta_z

def scanline_convert(polygons, i, screen, zbuffer, color):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [(polygons[i][0], polygons[i][1], polygons[i][2]),
               (polygons[i + 1][0], polygons[i + 1][1], polygons[i + 1][2]),
               (polygons[i + 2][0], polygons[i + 2][1], polygons[i + 2][2])]

    points.sort(key = lambda x: x[1])
    x0 = points[BOT][0]
    z0 = points[BOT][2]
    x1 = points[BOT][0]
    z1 = points[BOT][2]
    y = int(points[BOT][1])

    distance0 = int(points[TOP][1]) - y * 1.0 + 1
    distance1 = int(points[MID][1]) - y * 1.0 + 1
    distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

    dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

    while y <= int(points[TOP][1]):
        if (not flip and y >= int(points[MID][1])):
            flip = True

            dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
            dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
            x1 = points[MID][0]
            z1 = points[MID][2]

        #  draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
        draw_scanline(int(x0), z0, int(x1), z1, y, screen, zbuffer, color)
        x0 += dx0
        z0 += dz0
        x1 += dx1
        z1 += dz1
        y += 1

def interpolate(x0, y0, z0, x1, y1, z1, screen, zbuffer, view, ambient, lights, symbols, reflect, colornormal0, colornormal1, shading):
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt
        colornormal2 = colornormal0
        colornormal0 = colornormal1
        colornormal1 = colornormal2

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False
    r = colornormal0[0]
    g = colornormal0[1]
    b = colornormal0[2]

    if (abs(x1 - x0) >= abs(y1 - y0)): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x
        if (A > 0): #octant 1
            d = A + B / 2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B / 2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y)
        if (A > 0): #octant 2
            d = A / 2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A / 2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0
    dr = (colornormal1[0] - colornormal0[0]) / distance if distance != 0 else 0
    dg = (colornormal1[1] - colornormal0[1]) / distance if distance != 0 else 0
    db = (colornormal1[2] - colornormal0[2]) / distance if distance != 0 else 0

    while (loop_start < loop_end):
        if shading == 'phong':
            normal = [r, g, b]
            color = get_lighting(normal, view, ambient, lights, symbols, reflect)
        else:
            color = [int(r), int(g), int(b)]
        plot(screen, zbuffer, color, x, y, z)
        if ((wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
            (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):

            x += dx_northeast
            y += dy_northeast
            d += d_northeast
        else:
            x += dx_east
            y += dy_east
            d += d_east
        z += dz
        r += dr
        g += dg
        b += db
        loop_start += 1
    if shading == "phong":
        normal = [r, g, b]
        color = get_lighting(normal, view, ambient, lights, symbols, reflect)
    else:
        color = [int(r), int(g), int(b)]
    plot(screen, zbuffer, color, x, y, z)

def shade(polygons, i, screen, zbuffer, view, ambient, lights, symbols, reflect, vectors, shading):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [((polygons[i][0], polygons[i][1], polygons[i][2]), vectors[0]),
               ((polygons[i + 1][0], polygons[i + 1][1], polygons[i + 1][2]), vectors[1]),
               ((polygons[i + 2][0], polygons[i + 2][1], polygons[i + 2][2]), vectors[2])]

    points.sort(key = lambda x: x[0][1])
    x0 = points[BOT][0][0]
    z0 = points[BOT][0][2]
    x1 = points[BOT][0][0]
    z1 = points[BOT][0][2]
    y = int(points[BOT][0][1])

    distance0 = int(points[TOP][0][1]) - y * 1.0 + 1
    distance1 = int(points[MID][0][1]) - y * 1.0 + 1
    distance2 = int(points[TOP][0][1]) - int(points[MID][0][1]) * 1.0 + 1

    dx0 = (points[TOP][0][0] - points[BOT][0][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][0][2] - points[BOT][0][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0][0] - points[BOT][0][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][0][2] - points[BOT][0][2]) / distance1 if distance1 != 0 else 0

    r0 = points[BOT][1][0]
    g0 = points[BOT][1][1]
    b0 = points[BOT][1][2]
    r1 = points[BOT][1][0]
    g1 = points[BOT][1][1]
    b1 = points[BOT][1][2]

    dr0 = (points[TOP][1][0] - points[BOT][1][0]) / distance0 if distance0 != 0 else 0
    dg0 = (points[TOP][1][1] - points[BOT][1][1]) / distance0 if distance0 != 0 else 0
    db0 = (points[TOP][1][2] - points[BOT][1][2]) / distance0 if distance0 != 0 else 0
    dr1 = (points[MID][1][0] - points[BOT][1][0]) / distance1 if distance1 != 0 else 0
    dg1 = (points[MID][1][1] - points[BOT][1][1]) / distance1 if distance1 != 0 else 0
    db1 = (points[MID][1][2] - points[BOT][1][2]) / distance1 if distance1 != 0 else 0

    if distance0 == 0:
        r1 = points[TOP][1][0]
        g1 = points[TOP][1][1]
        b1 = points[TOP][1][2]
    elif distance1 == 0:
        r1 = points[MID][1][0]
        g1 = points[MID][1][1]
        b1 = points[MID][1][2]

    while y <= int(points[TOP][0][1]):
        if (not flip and y >= int(points[MID][0][1])):
            flip = True

            dx1 = (points[TOP][0][0] - points[MID][0][0]) / distance2 if distance2 != 0 else 0
            dz1 = (points[TOP][0][2] - points[MID][0][2]) / distance2 if distance2 != 0 else 0
            x1 = points[MID][0][0]
            z1 = points[MID][0][2]

            dr1 = (points[TOP][1][0] - points[MID][1][0]) / distance2 if distance2 != 0 else 0
            dg1 = (points[TOP][1][1] - points[MID][1][1]) / distance2 if distance2 != 0 else 0
            db1 = (points[TOP][1][2] - points[MID][1][2]) / distance2 if distance2 != 0 else 0
            r1 = points[MID][1][0]
            g1 = points[MID][1][1]
            b1 = points[MID][1][2]

        colornormal0 = [r0, g0, b0]
        colornormal1 = [r1, g1, b1]
        interpolate(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, view, ambient, lights, symbols, reflect, colornormal0, colornormal1, shading)
        x0 += dx0
        z0 += dz0
        x1 += dx1
        z1 += dz1
        y += 1
        r0 += dr0
        g0 += dg0
        b0 += db0
        r1 += dr1
        g1 += dg1
        b1 += db1

def mesh_points(filename):
    points = []
    f = open(filename, 'r')
    for line in f.readlines():
        line = re.sub(' +', ' ', line).split(" ")
        if line[0] == 'v':
            points.append([float(line[1]), float(line[2]), float(line[3])])
    f.close()
    return points

def mesh_faces(edges, filename):
    points = mesh_points(filename)
    f = open(filename, 'r')
    for line in f.readlines():
    	line = re.sub(' +', ' ', line).split(" ")
        if line[0] == 'f':
        	count = 2
        	vertices = line[1:]
        	while count < len(vertices):
                    p0 = int(vertices[0]) - 1
                    p1 = int(vertices[count - 1]) - 1
                    p2 = int(vertices[count]) - 1
                    add_polygon(edges, points[p0][0] * 10, points[p0][1] * 10, points[p0][2] * 10,
                                       points[p1][0] * 10, points[p1][1] * 10, points[p1][2] * 10,
                                       points[p2][0] * 10, points[p2][1] * 10, points[p2][2] * 10)
                    count += 1
	f.close()

def add_polygon(polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2):
    add_point(polygons, x0, y0, z0)
    add_point(polygons, x1, y1, z1)
    add_point(polygons, x2, y2, z2)

def draw_polygons(polygons, screen, zbuffer, view, ambient, lights, symbols, reflect, shading):
    if len(polygons) < 2:
        print ('Need at least 3 points to draw')
        return

    point = 0
    if shading == 'gouraud' or shading == 'phong':
        normals = {}
        while point < len(polygons) - 2:
            normal = calculate_normal(polygons, point)[:]
            normals[tuple(polygons[point])] = [normals[tuple(polygons[point])][0] + normal[0], normals[tuple(polygons[point])][1] + normal[1], normals[tuple(polygons[point])][2] + normal[2]] if tuple(polygons[point]) in normals else normal
            normals[tuple(polygons[point + 1])] = [normals[tuple(polygons[point + 1])][0] + normal[0], normals[tuple(polygons[point + 1])][1] + normal[1], normals[tuple(polygons[point + 1])][2] + normal[2]] if tuple(polygons[point + 1]) in normals else normal
            normals[tuple(polygons[point + 2])] = [normals[tuple(polygons[point + 2])][0] + normal[0], normals[tuple(polygons[point + 2])][1] + normal[1], normals[tuple(polygons[point + 2])][2] + normal[2]] if tuple(polygons[point + 2]) in normals else normal

            point += 3

    point = 0
    while point < len(polygons) - 2:
        face_normal = calculate_normal(polygons, point)[:]
        if dot_product(face_normal, view) > 0:
            if shading == 'flat':
                color = get_lighting(face_normal, view, ambient, lights, symbols, reflect)
                scanline_convert(polygons, point, screen, zbuffer, color)
            elif shading == 'gouraud':
                normal0 = normals[tuple(polygons[point])]
                normal1 = normals[tuple(polygons[point + 1])]
                normal2 = normals[tuple(polygons[point + 2])]
                color = get_lighting(normal, view, ambient, lights, symbols, reflect)
                color0 = get_lighting(normal0, view, ambient, lights, symbols, reflect)
                color1 = get_lighting(normal1, view, ambient, lights, symbols, reflect)
                color2 = get_lighting(normal2, view, ambient, lights, symbols, reflect)
                colors = [color0, color1, color2]
                shade(polygons, point, screen, zbuffer, view, ambient, lights, symbols, reflect, colors, shading)
            elif shading == 'phong':
                normal0 = normals[tuple(polygons[point])]
                normal1 = normals[tuple(polygons[point + 1])]
                normal2 = normals[tuple(polygons[point + 2])]
                normalss = [normal0, normal1, normal2]
                shade(polygons, point, screen, zbuffer, view, ambient, lights, symbols, reflect, normalss, shading)

        point += 3

def add_box(polygons, x, y, z, width, height, depth):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z)
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z)
    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1)
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1)

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1)
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1)
    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z)
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z)

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1)
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z)
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z)
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1)

def add_sphere(polygons, cx, cy, cz, r, step):
    points = generate_sphere(cx, cy, cz, r, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    step += 1
    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):
            p0 = lat * step + longt
            p1 = p0 + 1
            p2 = (p1 + step) % (step * (step - 1))
            p3 = (p0 + step) % (step * (step - 1))

            if longt != step - 2:
                add_polygon(polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p1][0],
                             points[p1][1],
                             points[p1][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2])
            if longt != 0:
                add_polygon(polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2],
                             points[p3][0],
                             points[p3][1],
                             points[p3][2])

def generate_sphere(cx, cy, cz, r, step):
    points = []

    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation / float(step)
        for circle in range(circ_start, circ_stop + 1):
            circ = circle / float(step)

            x = r * math.cos(math.pi * circ) + cx
            y = r * math.sin(math.pi * circ) * math.cos(2 * math.pi * rot) + cy
            z = r * math.sin(math.pi * circ) * math.sin(2 * math.pi * rot) + cz

            points.append([x, y, z])
    return points

def add_torus(polygons, cx, cy, cz, r0, r1, step):
    points = generate_torus(cx, cy, cz, r0, r1, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):
            p0 = lat * step + longt;
            if (longt == (step - 1)):
                p1 = p0 - longt;
            else:
                p1 = p0 + 1;
            p2 = (p1 + step) % (step * step);
            p3 = (p0 + step) % (step * step);

            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p3][0],
                        points[p3][1],
                        points[p3][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2])
            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2],
                        points[p1][0],
                        points[p1][1],
                        points[p1][2])

def generate_torus(cx, cy, cz, r0, r1, step):
    points = []
    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation / float(step)
        for circle in range(circ_start, circ_stop):
            circ = circle / float(step)

            x = math.cos(2 * math.pi * rot) * (r0 * math.cos(2 * math.pi * circ) + r1) + cx;
            y = r0 * math.sin(2*math.pi * circ) + cy;
            z = -math.sin(2 * math.pi * rot) * (r0 * math.cos(2 * math.pi * circ) + r1) + cz;

            points.append([x, y, z])
    return points

def add_circle(points, cx, cy, cz, r, step):
    x0 = r + cx
    y0 = cy
    i = 1

    while i <= step:
        t = float(i) / step
        x1 = r * math.cos(2 * math.pi * t) + cx;
        y1 = r * math.sin(2 * math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        i += 1

def add_curve(points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type):
    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    i = 1
    while i <= step:
        t = float(i) / step
        x = t * (t * (xcoefs[0] * t + xcoefs[1]) + xcoefs[2]) + xcoefs[3]
        y = t * (t * (ycoefs[0] * t + ycoefs[1]) + ycoefs[2]) + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        i += 1

def draw_lines(matrix, screen, zbuffer, color):
    if len(matrix) < 2:
        print ('Need at least 2 points to draw')
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line(int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point += 2

def add_edge(matrix, x0, y0, z0, x1, y1, z1):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point(matrix, x, y, z = 0):
    matrix.append([x, y, z, 1])

def draw_line(x0, y0, z0, x1, y1, z1, screen, zbuffer, color):
    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if (abs(x1-x0) >= abs(y1 - y0)): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x + 1
        if (A > 0): #octant 1
            d = A + B / 2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B / 2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y) + 1
        if (A > 0): #octant 2
            d = A / 2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A / 2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0

    while (loop_start < loop_end):
        plot(screen, zbuffer, color, x, y, z)
        if ((wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
            (tall and ((A > 0 and d < 0) or (A < 0 and d > 0)))):

            x += dx_northeast
            y += dy_northeast
            d += d_northeast
        else:
            x += dx_east
            y += dy_east
            d += d_east
        z += dz
        loop_start += 1
    plot(screen, zbuffer, color, x, y, z)

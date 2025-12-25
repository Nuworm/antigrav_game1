import math
import collections

# Hex coordinates in axial (q, r)
# s is implicitly -q - r
Hex = collections.namedtuple("Hex", ["q", "r"])

def hex_add(a, b):
    return Hex(a.q + b.q, a.r + b.r)

def hex_subtract(a, b):
    return Hex(a.q - b.q, a.r - b.r)

def hex_scale(a, k):
    return Hex(a.q * k, a.r * k)

def hex_direction(direction):
    assert 0 <= direction < 6
    return hex_directions[direction]

def hex_neighbor(hex, direction):
    return hex_add(hex, hex_direction(direction))

hex_directions = [
    Hex(1, 0), Hex(1, -1), Hex(0, -1),
    Hex(-1, 0), Hex(-1, 1), Hex(0, 1),
]

def hex_length(hex):
    return (abs(hex.q) + abs(hex.r) + abs(-hex.q - hex.r)) // 2

def hex_distance(a, b):
    return hex_length(hex_subtract(a, b))

def hex_to_pixel(layout, h):
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    x = (M.f0 * h.q + M.f1 * h.r) * size.x
    y = (M.f2 * h.q + M.f3 * h.r) * size.y
    return Point(x + origin.x, y + origin.y)

def pixel_to_hex(layout, p):
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = M.b0 * pt.x + M.b1 * pt.y
    r = M.b2 * pt.x + M.b3 * pt.y
    return hex_round(q, r, -q - r) # Round to nearest hex

def hex_round(frac_q, frac_r, frac_s):
    q = round(frac_q)
    r = round(frac_r)
    s = round(frac_s)
    q_diff = abs(q - frac_q)
    r_diff = abs(r - frac_r)
    s_diff = abs(s - frac_s)
    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s
    return Hex(int(q), int(r))

Point = collections.namedtuple("Point", ["x", "y"])

Orientation = collections.namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])

layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0,
                            math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0,
                            0.5)
layout_flat = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0),
                          2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0,
                          0.0)

class Layout:
    def __init__(self, orientation, size, origin):
        self.orientation = orientation
        self.size = size
        self.origin = origin

def hex_corner_offset(layout, corner):
    M = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (M.start_angle + corner) / 6
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))

def polygon_corners(layout, h):
    corners = []
    center = hex_to_pixel(layout, h)
    for i in range(6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners

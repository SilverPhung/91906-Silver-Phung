from pyglet.math import Vec2

def to_vector(tuple: tuple[float, float]) -> Vec2:
    return Vec2(tuple[0], tuple[1])

def to_tuple(vector: Vec2) -> tuple[float, float]:
    return vector.x, vector.y
from pyglet.math import Vec2


def to_vector(tuple_arg: tuple[float, float]) -> Vec2:
    return Vec2(tuple_arg[0], tuple_arg[1])


def to_tuple(vector: Vec2) -> tuple[float, float]:
    return vector.x, vector.y

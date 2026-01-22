"""Egyptian symbol drawing functions"""
import math
from kivy.graphics import Color, Ellipse, Rectangle, Line


def draw_ankh_symbol(canvas, x, y, size, color_tuple):
    """Draw Egyptian Ankh symbol"""
    with canvas:
        Color(*color_tuple)
        Ellipse(pos=(x + size*0.35, y + size*0.6), size=(size*0.3, size*0.3))
        Rectangle(pos=(x + size*0.45, y + size*0.1), size=(size*0.1, size*0.65))
        Rectangle(pos=(x + size*0.25, y + size*0.45), size=(size*0.5, size*0.08))


def draw_eye_of_horus(canvas, x, y, size, color_tuple):
    """Draw Eye of Horus symbol"""
    with canvas:
        Color(*color_tuple)
        Line(points=[
            x + size*0.2, y + size*0.5,
            x + size*0.5, y + size*0.7,
            x + size*0.8, y + size*0.5,
            x + size*0.5, y + size*0.3,
            x + size*0.2, y + size*0.5
        ], width=2)
        Ellipse(pos=(x + size*0.45, y + size*0.45), size=(size*0.1, size*0.1))
        Line(points=[
            x + size*0.5, y + size*0.3,
            x + size*0.6, y + size*0.2,
            x + size*0.5, y + size*0.1
        ], width=1.5)


def draw_water_waves(canvas, x, y, size, color_tuple):
    """Draw water wave symbols"""
    with canvas:
        Color(*color_tuple)
        for i in range(3):
            y_offset = y + size*0.25 + i*size*0.25
            points = []
            for j in range(5):
                wave_x = x + size*0.2 + j*size*0.15
                wave_y = y_offset + math.sin(j) * size*0.1
                points.extend([wave_x, wave_y])
            Line(points=points, width=2)


def draw_ankh_small(canvas, x, y, size, color_tuple):
    """Draw small Ankh for rebirth"""
    with canvas:
        Color(*color_tuple)
        Ellipse(pos=(x + size*0.4, y + size*0.65), size=(size*0.2, size*0.2))
        Rectangle(pos=(x + size*0.47, y + size*0.2), size=(size*0.06, size*0.5))
        Rectangle(pos=(x + size*0.3, y + size*0.55), size=(size*0.4, size*0.06))
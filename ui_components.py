from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle


def create_styled_button(text, size_hint, pos_hint, bg_color, font_size='20sp'):
    btn = Button(
        text=text,
        size_hint=size_hint,
        pos_hint=pos_hint,
        background_normal='',
        background_color=(1, 1, 1, 0),
        font_size=font_size,
        bold=True,
        color=(1, 1, 1, 1),
        halign='center',
        valign='middle'
    )
    
    with btn.canvas.before:
        Color(*bg_color)
        btn.rounded_rect = RoundedRectangle(
            pos=btn.pos,
            size=btn.size,
            radius=[25]
        )
    
    btn.bind(pos=lambda inst, val: setattr(inst.rounded_rect, 'pos', val))
    btn.bind(size=lambda inst, val: setattr(inst.rounded_rect, 'size', val))
    
    return btn
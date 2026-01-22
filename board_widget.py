import random
import math
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle
from kivy.clock import Clock

from state import GameState, board, REBIRTH, HAPPY, WATER, TRIPLE, DOUBLE, HORUS, NORMAL
from actions import available_moves
from particle import Particle
from egyptian_symbols import (draw_ankh_symbol, draw_eye_of_horus, 
                              draw_water_waves, draw_ankh_small)


class BoardWidget(FloatLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = None
        self.selected_rock = None
        self.available_moves_list = []
        self.human_player = None
        self.computer_player = None
        self.current_roll = None
        self.ai_depth = 3
        self.game_over = False
        self.cell_rects = []
        self.particles = []
        self.animation_running = False
        self.needs_redraw = False
        
        self.bind(size=self.on_size_change, pos=self.on_pos_change)
        
        Clock.schedule_interval(self.update_particles, 1/20)
    
    def on_size_change(self, *args):
        Clock.schedule_once(lambda dt: self.ensure_board_setup(), 0.01)
    
    def on_pos_change(self, *args):
        if self.state:
            self.calculate_cells()
            self.update_board()
    
    def ensure_board_setup(self):
        if self.state:
            self.calculate_cells()
            self.update_board()
    
    def setup_game(self, human_player, ai_depth):
        self.human_player = human_player
        self.computer_player = 2 if human_player == 1 else 1
        self.ai_depth = ai_depth
        self.state = GameState(
            player_1_rocks_pos=(1, 3, 5, 7, 9, 11, 13),
            player_2_rocks_pos=(0, 2, 4, 6, 8, 10, 12),
            current_player=human_player,
        )
        self.calculate_cells()
        self.update_board()
    
    def calculate_cells(self, *args):
        if self.width == 0 or self.height == 0:
            return
        
        margin = min(self.width, self.height) * 0.02
        available_width = self.width - (margin * 2)
        available_height = self.height * 0.6
        
        cell_size = min(available_width / 10, available_height / 3) * 0.85
        spacing = cell_size * 0.15
        
        board_width = 10 * (cell_size + spacing) - spacing
        board_height = 3 * (cell_size + spacing) - spacing
        start_x = (self.width - board_width) / 2
        start_y = (self.height - board_height) / 2 + self.height * 0.1
        
        self.cell_rects = []
        for i in range(30):
            if i < 10:
                row, col = 0, i
            elif i < 20:
                row, col = 1, 19 - i
            else:
                row, col = 2, i - 20
            
            x = start_x + col * (cell_size + spacing)
            y = start_y + (2 - row) * (cell_size + spacing)
            
            self.cell_rects.append({
                'x': x, 'y': y, 'size': cell_size,
                'center_x': x + cell_size/2,
                'center_y': y + cell_size/2,
                'index': i
            })
    
    def update_board(self, *args):
        if not self.cell_rects or not self.state:
            self.calculate_cells()
            if not self.cell_rects:
                return
        
        self.canvas.clear()
        
        with self.canvas:
            Color(0.95, 0.9, 0.75, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            for i in range(10):
                Color(0.9, 0.85, 0.7, 0.1)
                y_pos = self.y + random.uniform(0, self.height)
                Rectangle(pos=(self.x, y_pos), size=(self.width, 2))
            
            self._draw_cells()
            
            self._draw_pieces()
            
            for particle in self.particles:
                Color(*particle.color[:3], particle.life)
                Ellipse(
                    pos=(particle.x - particle.size/2, particle.y - particle.size/2),
                    size=(particle.size, particle.size)
                )
        
        self.canvas.ask_update()
        self.needs_redraw = False
    
    def _draw_cells(self):
        for rect in self.cell_rects:
            i = rect['index']
            
            # Cell background colors
            if board[i] == WATER:
                Color(0.2, 0.5, 0.8, 1)
            elif board[i] == REBIRTH:
                Color(0.9, 0.5, 0.2, 1)
            elif board[i] == HAPPY:
                Color(0.95, 0.8, 0.2, 1)
            elif board[i] in (TRIPLE, DOUBLE, HORUS):
                Color(0.6, 0.3, 0.7, 1)
            else:
                if i % 2 == 0:
                    Color(0.8, 0.65, 0.4, 1)
                else:
                    Color(0.7, 0.55, 0.3, 1)
            
            RoundedRectangle(
                pos=(rect['x'], rect['y']),
                size=(rect['size'], rect['size']),
                radius=[6]
            )
            
            Color(0.6, 0.4, 0.1, 1)
            Line(
                rounded_rectangle=(rect['x'], rect['y'], rect['size'], rect['size'], 6),
                width=3
            )
            
            Color(0.9, 0.7, 0.3, 0.5)
            Line(
                rounded_rectangle=(
                    rect['x']+3, rect['y']+3, 
                    rect['size']-6, rect['size']-6, 4
                ),
                width=1
            )
            
            self._draw_cell_icon(rect, i)
            
            self._highlight_available_moves(rect, i)
    
    def _draw_cell_icon(self, rect, index):
        if board[index] == WATER:
            draw_water_waves(self.canvas, rect['x'], rect['y'], rect['size'], (1, 1, 1, 0.8))
        elif board[index] == REBIRTH:
            draw_ankh_small(self.canvas, rect['x'], rect['y'], rect['size'], (1, 0.9, 0.7, 1))
        elif board[index] == HAPPY:
            draw_ankh_symbol(self.canvas, rect['x'], rect['y'], rect['size'], (0.3, 0.2, 0.1, 0.9))
        elif board[index] == HORUS:
            draw_eye_of_horus(self.canvas, rect['x'], rect['y'], rect['size'], (1, 0.9, 0.7, 1))
        elif board[index] in (TRIPLE, DOUBLE):
            num_bars = 3 if board[index] == TRIPLE else 2
            Color(1, 0.9, 0.7, 0.95)
            
            bar_width = rect['size'] * 0.08
            bar_height = rect['size'] * 0.5
            total_width = num_bars * bar_width + (num_bars - 1) * bar_width * 0.5
            start_x = rect['x'] + (rect['size'] - total_width) / 2
            start_y = rect['y'] + (rect['size'] - bar_height) / 2
            
            for j in range(num_bars):
                bar_x = start_x + j * (bar_width * 1.5)
                Rectangle(pos=(bar_x, start_y), size=(bar_width, bar_height))
    
    def _highlight_available_moves(self, rect, index):
        if self.selected_rock is not None:
            for old_pos, new_pos in self.available_moves_list:
                if old_pos == self.selected_rock and new_pos == index:
                    for glow_i in range(2):
                        Color(0.2, 1, 0.4, 0.15 - glow_i*0.05)
                        glow_size = rect['size'] + glow_i * 8
                        glow_offset = glow_i * 4
                        RoundedRectangle(
                            pos=(rect['x'] - glow_offset, rect['y'] - glow_offset),
                            size=(glow_size, glow_size),
                            radius=[8]
                        )
                    Color(0.2, 1, 0.4, 1)
                    Line(
                        rounded_rectangle=(rect['x'], rect['y'], rect['size'], rect['size'], 6),
                        width=4
                    )
    
    def _draw_pieces(self):
        if not self.state:
            return
        
        piece_size = self.cell_rects[0]['size'] * 0.55
        
        for pos in self.state.player_1_rocks_pos:
            if pos < 30:
                self._draw_piece(pos, piece_size, is_player1=True)
        
        for pos in self.state.player_2_rocks_pos:
            if pos < 30:
                self._draw_piece(pos, piece_size, is_player1=False)
    
    def _draw_piece(self, pos, piece_size, is_player1):
        rect = self.cell_rects[pos]
        
        if self.selected_rock == pos:
            glow_color = (1, 0.6, 0.2) if is_player1 else (0.3, 0.6, 1)
            for i in range(2):
                Color(*glow_color, 0.2 - i*0.08)
                glow_size = piece_size + (i * 12)
                Ellipse(
                    pos=(rect['center_x'] - glow_size/2, rect['center_y'] - glow_size/2),
                    size=(glow_size, glow_size)
                )
        
        Color(0, 0, 0, 0.4)
        Ellipse(
            pos=(rect['center_x'] - piece_size/2 + 4, rect['center_y'] - piece_size/2 - 4),
            size=(piece_size, piece_size)
        )
        
        if is_player1:
            Color(0.7, 0.2, 0.1, 1)
            Ellipse(
                pos=(rect['center_x'] - piece_size/2, rect['center_y'] - piece_size/2),
                size=(piece_size, piece_size)
            )
            Color(0.95, 0.3, 0.15, 1)
            Ellipse(
                pos=(rect['center_x'] - piece_size*0.4, rect['center_y'] - piece_size*0.4),
                size=(piece_size*0.8, piece_size*0.8)
            )
            Color(1, 0.7, 0.5, 0.9)
            Ellipse(
                pos=(rect['center_x'] - piece_size*0.25, rect['center_y'] - piece_size*0.15),
                size=(piece_size*0.35, piece_size*0.35)
            )
            Color(1, 0.84, 0, 1)
            Line(circle=(rect['center_x'], rect['center_y'], piece_size/2), width=3)
            Color(0.8, 0.6, 0.2, 0.6)
            Line(circle=(rect['center_x'], rect['center_y'], piece_size/2.5), width=1.5)
        else:
            Color(0.15, 0.35, 0.6, 1)
            Ellipse(
                pos=(rect['center_x'] - piece_size/2, rect['center_y'] - piece_size/2),
                size=(piece_size, piece_size)
            )
            Color(0.25, 0.55, 0.9, 1)
            Ellipse(
                pos=(rect['center_x'] - piece_size*0.4, rect['center_y'] - piece_size*0.4),
                size=(piece_size*0.8, piece_size*0.8)
            )
            Color(0.6, 0.85, 1, 0.9)
            Ellipse(
                pos=(rect['center_x'] - piece_size*0.25, rect['center_y'] - piece_size*0.15),
                size=(piece_size*0.35, piece_size*0.35)
            )
            Color(0.8, 0.85, 0.9, 1)
            Line(circle=(rect['center_x'], rect['center_y'], piece_size/2), width=3)
            Color(0.6, 0.65, 0.7, 0.6)
            Line(circle=(rect['center_x'], rect['center_y'], piece_size/2.5), width=1.5)
    
    def create_particles(self, x, y, color, count=10):
        """Create particle explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, color, vx, vy))
    
    def update_particles(self, dt):
        """Update particle positions"""
        self.particles = [p for p in self.particles if p.update(dt)]
        if self.particles or self.needs_redraw:
            self.update_board()
    
    def animate_piece_move(self, from_pos, to_pos, callback):
        """Smooth piece movement animation"""
        if from_pos >= len(self.cell_rects):
            callback()
            return

        self.animation_running = True

        from_rect = self.cell_rects[from_pos]
        if to_pos < len(self.cell_rects):
            to_rect = self.cell_rects[to_pos]

            if self.state.current_player == 1:
                color = (0.95, 0.3, 0.15, 1)
            else:
                color = (0.25, 0.55, 0.9, 1)

            self.create_particles(from_rect['center_x'], from_rect['center_y'], color, 5)

            Clock.schedule_once(lambda dt: self.create_particles(
                to_rect['center_x'], to_rect['center_y'], (1, 1, 0.5, 1), 10
            ), 0.1)

        Clock.schedule_once(lambda dt: self.finish_animation(callback), 0.1)
    
    def finish_animation(self, callback):
        """Finish animation and call callback"""
        self.animation_running = False
        callback()
    
    def on_touch_down(self, touch):
        if self.game_over or not self.state or self.animation_running:
            return super().on_touch_down(touch)

        app_instance = App.get_running_app()
        is_current_player_human = False

        if hasattr(app_instance, 'is_two_player_mode') and app_instance.is_two_player_mode:
            is_current_player_human = True
        else:
            is_current_player_human = (self.state.current_player == app_instance.human_player)

        if not is_current_player_human or self.current_roll is None:
            return super().on_touch_down(touch)
        
        for rect in self.cell_rects:
            if (rect['x'] <= touch.x <= rect['x'] + rect['size'] and
                rect['y'] <= touch.y <= rect['y'] + rect['size']):
                
                i = rect['index']
                positions = (self.state.player_1_rocks_pos if self.state.current_player == 1
                           else self.state.player_2_rocks_pos)
                
                if i in positions:
                    self.selected_rock = i
                    self.available_moves_list = [(old_pos, new_pos) for old_pos, new_pos in
                                                available_moves(self.state, self.current_roll)
                                                if old_pos == i]
                    color = (0.95, 0.3, 0.15, 1) if self.state.current_player == 1 else (0.25, 0.55, 0.9, 1)
                    self.create_particles(rect['center_x'], rect['center_y'], color, 5)
                    self.update_board()
                    break
        
        return super().on_touch_down(touch)
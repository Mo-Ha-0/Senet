from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle, Triangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty
import random
import math

from state import GameState, board, REBIRTH, HAPPY, WATER, TRIPLE, DOUBLE, HORUS, NORMAL
from actions import number_of_steps, available_moves, apply_move_lists, handle_rebirth
from ai import get_best_move_expectiminimax


class Particle:
    """Particle for visual effects"""
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 1.0
        self.size = random.uniform(3, 8)
        
    def update(self, dt):
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        self.velocity_y -= 200 * dt  # Gravity
        self.life -= dt * 2
        return self.life > 0


class BoardWidget(FloatLayout):
    """Enhanced board with Egyptian icons and animations"""
    
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
        
        # Bind events
        self.bind(size=self.on_size_change, pos=self.on_pos_change)
        
        # Start particle update loop
        Clock.schedule_interval(self.update_particles, 1/30)
    
    def on_size_change(self, *args):
        Clock.schedule_once(lambda dt: self.ensure_board_setup(), 0.01)
    
    def on_pos_change(self, *args):
        if self.state and self.cell_rects:
            Clock.schedule_once(lambda dt: self.update_board(), 0.01)
    
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
        Clock.schedule_once(lambda dt: self.update_board(), 0.1)
    
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
    
    def draw_ankh_symbol(self, x, y, size, color_tuple):
        """Draw Egyptian Ankh symbol"""
        Color(*color_tuple)
        # Circle (top)
        Ellipse(pos=(x + size*0.35, y + size*0.6), size=(size*0.3, size*0.3))
        # Vertical line
        Rectangle(pos=(x + size*0.45, y + size*0.1), size=(size*0.1, size*0.65))
        # Horizontal line
        Rectangle(pos=(x + size*0.25, y + size*0.45), size=(size*0.5, size*0.08))
    
    def draw_eye_of_horus(self, x, y, size, color_tuple):
        """Draw Eye of Horus symbol"""
        Color(*color_tuple)
        # Main eye shape
        Line(points=[
            x + size*0.2, y + size*0.5,
            x + size*0.5, y + size*0.7,
            x + size*0.8, y + size*0.5,
            x + size*0.5, y + size*0.3,
            x + size*0.2, y + size*0.5
        ], width=2)
        # Pupil
        Ellipse(pos=(x + size*0.45, y + size*0.45), size=(size*0.1, size*0.1))
        # Spiral detail
        Line(points=[
            x + size*0.5, y + size*0.3,
            x + size*0.6, y + size*0.2,
            x + size*0.5, y + size*0.1
        ], width=1.5)
    
    def draw_water_waves(self, x, y, size, color_tuple):
        """Draw water wave symbols"""
        Color(*color_tuple)
        for i in range(3):
            y_offset = y + size*0.25 + i*size*0.25
            points = []
            for j in range(5):
                wave_x = x + size*0.2 + j*size*0.15
                wave_y = y_offset + math.sin(j) * size*0.1
                points.extend([wave_x, wave_y])
            Line(points=points, width=2)
    
    def draw_ankh_small(self, x, y, size, color_tuple):
        """Draw small Ankh for rebirth"""
        Color(*color_tuple)
        # Simplified ankh
        Ellipse(pos=(x + size*0.4, y + size*0.65), size=(size*0.2, size*0.2))
        Rectangle(pos=(x + size*0.47, y + size*0.2), size=(size*0.06, size*0.5))
        Rectangle(pos=(x + size*0.3, y + size*0.55), size=(size*0.4, size*0.06))
    
    def update_board(self, *args):
        if not self.cell_rects or not self.state:
            self.calculate_cells()
            if not self.cell_rects:
                return
        
        self.canvas.clear()
        
        with self.canvas:
            # Papyrus-like background
            Color(0.95, 0.9, 0.75, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Add texture effect
            for i in range(20):
                Color(0.9, 0.85, 0.7, 0.1)
                y_pos = self.y + random.uniform(0, self.height)
                Rectangle(pos=(self.x, y_pos), size=(self.width, 2))
            
            # Draw cells with Egyptian styling
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
                
                # Main cell
                RoundedRectangle(
                    pos=(rect['x'], rect['y']),
                    size=(rect['size'], rect['size']),
                    radius=[6]
                )
                
                # Ornate border
                Color(0.6, 0.4, 0.1, 1)
                Line(
                    rounded_rectangle=(rect['x'], rect['y'], rect['size'], rect['size'], 6),
                    width=3
                )
                
                # Inner decorative border
                Color(0.9, 0.7, 0.3, 0.5)
                Line(
                    rounded_rectangle=(
                        rect['x']+3, rect['y']+3, 
                        rect['size']-6, rect['size']-6, 4
                    ),
                    width=1
                )
                
                # Draw icons for special squares
                if board[i] == WATER:
                    self.draw_water_waves(rect['x'], rect['y'], rect['size'], (1, 1, 1, 0.8))
                elif board[i] == REBIRTH:
                    self.draw_ankh_small(rect['x'], rect['y'], rect['size'], (1, 0.9, 0.7, 1))
                elif board[i] == HAPPY:
                    self.draw_ankh_symbol(rect['x'], rect['y'], rect['size'], (0.3, 0.2, 0.1, 0.9))
                elif board[i] == HORUS:
                    self.draw_eye_of_horus(rect['x'], rect['y'], rect['size'], (1, 0.9, 0.7, 1))
                elif board[i] in (TRIPLE, DOUBLE):
                    # Draw vertical bars instead of stars
                    num_bars = 3 if board[i] == TRIPLE else 2
                    Color(1, 0.9, 0.7, 0.95)
                    
                    bar_width = rect['size'] * 0.08
                    bar_height = rect['size'] * 0.5
                    total_width = num_bars * bar_width + (num_bars - 1) * bar_width * 0.5
                    start_x = rect['x'] + (rect['size'] - total_width) / 2
                    start_y = rect['y'] + (rect['size'] - bar_height) / 2
                    
                    for j in range(num_bars):
                        bar_x = start_x + j * (bar_width * 1.5)
                        Rectangle(pos=(bar_x, start_y), size=(bar_width, bar_height))
                
                # Highlight available moves with glow
                if self.selected_rock is not None:
                    for old_pos, new_pos in self.available_moves_list:
                        if old_pos == self.selected_rock and new_pos == i:
                            # Glowing highlight
                            for glow_i in range(3):
                                Color(0.2, 1, 0.4, 0.15 - glow_i*0.04)
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
            
            # Draw pieces with enhanced 3D effect
            if self.state:
                piece_size = self.cell_rects[0]['size'] * 0.55
                
                # Player 1 pieces (Red/Gold - Egyptian style)
                for pos in self.state.player_1_rocks_pos:
                    if pos < 30:
                        rect = self.cell_rects[pos]
                        
                        # Glow for selected piece
                        if self.selected_rock == pos:
                            for i in range(4):
                                Color(1, 0.6, 0.2, 0.2 - i*0.04)
                                glow_size = piece_size + (i * 12)
                                Ellipse(
                                    pos=(rect['center_x'] - glow_size/2, rect['center_y'] - glow_size/2),
                                    size=(glow_size, glow_size)
                                )
                        
                        # Large shadow
                        Color(0, 0, 0, 0.4)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size/2 + 4, rect['center_y'] - piece_size/2 - 4),
                            size=(piece_size, piece_size)
                        )
                        
                        # Gradient effect - dark base
                        Color(0.7, 0.2, 0.1, 1)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size/2, rect['center_y'] - piece_size/2),
                            size=(piece_size, piece_size)
                        )
                        
                        # Middle layer
                        Color(0.95, 0.3, 0.15, 1)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size*0.4, rect['center_y'] - piece_size*0.4),
                            size=(piece_size*0.8, piece_size*0.8)
                        )
                        
                        # Bright highlight
                        Color(1, 0.7, 0.5, 0.9)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size*0.25, rect['center_y'] - piece_size*0.15),
                            size=(piece_size*0.35, piece_size*0.35)
                        )
                        
                        # Gold rim
                        Color(1, 0.84, 0, 1)
                        Line(circle=(rect['center_x'], rect['center_y'], piece_size/2), width=3)
                        
                        # Inner decorative circle
                        Color(0.8, 0.6, 0.2, 0.6)
                        Line(circle=(rect['center_x'], rect['center_y'], piece_size/2.5), width=1.5)
                
                # Player 2 pieces (Blue/Silver - Egyptian style)
                for pos in self.state.player_2_rocks_pos:
                    if pos < 30:
                        rect = self.cell_rects[pos]
                        
                        # Glow for selected piece
                        if self.selected_rock == pos:
                            for i in range(4):
                                Color(0.3, 0.6, 1, 0.2 - i*0.04)
                                glow_size = piece_size + (i * 12)
                                Ellipse(
                                    pos=(rect['center_x'] - glow_size/2, rect['center_y'] - glow_size/2),
                                    size=(glow_size, glow_size)
                                )
                        
                        # Large shadow
                        Color(0, 0, 0, 0.4)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size/2 + 4, rect['center_y'] - piece_size/2 - 4),
                            size=(piece_size, piece_size)
                        )
                        
                        # Gradient effect - dark base
                        Color(0.15, 0.35, 0.6, 1)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size/2, rect['center_y'] - piece_size/2),
                            size=(piece_size, piece_size)
                        )
                        
                        # Middle layer
                        Color(0.25, 0.55, 0.9, 1)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size*0.4, rect['center_y'] - piece_size*0.4),
                            size=(piece_size*0.8, piece_size*0.8)
                        )
                        
                        # Bright highlight
                        Color(0.6, 0.85, 1, 0.9)
                        Ellipse(
                            pos=(rect['center_x'] - piece_size*0.25, rect['center_y'] - piece_size*0.15),
                            size=(piece_size*0.35, piece_size*0.35)
                        )
                        
                        # Silver rim
                        Color(0.8, 0.85, 0.9, 1)
                        Line(circle=(rect['center_x'], rect['center_y'], piece_size/2), width=3)
                        
                        # Inner decorative circle
                        Color(0.6, 0.65, 0.7, 0.6)
                        Line(circle=(rect['center_x'], rect['center_y'], piece_size/2.5), width=1.5)
            
            # Draw particles
            for particle in self.particles:
                Color(*particle.color[:3], particle.life)
                Ellipse(
                    pos=(particle.x - particle.size/2, particle.y - particle.size/2),
                    size=(particle.size, particle.size)
                )
        
        self.canvas.ask_update()
    
    def create_particles(self, x, y, color, count=15):
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
        if self.particles:
            self.update_board()
    
    def animate_piece_move(self, from_pos, to_pos, callback):
        """Smooth piece movement animation"""
        if from_pos >= len(self.cell_rects):
            callback()
            return
        
        self.animation_running = True
        
        # Create particle trail effect
        from_rect = self.cell_rects[from_pos]
        if to_pos < len(self.cell_rects):
            to_rect = self.cell_rects[to_pos]
            
            # Particle color based on current player
            if self.state.current_player == 1:
                color = (0.95, 0.3, 0.15, 1)
            else:
                color = (0.25, 0.55, 0.9, 1)
            
            # Create trail particles
            self.create_particles(from_rect['center_x'], from_rect['center_y'], color, 10)
            
            # Flash at destination
            Clock.schedule_once(lambda dt: self.create_particles(
                to_rect['center_x'], to_rect['center_y'], (1, 1, 0.5, 1), 20
            ), 0.3)
        
        Clock.schedule_once(lambda dt: self.finish_animation(callback), 0.4)
    
    def finish_animation(self, callback):
        """Finish animation and call callback"""
        self.animation_running = False
        callback()
    
    def on_touch_down(self, touch):
        if self.game_over or not self.state or self.animation_running:
            return super().on_touch_down(touch)
        
        if self.state.current_player != self.human_player or self.current_roll is None:
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
                    # Particle burst on selection
                    color = (0.95, 0.3, 0.15, 1) if self.state.current_player == 1 else (0.25, 0.55, 0.9, 1)
                    self.create_particles(rect['center_x'], rect['center_y'], color, 8)
                    self.update_board()
                    break
        
        return super().on_touch_down(touch)


class SenetApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.08, 0.06, 1)
        self.main_layout = FloatLayout()
        self.show_start_screen()
        return self.main_layout
    
    def show_start_screen(self):
        self.main_layout.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Clean title without symbols
        title = Label(
            text='[b][color=FFD700]SENET[/color][/b]\n[size=20][color=D4AF37]Ancient Egyptian Game of Passage[/color][/size]',
            markup=True,
            size_hint=(1, 0.3),
            font_size='48sp'
        )
        layout.add_widget(title)
        
        btn_player1 = Button(
            text='Play as RED',
            size_hint=(1, 0.15),
            background_color=(0.95, 0.3, 0.25, 1),
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        btn_player1.bind(on_press=lambda x: self.select_player(1))
        
        btn_player2 = Button(
            text='Play as BLUE',
            size_hint=(1, 0.15),
            background_color=(0.25, 0.55, 0.9, 1),
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        btn_player2.bind(on_press=lambda x: self.select_player(2))
        
        layout.add_widget(btn_player1)
        layout.add_widget(btn_player2)
        
        instructions = Label(
            text='- Tap piece to select\n- Tap glowing square to move\n- First to remove all pieces wins',
            size_hint=(1, 0.2),
            font_size='18sp',
            color=(0.9, 0.85, 0.7, 1)
        )
        layout.add_widget(instructions)
        
        self.main_layout.add_widget(layout)
    
    def select_player(self, player):
        self.human_player = player
        self.computer_player = 2 if player == 1 else 1
        self.show_difficulty_screen()
    
    def show_difficulty_screen(self):
        self.main_layout.clear_widgets()
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        title = Label(
            text='[b][color=FFD700]Select Difficulty[/color][/b]',
            markup=True,
            font_size='40sp',
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        
        difficulties = [
            ('very Easy', 1, (0.1, 0.5, 0.3, 1)),
            ('Easy', 2, (0.2, 0.8, 0.4, 1)),
            ('Medium', 3, (0.95, 0.8, 0.2, 1)),
            ('Hard', 4, (0.95, 0.3, 0.25, 1)),
            ('Expert', 5, (0.6, 0.1, 0.1, 1))
        ]
        
        for name, depth, color in difficulties:
            btn = Button(
                text=name,
                size_hint=(1, 0.15),
                background_color=color,
                font_size='24sp',
                bold=True
            )
            btn.bind(on_press=lambda x, d=depth: self.start_game(d))
            layout.add_widget(btn)
        
        self.main_layout.add_widget(layout)
    
    def start_game(self, depth):
        self.ai_depth = depth
        self.main_layout.clear_widgets()
        
        game_layout = BoxLayout(orientation='vertical')
        
        self.status_label = Label(
            text='[b]Tap ROLL to begin![/b]',
            markup=True,
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(1, 0.95, 0.7, 1)
        )
        game_layout.add_widget(self.status_label)
        
        self.board_widget = BoardWidget(size_hint=(1, 0.7))
        game_layout.add_widget(self.board_widget)
        self.board_widget.setup_game(self.human_player, self.ai_depth)
        Clock.schedule_once(lambda dt: self.board_widget.update_board(), 0.1)
        
        control_panel = BoxLayout(size_hint=(1, 0.22), spacing=10, padding=10)
        
        self.roll_button = Button(
            text='ROLL DICE',
            background_color=(0.95, 0.8, 0.2, 1),
            font_size='24sp',
            bold=True,
            color=(0.3, 0.2, 0.1, 1)
        )
        self.roll_button.bind(on_press=self.roll_dice)
        control_panel.add_widget(self.roll_button)
        
        self.dice_label = Label(
            text='',
            font_size='48sp',
            bold=True,
            color=(1, 0.9, 0.5, 1)
        )
        control_panel.add_widget(self.dice_label)
        
        btn_restart = Button(
            text='RESTART',
            background_color=(0.7, 0.3, 0.3, 1),
            font_size='20sp',
            bold=True
        )
        btn_restart.bind(on_press=lambda x: self.show_start_screen())
        control_panel.add_widget(btn_restart)
        
        game_layout.add_widget(control_panel)
        self.main_layout.add_widget(game_layout)
        
        if self.board_widget.state.current_player == self.computer_player:
            Clock.schedule_once(lambda dt: self.computer_turn(), 1)
    
    def roll_dice(self, instance):
        if (self.board_widget.game_over or 
            self.board_widget.state.current_player != self.human_player or
            self.board_widget.current_roll is not None):
            return
        
        # Animated dice roll
        self.dice_label.text = 'Rolling...'
        self.animate_dice_roll(0, lambda: None)
    
    def animate_dice_roll(self, count, callback):
        """Animated dice rolling effect"""
        if count < 5:
            self.dice_label.text = f'{random.randint(1, 5)}'
            Clock.schedule_once(lambda dt: self.animate_dice_roll(count + 1, callback), 0.1)
        else:
            roll = number_of_steps()
            self.board_widget.current_roll = roll
            self.dice_label.text = f'{roll}'
            
            moves = available_moves(self.board_widget.state, roll)
            self.board_widget.available_moves_list = moves
            
            if not moves:
                self.status_label.text = f'[b]Rolled {roll} - No moves![/b]'
                Clock.schedule_once(lambda dt: self.skip_turn(), 1.5)
            else:
                self.status_label.text = f'[b]Rolled {roll} - Select your piece[/b]'
                self.board_widget.bind(on_touch_down=self.handle_move_selection)
    
    def handle_move_selection(self, widget, touch):
        for old_pos, new_pos in widget.available_moves_list:
            if old_pos == widget.selected_rock:
                is_valid_click = False
                
                if new_pos >= len(board):
                    is_valid_click = True
                else:
                    for rect in widget.cell_rects:
                        if rect['index'] == new_pos:
                            if (rect['x'] <= touch.x <= rect['x'] + rect['size'] and
                                rect['y'] <= touch.y <= rect['y'] + rect['size']):
                                is_valid_click = True
                                break
                
                if is_valid_click:
                    widget.unbind(on_touch_down=self.handle_move_selection)
                    
                    def execute_move():
                        player_1_rocks_pos, player_1_rocks, player_2_rocks_pos, player_2_rocks, rock_idx = \
                            apply_move_lists(widget.state, (old_pos, new_pos))
                        
                        if widget.state.current_player == 1:
                            player_1_rocks_pos, player_1_rocks = handle_rebirth(
                                player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx
                            )
                        else:
                            player_2_rocks_pos, player_2_rocks = handle_rebirth(
                                player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx
                            )
                        
                        widget.state = GameState(
                            player_1_rocks_pos=tuple(player_1_rocks_pos),
                            player_2_rocks_pos=tuple(player_2_rocks_pos),
                            current_player=2 if widget.state.current_player == 1 else 1,
                        )
                        
                        widget.current_roll = None
                        widget.selected_rock = None
                        widget.available_moves_list = []
                        widget.update_board()
                        
                        if widget.state.is_terminal():
                            self.handle_game_over(widget.state.winner())
                        else:
                            self.dice_label.text = ''
                            if widget.state.current_player == self.computer_player:
                                Clock.schedule_once(lambda dt: self.computer_turn(), 1)
                            else:
                                self.status_label.text = '[b]Your turn - Tap ROLL[/b]'
                    
                    widget.animate_piece_move(old_pos, new_pos, execute_move)
                    return
    
    def skip_turn(self):
        self.board_widget.state = GameState(
            player_1_rocks_pos=self.board_widget.state.player_1_rocks_pos,
            player_2_rocks_pos=self.board_widget.state.player_2_rocks_pos,
            current_player=2 if self.board_widget.state.current_player == 1 else 1,
        )
        self.board_widget.current_roll = None
        self.dice_label.text = ''
        
        if self.board_widget.state.current_player == self.computer_player:
            Clock.schedule_once(lambda dt: self.computer_turn(), 1)
        else:
            self.status_label.text = '[b]Your turn - Tap ROLL[/b]'
    
    def computer_turn(self):
        if self.board_widget.game_over:
            return
        
        self.roll_button.disabled = True
        
        # Animated computer dice roll
        self.animate_dice_roll(0, lambda: None)
        Clock.schedule_once(lambda dt: self.computer_roll_complete(), 0.6)
    
    def computer_roll_complete(self):
        roll = number_of_steps()
        self.board_widget.current_roll = roll
        self.dice_label.text = f'{roll}'
        self.status_label.text = f'[b]Computer rolled {roll}[/b]'
        
        moves = available_moves(self.board_widget.state, roll)
        
        if not moves:
            self.status_label.text = f'[b]Computer rolled {roll} - No moves![/b]'
            Clock.schedule_once(lambda dt: self.skip_turn(), 1.5)
            return
        
        self.status_label.text = '[b]Computer thinking...[/b]'
        Clock.schedule_once(lambda dt: self.execute_computer_move(roll), 1)
    
    def execute_computer_move(self, roll):
        best_move, nodes, score = get_best_move_expectiminimax(
            self.board_widget.state, roll, depth=self.ai_depth, reporting=False
        )
        
        if best_move:
            old_pos, new_pos = best_move
            
            def complete_computer_move():
                player_1_rocks_pos, player_1_rocks, player_2_rocks_pos, player_2_rocks, rock_idx = \
                    apply_move_lists(self.board_widget.state, best_move)
                
                if self.board_widget.state.current_player == 1:
                    player_1_rocks_pos, player_1_rocks = handle_rebirth(
                        player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx
                    )
                else:
                    player_2_rocks_pos, player_2_rocks = handle_rebirth(
                        player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx
                    )
                
                self.board_widget.state = GameState(
                    player_1_rocks_pos=tuple(player_1_rocks_pos),
                    player_2_rocks_pos=tuple(player_2_rocks_pos),
                    current_player=2 if self.board_widget.state.current_player == 1 else 1,
                )
                
                self.board_widget.current_roll = None
                self.board_widget.update_board()
                
                if self.board_widget.state.is_terminal():
                    self.handle_game_over(self.board_widget.state.winner())
                else:
                    self.dice_label.text = ''
                    self.status_label.text = '[b]Your turn - Tap ROLL[/b]'
                    self.roll_button.disabled = False
            
            self.board_widget.animate_piece_move(old_pos, new_pos, complete_computer_move)
        else:
            Clock.schedule_once(lambda dt: self.skip_turn(), 1)
    
    def handle_game_over(self, winner):
        if winner == self.human_player:
            self.status_label.text = '[b][color=FFD700]VICTORY! YOU WIN![/color][/b]'
        else:
            self.status_label.text = '[b][color=FF6B6B]Computer Wins![/color][/b]'
        
        self.board_widget.game_over = True
        self.roll_button.disabled = True
        self.roll_button.background_color = (0.5, 0.5, 0.5, 1)


if __name__ == '__main__':
    SenetApp().run()
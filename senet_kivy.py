import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window

# Import the game logic modules
from state import GameState, board
from actions import number_of_steps, available_moves, apply_move_lists, handle_rebirth
from ai import get_best_move_expectiminimax
from state import DOUBLE, REBIRTH, HAPPY, WATER, TRIPLE, HORUS, NORMAL


class SenetBoardWidget(Widget):
    def __init__(self, **kwargs):
        super(SenetBoardWidget, self).__init__(**kwargs)
        self.state = None
        self.human_player = 1
        self.computer_player = 2
        self.ai_depth = 3
        self.current_roll = None
        self.available_moves_list = []
        self.selected_rock = None
        self.thinking = False
        self.game_over = False
        self.message_label = None
        
        # Bind to redraw when size changes
        self.bind(size=self.redraw, pos=self.redraw)
        
    def set_message_label(self, label):
        self.message_label = label
        
    def set_game_state(self, state):
        self.state = state
        self.redraw()
        
    def redraw(self, *args):
        self.canvas.clear()
        if self.state:
            self.draw_board()
            self.draw_pieces()
            
    def draw_board(self):
        if not self.state:
            return
            
        # Calculate cell dimensions based on widget size
        if self.width == 0 or self.height == 0:
            return  # Widget hasn't been sized yet
            
        cell_width = self.width / 10
        cell_height = self.height / 3
        
        with self.canvas:
            # Draw the 3 rows of the board
            for i in range(30):
                if 0 <= i < 10:
                    row = 0
                    col = i
                elif 10 <= i < 20:
                    row = 1
                    col = 19 - i
                else:
                    row = 2
                    col = i - 20
                
                x = self.x + col * cell_width
                y = self.y + (2 - row) * cell_height  # Flip row order
                
                # Determine cell color based on type
                if board[i] == WATER:
                    Color(0.2, 0.4, 0.7)  # Blue for water
                elif board[i] == REBIRTH:
                    Color(0.8, 0.4, 0.2)  # Orange for rebirth
                elif board[i] == HAPPY:
                    Color(0.9, 0.8, 0.2)  # Yellow for happy
                elif board[i] == TRIPLE:
                    Color(0.6, 0.3, 0.8)  # Purple for triple
                elif board[i] == DOUBLE:
                    Color(0.6, 0.3, 0.8)  # Purple for double
                elif board[i] == HORUS:
                    Color(0.6, 0.3, 0.8)  # Purple for horus
                else:
                    # Alternating colors for normal cells
                    if (row + col) % 2 == 0:
                        Color(0.8, 0.7, 0.5)  # Light wood
                    else:
                        Color(0.6, 0.4, 0.2)  # Dark wood
                
                # Draw cell
                Rectangle(pos=(x, y), size=(cell_width, cell_height))
                
                # Draw border
                Color(0.3, 0.2, 0.1)  # Dark brown border
                Line(rectangle=(x, y, cell_width, cell_height), width=2)
                
    def draw_pieces(self):
        if not self.state:
            return
            
        if self.width == 0 or self.height == 0:
            return  # Widget hasn't been sized yet
            
        cell_width = self.width / 10
        cell_height = self.height / 3
        
        # Draw Player 1 pieces (red)
        for pos in self.state.player_1_rocks_pos:
            if 0 <= pos < 10:
                row = 0
                col = pos
            elif 10 <= pos < 20:
                row = 1
                col = 19 - pos
            else:
                row = 2
                col = pos - 20
            
            x = self.x + col * cell_width + cell_width/2
            y = self.y + (2 - row) * cell_height + cell_height/2
            
            with self.canvas:
                Color(0.8, 0.2, 0.2)  # Red
                Ellipse(pos=(x-15, y-15), size=(30, 30))
                Color(0.5, 0.1, 0.1)  # Darker red border
                Line(circle=(x, y, 15), width=2)
        
        # Draw Player 2 pieces (blue)
        for pos in self.state.player_2_rocks_pos:
            if 0 <= pos < 10:
                row = 0
                col = pos
            elif 10 <= pos < 20:
                row = 1
                col = 19 - pos
            else:
                row = 2
                col = pos - 20
            
            x = self.x + col * cell_width + cell_width/2
            y = self.y + (2 - row) * cell_height + cell_height/2
            
            with self.canvas:
                Color(0.2, 0.5, 0.8)  # Blue
                Ellipse(pos=(x-15, y-15), size=(30, 30))
                Color(0.1, 0.3, 0.5)  # Darker blue border
                Line(circle=(x, y, 15), width=2)
                
    def on_touch_down(self, touch):
        if self.game_over or self.thinking:
            return False
            
        if not self.collide_point(*touch.pos):
            return False
            
        if not self.state:
            return False
            
        # Calculate which cell was touched
        if self.width == 0 or self.height == 0:
            return False  # Widget hasn't been sized yet
            
        cell_width = self.width / 10
        cell_height = self.height / 3
        
        # Convert touch position to board coordinates
        rel_x = touch.x - self.x
        rel_y = touch.y - self.y
        
        # Determine which row and column
        row = 2 - int(rel_y / cell_height)  # Flip row order
        col = int(rel_x / cell_width)
        
        # Convert to board position
        pos = -1
        if row == 0 and 0 <= col <= 9:
            pos = col
        elif row == 1 and 0 <= col <= 9:
            pos = 19 - col
        elif row == 2 and 0 <= col <= 9:
            pos = 20 + col
        
        if pos != -1:
            # Check if it's a player's rock
            if self.state.current_player == 1 and pos in self.state.player_1_rocks_pos:
                self.selected_rock = pos
                if self.message_label:
                    self.message_label.text = f"Selected rock at position {pos}"
            elif self.state.current_player == 2 and pos in self.state.player_2_rocks_pos:
                self.selected_rock = pos
                if self.message_label:
                    self.message_label.text = f"Selected rock at position {pos}"
            elif self.selected_rock is not None:
                # Try to make a move
                for old_pos, new_pos in self.available_moves_list:
                    if old_pos == self.selected_rock and new_pos == pos:
                        self.make_move((old_pos, new_pos))
                        break
        return True
        
    def roll_dice(self):
        """Roll the dice for the current player"""
        self.current_roll = number_of_steps()
        if self.message_label:
            self.message_label.text = f"Rolled {self.current_roll} steps"
        
        self.available_moves_list = available_moves(self.state, self.current_roll)
        
        if not self.available_moves_list:
            if self.message_label:
                self.message_label.text = f"No moves available after rolling {self.current_roll}"
            Clock.schedule_once(self.switch_player, 1.5)  # Switch after delay
        else:
            if self.message_label:
                self.message_label.text = f"Rolled {self.current_roll}. Select a piece to move."
        
        self.redraw()
        
    def switch_player(self, dt):
        """Switch to the next player"""
        if self.state:
            new_current_player = 2 if self.state.current_player == 1 else 1
            self.state = GameState(
                player_1_rocks_pos=self.state.player_1_rocks_pos,
                player_2_rocks_pos=self.state.player_2_rocks_pos,
                current_player=new_current_player
            )
            
            if self.state.current_player == self.computer_player:
                if self.message_label:
                    self.message_label.text = "Computer's turn..."
                Clock.schedule_once(self.computer_turn, 1.0)
            else:
                if self.message_label:
                    self.message_label.text = "Your turn. Press ROLL to play."
        
        self.redraw()
        
    def computer_turn(self, dt):
        """Process computer's turn"""
        if self.state and self.state.current_player == self.computer_player:
            self.thinking = True
            if self.message_label:
                self.message_label.text = "Computer is thinking..."
            
            # Roll dice for computer
            self.current_roll = number_of_steps()
            if self.message_label:
                self.message_label.text = f"Computer rolled {self.current_roll}"
            
            moves = available_moves(self.state, self.current_roll)
            
            if not moves:
                Clock.schedule_once(self.switch_player, 1.5)
            else:
                # Find best move using AI
                best_move, nodes, score = get_best_move_expectiminimax(
                    self.state, self.current_roll, depth=self.ai_depth, reporting=False
                )
                
                if best_move:
                    Clock.schedule_once(lambda dt: self.make_move(best_move), 1.0)
                else:
                    Clock.schedule_once(self.switch_player, 1.5)
                    
    def make_move(self, move):
        """Execute a move"""
        if not move or not self.state:
            return
            
        old_pos, new_pos = move
        
        # Apply the move
        (player_1_rocks_pos_new, player_1_rocks_new, 
         player_2_rocks_pos_new, player_2_rocks_new, rock_idx) = apply_move_lists(self.state, move)

        if self.state.current_player == 1:
            player_1_rocks_pos_new, player_1_rocks_new = handle_rebirth(
                player_1_rocks_pos_new, player_1_rocks_new, player_2_rocks_new, rock_idx
            )
        else:
            player_2_rocks_pos_new, player_2_rocks_new = handle_rebirth(
                player_2_rocks_pos_new, player_2_rocks_new, player_1_rocks_new, rock_idx
            )

        # Update state
        self.state = GameState(
            player_1_rocks_pos=tuple(player_1_rocks_pos_new),
            player_2_rocks_pos=tuple(player_2_rocks_pos_new),
            current_player=2 if self.state.current_player == 1 else 1,
        )
        
        # Reset selection
        self.selected_rock = None
        self.current_roll = None
        self.available_moves_list = []
        
        # Check for game over
        if self.state.is_terminal():
            winner = self.state.winner()
            self.game_over = True
            if winner == self.human_player:
                if self.message_label:
                    self.message_label.text = "Congratulations! You won!"
            else:
                if self.message_label:
                    self.message_label.text = "Computer wins! Better luck next time!"
        else:
            # Switch to next player
            if self.state.current_player == self.computer_player:
                if self.message_label:
                    self.message_label.text = "Computer's turn..."
                Clock.schedule_once(self.computer_turn, 1.0)
            else:
                if self.message_label:
                    self.message_label.text = "Your turn. Press ROLL to play."
        
        self.redraw()


class SenetApp(App):
    def build(self):
        # Set window size to simulate mobile device
        Window.size = (800, 600)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text='Senet Game', size_hint_y=None, height=50, font_size=30)
        main_layout.add_widget(title)

        # Message label
        self.message_label = Label(text='Welcome to Senet! Choose your player.',
                                  size_hint_y=None, height=50, font_size=18)
        main_layout.add_widget(self.message_label)

        # Board widget
        self.board_widget = SenetBoardWidget()
        self.board_widget.set_message_label(self.message_label)
        main_layout.add_widget(self.board_widget)

        # Control buttons
        controls_layout = GridLayout(cols=2, size_hint_y=None, height=60, spacing=10)

        # Player selection buttons
        player1_btn = Button(text='Play as Player 1 (Red)')
        player1_btn.bind(on_press=self.select_player_1)
        controls_layout.add_widget(player1_btn)

        player2_btn = Button(text='Play as Player 2 (Blue)')
        player2_btn.bind(on_press=self.select_player_2)
        controls_layout.add_widget(player2_btn)

        main_layout.add_widget(controls_layout)

        # Roll button
        self.roll_btn = Button(text='ROLL DICE', size_hint_y=None, height=60)
        self.roll_btn.bind(on_press=self.roll_dice)
        self.roll_btn.disabled = True  # Disabled until player is selected
        main_layout.add_widget(self.roll_btn)

        # Restart button
        restart_btn = Button(text='RESTART GAME', size_hint_y=None, height=60)
        restart_btn.bind(on_press=self.restart_game)
        main_layout.add_widget(restart_btn)

        # Initialize game
        self.init_game()

        return main_layout
    
    def init_game(self):
        # Initialize with default positions
        self.initial_state = GameState(
            player_1_rocks_pos=(1, 3, 5, 7, 9, 11, 13),
            player_2_rocks_pos=(0, 2, 4, 6, 8, 10, 12),
            current_player=1,  # Will be updated after player selection
        )

    def restart_game(self, instance):
        # Reset the game to initial state
        self.board_widget.game_over = False
        self.board_widget.thinking = False
        self.board_widget.selected_rock = None
        self.board_widget.current_roll = None
        self.board_widget.available_moves_list = []

        # Reset to initial state
        if hasattr(self, 'current_player_selection'):
            # If player has already selected, reset to that state
            if self.current_player_selection == 1:
                self.select_player_1(instance)
            else:
                self.select_player_2(instance)
        else:
            # If no selection made yet, just reset message
            self.message_label.text = 'Welcome to Senet! Choose your player.'
            self.roll_btn.disabled = True
    
    def select_player_1(self, instance):
        self.current_player_selection = 1
        self.board_widget.human_player = 1
        self.board_widget.computer_player = 2
        self.board_widget.state = GameState(
            player_1_rocks_pos=self.initial_state.player_1_rocks_pos,
            player_2_rocks_pos=self.initial_state.player_2_rocks_pos,
            current_player=1
        )
        self.board_widget.set_game_state(self.board_widget.state)
        self.roll_btn.disabled = False
        self.message_label.text = "You are Player 1 (Red). Your turn. Press ROLL to play."
        
    def select_player_2(self, instance):
        self.current_player_selection = 2
        self.board_widget.human_player = 2
        self.board_widget.computer_player = 1
        self.board_widget.state = GameState(
            player_1_rocks_pos=self.initial_state.player_1_rocks_pos,
            player_2_rocks_pos=self.initial_state.player_2_rocks_pos,
            current_player=2
        )
        self.board_widget.set_game_state(self.board_widget.state)
        self.roll_btn.disabled = True  # Computer goes first
        self.message_label.text = "You are Player 2 (Blue). Computer's turn..."

        # Start computer's turn
        Clock.schedule_once(self.board_widget.computer_turn, 1.0)
        
    def roll_dice(self, instance):
        if (self.board_widget.state and 
            self.board_widget.state.current_player == self.board_widget.human_player):
            self.board_widget.roll_dice()


if __name__ == '__main__':
    SenetApp().run()

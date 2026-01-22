import random
from kivy.clock import Clock

from state import GameState, board
from actions import number_of_steps, available_moves, apply_move_lists, handle_rebirth
from ai import get_best_move_expectiminimax


class GameLogic:
    
    def __init__(self, app):
        self.app = app
    
    def start_turn(self):
        if self.app.board_widget.game_over:
            return

        current_player = self.app.board_widget.state.current_player

        if self.app.is_two_player_mode:
            player_color = "RED" if current_player == 1 else "BLUE"
            self.app.status_label.text = f'[b]{player_color}\'s turn - Tap ROLL[/b]'
            self.app.roll_button.disabled = False
        else:
            if current_player == self.app.human_player:
                player_color = "RED" if self.app.human_player == 1 else "BLUE"
                self.app.status_label.text = f'[b]{player_color}\'s turn - Tap ROLL[/b]'
                self.app.roll_button.disabled = False
            else:
                self.app.status_label.text = '[b]Computer\'s turn...[/b]'
                self.app.roll_button.disabled = True
                Clock.schedule_once(lambda dt: self.computer_roll_dice(), 0.2)
    
    def on_roll_button_pressed(self):
        if self.app.board_widget.game_over:
            return

        current_player = self.app.board_widget.state.current_player

        if not self.app.is_two_player_mode:
            if current_player != self.app.human_player:
                return

        self.app.roll_button.disabled = True
        self.human_roll_dice()
    
    def human_roll_dice(self):
        self.app.dice_label.text = 'Rolling...'
        self.animate_dice(0, is_human=True)
    
    def computer_roll_dice(self):
        if self.app.is_two_player_mode:
            return

        self.app.dice_label.text = 'Rolling...'
        self.app.status_label.text = '[b]Computer is rolling...[/b]'
        self.animate_dice(0, is_human=False)
    
    def animate_dice(self, count, is_human):
        if count < 5:
            self.app.dice_label.text = f'{random.randint(1, 5)}'
            Clock.schedule_once(lambda dt: self.animate_dice(count + 1, is_human), 0.05)
        else:
            roll = number_of_steps()
            self.app.board_widget.current_roll = roll
            self.app.dice_label.text = f'{roll}'
            
            moves = available_moves(self.app.board_widget.state, roll)
            self.app.board_widget.available_moves_list = moves
            
            if not moves:
                if is_human:
                    self.app.status_label.text = f'[b]Rolled {roll} - No moves available![/b]'
                else:
                    self.app.status_label.text = f'[b]Computer rolled {roll} - No moves![/b]'
                Clock.schedule_once(lambda dt: self.end_turn_no_moves(), 1.0)
            else:
                if is_human:
                    self.app.status_label.text = f'[b]Rolled {roll} - Select your piece[/b]'
                    self.app.board_widget.bind(on_touch_down=self.on_human_move_click)
                else:
                    self.app.status_label.text = f'[b]Computer rolled {roll} - Thinking...[/b]'
                    Clock.schedule_once(lambda dt: self.computer_make_move(roll), 0.5)
    
    def on_human_move_click(self, widget, touch):
        if widget.selected_rock is None:
            return

        current_player = widget.state.current_player
        if self.app.is_two_player_mode:
            positions = (widget.state.player_1_rocks_pos if current_player == 1
                       else widget.state.player_2_rocks_pos)

            if widget.selected_rock not in positions:
                return
        else:
            positions = (widget.state.player_1_rocks_pos if self.app.human_player == 1
                       else widget.state.player_2_rocks_pos)

            if widget.selected_rock not in positions:
                return

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
                    widget.unbind(on_touch_down=self.on_human_move_click)
                    self.execute_move(old_pos, new_pos)
                    return
    
    def computer_make_move(self, roll):
        if self.app.is_two_player_mode:
            Clock.schedule_once(lambda dt: self.end_turn_no_moves(), 0.2)
            return

        best_move, nodes, score = get_best_move_expectiminimax(
            self.app.board_widget.state,
            roll,
            depth=self.app.ai_depth,
            reporting=False
        )

        if best_move:
            old_pos, new_pos = best_move
            self.execute_move(old_pos, new_pos)
        else:
            Clock.schedule_once(lambda dt: self.end_turn_no_moves(), 0.2)
    
    def execute_move(self, old_pos, new_pos):
        def complete_move():
            board_widget = self.app.board_widget
            
            if board_widget.state.current_player == 1:
                if old_pos not in board_widget.state.player_1_rocks_pos:
                    board_widget.state = GameState(
                        player_1_rocks_pos=board_widget.state.player_1_rocks_pos,
                        player_2_rocks_pos=board_widget.state.player_2_rocks_pos,
                        current_player=2 if board_widget.state.current_player == 1 else 1,
                    )
                    board_widget.current_roll = None
                    board_widget.selected_rock = None
                    board_widget.available_moves_list = []
                    board_widget.update_board()
                    self.app.dice_label.text = ''
                    Clock.schedule_once(lambda dt: self.start_turn(), 0.2)
                    return
            else:
                if old_pos not in board_widget.state.player_2_rocks_pos:
                    board_widget.state = GameState(
                        player_1_rocks_pos=board_widget.state.player_1_rocks_pos,
                        player_2_rocks_pos=board_widget.state.player_2_rocks_pos,
                        current_player=2 if board_widget.state.current_player == 1 else 1,
                    )
                    board_widget.current_roll = None
                    board_widget.selected_rock = None
                    board_widget.available_moves_list = []
                    board_widget.update_board()
                    self.app.dice_label.text = ''
                    Clock.schedule_once(lambda dt: self.start_turn(), 0.2)
                    return

            player_1_rocks_pos, player_1_rocks, player_2_rocks_pos, player_2_rocks, rock_idx = \
                apply_move_lists(board_widget.state, (old_pos, new_pos))

            if board_widget.state.current_player == 1:
                player_1_rocks_pos, player_1_rocks = handle_rebirth(
                    player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx
                )
            else:
                player_2_rocks_pos, player_2_rocks = handle_rebirth(
                    player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx
                )

            board_widget.state = GameState(
                player_1_rocks_pos=tuple(player_1_rocks_pos),
                player_2_rocks_pos=tuple(player_2_rocks_pos),
                current_player=2 if board_widget.state.current_player == 1 else 1,
            )

            board_widget.current_roll = None
            board_widget.selected_rock = None
            board_widget.available_moves_list = []
            board_widget.update_board()

            if board_widget.state.is_terminal():
                self.handle_game_over(board_widget.state.winner())
            else:
                self.app.dice_label.text = ''
                Clock.schedule_once(lambda dt: self.start_turn(), 0.2)

        self.app.board_widget.animate_piece_move(old_pos, new_pos, complete_move)
    
    def end_turn_no_moves(self):
        board_widget = self.app.board_widget
        
        player_1_rocks_pos = list(board_widget.state.player_1_rocks_pos)
        player_1_rocks = list(board_widget.state.player_1_rocks)
        player_2_rocks_pos = list(board_widget.state.player_2_rocks_pos)
        player_2_rocks = list(board_widget.state.player_2_rocks)

        rock_idx = -1

        if board_widget.state.current_player == 1:
            player_1_rocks_pos, player_1_rocks = handle_rebirth(
                player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx
            )
        else:
            player_2_rocks_pos, player_2_rocks = handle_rebirth(
                player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx
            )

        board_widget.state = GameState(
            player_1_rocks_pos=tuple(player_1_rocks_pos),
            player_2_rocks_pos=tuple(player_2_rocks_pos),
            current_player=2 if board_widget.state.current_player == 1 else 1,
        )

        board_widget.current_roll = None
        board_widget.selected_rock = None
        board_widget.available_moves_list = []
        self.app.dice_label.text = ''
        board_widget.update_board()

        Clock.schedule_once(lambda dt: self.start_turn(), 0.2)
    
    def handle_game_over(self, winner):
        if self.app.is_two_player_mode:
            if winner == 1:
                self.app.status_label.text = '[b][color=FF6B6B]RED PLAYER WINS![/color][/b]'
            else:
                self.app.status_label.text = '[b][color=6B9DFF]BLUE PLAYER WINS![/color][/b]'
        else:
            if winner == self.app.human_player:
                self.app.status_label.text = '[b][color=FFD700]VICTORY! YOU WIN![/color][/b]'
            else:
                self.app.status_label.text = '[b][color=FF6B6B]Computer Wins![/color][/b]'

        self.app.board_widget.game_over = True
        self.app.roll_button.disabled = True
        self.app.roll_button.background_color = (0.5, 0.5, 0.5, 1)
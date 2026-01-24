from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock

from board_widget import BoardWidget
from game_logic import GameLogic
from ui_components import create_styled_button


class SenetApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.08, 0.06, 1)
        self.main_layout = FloatLayout()
        self.game_logic = GameLogic(self)
        self.show_start_screen()
        return self.main_layout
    
    def show_start_screen(self):
        self.main_layout.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        title = Label(
            text='[b][color=FFD700]SENET[/color][/b]\n[size=20][color=D4AF37]Ancient Egyptian Game of Passage[/color][/size]',
            markup=True,
            size_hint=(1, 0.3),
            font_size='48sp'
        )
        layout.add_widget(title)

        btn_player1 = create_styled_button(
            'Play as RED vs AI',
            (0.8, 0.12),
            {'center_x': 0.5},
            (0.95, 0.3, 0.25, 1)
        )
        btn_player1.bind(on_press=lambda x: self.select_player(1))

        btn_player2 = create_styled_button(
            'Play as BLUE vs AI',
            (0.8, 0.12),
            {'center_x': 0.5},
            (0.25, 0.55, 0.9, 1)
        )
        btn_player2.bind(on_press=lambda x: self.select_player(2))

        btn_two_players = create_styled_button(
            'Two Players Mode',
            (0.8, 0.12),
            {'center_x': 0.5},
            (0.1, 0.6, 0.3, 1)
        )
        btn_two_players.bind(on_press=lambda x: self.start_two_player_game())

        layout.add_widget(btn_player1)
        layout.add_widget(btn_player2)
        layout.add_widget(btn_two_players)

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
        self.is_two_player_mode = False
        self.show_difficulty_screen()

    def start_two_player_game(self):
        self.human_player = 1
        self.computer_player = 2
        self.is_two_player_mode = True
        self.start_game(1)
    
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
            ('Very Easy', 1, (0.1, 0.5, 0.3, 1)),
            ('Easy', 2, (0.2, 0.8, 0.4, 1)),
            ('Medium', 3, (0.95, 0.8, 0.2, 1)),
            ('Hard', 4, (0.95, 0.3, 0.25, 1)),
            ('Expert', 5, (0.6, 0.1, 0.1, 1)),
            ('Master', 6, (0.5, 0.0, 0.5, 1)),
            ('Legendary', 7, (0.8, 0.0, 0.8, 1)),
        ]
        
        for name, depth, color in difficulties:
            btn = create_styled_button(
                name,
                (0.8, 0.15),
                {'center_x': 0.5},
                color,
                font_size='24sp'
            )
            btn.bind(on_press=lambda x, d=depth: self.start_game(d))
            layout.add_widget(btn)
        
        self.main_layout.add_widget(layout)
    
    def start_game(self, depth):
        self.ai_depth = depth
        self.main_layout.clear_widgets()

        game_layout = BoxLayout(orientation='vertical')

        self.status_label = Label(
            text='',
            markup=True,
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(1, 0.95, 0.7, 1)
        )
        game_layout.add_widget(self.status_label)

        main_container = FloatLayout()

        self.board_widget = BoardWidget()
        self.board_widget.size_hint = (1, 0.9)
        self.board_widget.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
        self.board_widget.setup_game(self.human_player, self.ai_depth)
        main_container.add_widget(self.board_widget)

        btn_restart = create_styled_button(
            'RESTART',
            (0.2, 0.08),
            {'x': 0.02, 'top': 0.98},
            (0.7, 0.2, 0.2, 0.8)
        )
        btn_restart.bind(on_press=lambda x: self.restart_game())
        main_container.add_widget(btn_restart)

        dice_text_label = Label(
            text='Dice Result:',
            size_hint=(0.05, 0.06),
            pos_hint={'center_x': 0.43, 'center_y': 0.21},
            font_size='20sp',
            bold=True,
            color=(0.2, 0.1, 0.05, 1),
            halign='center',
            valign='middle'
        )
        main_container.add_widget(dice_text_label)

        self.dice_label = Label(
            text='',
            size_hint=(0.12, 0.12),
            pos_hint={'center_x': 0.56, 'center_y': 0.21},
            font_size='30sp',
            bold=True,
            color=(0.2, 0.1, 0.05, 1),
            halign='center',
            valign='middle',
        )
        with self.dice_label.canvas.before:
            Color(0.95, 0.8, 0.2, 1)
            self.dice_label.circle = Ellipse(
                pos=self.dice_label.pos,
                size=self.dice_label.size
            )
        self.dice_label.bind(pos=lambda inst, val: setattr(inst.circle, 'pos', val))
        self.dice_label.bind(size=lambda inst, val: setattr(inst.circle, 'size', val))
        main_container.add_widget(self.dice_label)

        self.roll_button = create_styled_button(
            'ROLL DICE',
            (0.4, 0.12),
            {'center_x': 0.5, 'y': 0.02},
            (0.85, 0.65, 0.15, 1),
            font_size='22sp'
        )
        self.roll_button.color = (0.2, 0.1, 0.05, 1)
        self.roll_button.bind(on_press=lambda x: self.game_logic.on_roll_button_pressed())
        main_container.add_widget(self.roll_button)

        game_layout.add_widget(main_container)
        self.main_layout.add_widget(game_layout)

        Clock.schedule_once(lambda dt: self.game_logic.start_turn(), 0.1)

    def restart_game(self):
        Clock.unschedule(self.game_logic.start_turn)
        Clock.unschedule(self.game_logic.computer_roll_dice)
        Clock.unschedule(self.game_logic.computer_make_move)
        Clock.unschedule(self.game_logic.end_turn_no_moves)
        Clock.unschedule(self.game_logic.handle_game_over)

        self.main_layout.clear_widgets()

        if hasattr(self, 'board_widget') and self.board_widget:
            self.board_widget.animation_running = False
            self.board_widget.current_roll = None
            self.board_widget.selected_rock = None
            self.board_widget.available_moves_list = []
            self.board_widget.game_over = False

        self.show_start_screen()


if __name__ == '__main__':
    SenetApp().run()
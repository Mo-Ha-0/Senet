from typing import Tuple

NORMAL = 0
REBIRTH = 14
HAPPY = 25
WATER = 26
TRIPLE = 27
DOUBLE = 28
HORUS = 29  

board = (
    NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,
    NORMAL,NORMAL,NORMAL,NORMAL,REBIRTH,NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,
    NORMAL,NORMAL,NORMAL,NORMAL,NORMAL,HAPPY,WATER,TRIPLE,DOUBLE,HORUS,
)

class GameState:
    def __init__(
        self,
        player_1_rocks_pos: Tuple[int, ...],
        player_2_rocks_pos: Tuple[int, ...],
        current_player: int,
    ):
        board_len = len(board)

        self.player_1_rocks = tuple(i in player_1_rocks_pos for i in range(board_len))
        self.player_2_rocks = tuple(i in player_2_rocks_pos for i in range(board_len))

        self.player_1_rocks_pos = player_1_rocks_pos
        self.player_2_rocks_pos = player_2_rocks_pos
        self.current_player = current_player

    def is_terminal(self):
        return len(self.player_1_rocks_pos) == 0 or len(self.player_2_rocks_pos) == 0

    def winner(self):
        if len(self.player_1_rocks_pos) == 0:
            return 1
        if len(self.player_2_rocks_pos) == 0:
            return 2
        return None

    
    def build_final_board(self):
        final_board = []

        for i in range(len(board)):
            if self.player_1_rocks[i]:
                cell = "1"
            elif self.player_2_rocks[i]:
                cell = "2"
            elif board[i] == REBIRTH:
                cell = "R"
            elif board[i] == HAPPY:
                cell = "H"
            elif board[i] == WATER:
                cell = "W"
            elif board[i] == TRIPLE:
                cell = "T"
            elif board[i] == DOUBLE:
                cell = "D"
            elif board[i] == HORUS:
                cell = "H"
            else:
                cell = "."

            final_board.append(cell)

        return final_board
    
    def __hash__(self):
        return hash((
            self.player_1_rocks_pos,
            self.player_2_rocks_pos,
            self.current_player
        ))

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return (
            self.player_1_rocks_pos == other.player_1_rocks_pos and
            self.player_2_rocks_pos == other.player_2_rocks_pos and
            self.current_player == other.current_player
        )

    def print_details(self):
        print("\n🟢 Game State Details")
        print(f"Current Player: {self.current_player}")

        # Player 1
        print(f"Player 1 Rocks Positions ({len(self.player_1_rocks_pos)}): {self.player_1_rocks_pos}")

        # Player 2
        print(f"Player 2 Rocks Positions ({len(self.player_2_rocks_pos)}): {self.player_2_rocks_pos}")

        print(len(self.player_1_rocks))
        print("\n")
        print(self.player_2_rocks)
        print("\n")

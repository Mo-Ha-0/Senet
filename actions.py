import random
from state import GameState
from state import board
from state import DOUBLE, REBIRTH, HAPPY, WATER, TRIPLE, HORUS, NORMAL


def number_of_steps():

    sticks = [random.randint(0, 1) for _ in range(4)]

    total_dark = sum(sticks)

    if total_dark == 0:
        return 5
    else:
        return total_dark


def available_moves(state: GameState, steps: int):
    moves = []
    player = state.current_player

    if player == 1:
        player_rocks_pos = state.player_1_rocks_pos
        player_rocks = state.player_1_rocks
    elif player == 2:
        player_rocks_pos = state.player_2_rocks_pos
        player_rocks = state.player_2_rocks
    else:
        raise ValueError("Invalid current_player")

    for idx, pos in enumerate(player_rocks_pos):
        new_pos = pos + steps
        current_cell = board[pos]

        # 1. SPECIAL HOUSE EXIT RULES (MUST happen before bearing off)
        # These squares require an exact roll to leave the board or move forward
        if current_cell == TRIPLE and steps != 3:
            continue
        if current_cell == DOUBLE and steps != 2:
            continue
        
        # 2. HOUSE OF HAPPINESS PASSING RULE
        # You cannot skip the House of Happiness; you must land on it
        if pos < HAPPY and new_pos > HAPPY:
            continue

        # 3. BEARING OFF (Winning the piece)
        if new_pos >= len(board):
            moves.append((pos, new_pos))
            continue

        # 4. SELF-BLOCK CHECK
        # Cannot land on your own pieces
        if player_rocks[new_pos]:
            continue

        moves.append((pos, new_pos))

    return moves


def apply_move_lists(state: GameState, move: tuple):
    old_pos, new_pos = move
    player = state.current_player

    # نسخ القوائم
    player_1_rocks_pos = list(state.player_1_rocks_pos)
    player_2_rocks_pos = list(state.player_2_rocks_pos)
    player_1_rocks = list(state.player_1_rocks)
    player_2_rocks = list(state.player_2_rocks)

    if player == 1:
        rocks_pos = player_1_rocks_pos
        rocks_bool = player_1_rocks
        opp_pos = player_2_rocks_pos
        opp_bool = player_2_rocks
    else:
        rocks_pos = player_2_rocks_pos
        rocks_bool = player_2_rocks
        opp_pos = player_1_rocks_pos
        opp_bool = player_1_rocks

    rock_idx = rocks_pos.index(old_pos)

    # التعامل مع حجر الخصم
    if new_pos < len(board) and opp_bool[new_pos]:
        opp_idx = opp_pos.index(new_pos)
        opp_pos[opp_idx] = old_pos
        opp_bool[old_pos] = True

    # تحريك حجر اللاعب
    if new_pos >= len(board):
        del rocks_pos[rock_idx]
        rocks_bool[old_pos] = False
        rock_idx = -1
    else:
        rocks_pos[rock_idx] = new_pos
        rocks_bool[old_pos] = False
        rocks_bool[new_pos] = True

    return (
        player_1_rocks_pos,
        player_1_rocks,
        player_2_rocks_pos,
        player_2_rocks,
        rock_idx,
    )


def handle_rebirth(
    current_player_rocks_pos, current_player_rocks, opponent_rocks_pos, rock_idx
):
    
    for idx, pos in enumerate(current_player_rocks_pos):
        
        if board[pos] ==WATER:
            target = REBIRTH
            while target in current_player_rocks_pos or target in opponent_rocks_pos:
                target -= 1
                if target < 0:
                    target = 0
                    break

            current_player_rocks_pos[idx] = target

            current_player_rocks = [
                i == target if i == pos else val
                for val, i in enumerate(current_player_rocks)
            ]
        
        if board[pos] in ( DOUBLE, TRIPLE, HORUS):
            if(idx ==rock_idx):
                continue
            target = REBIRTH
            while target in current_player_rocks_pos or target in opponent_rocks_pos:
                target -= 1
                if target < 0:
                    target = 0
                    break

            current_player_rocks_pos[idx] = target

            current_player_rocks = [
                i == target if i == pos else val
                for val, i in enumerate(current_player_rocks)
            ]

    return current_player_rocks_pos, current_player_rocks


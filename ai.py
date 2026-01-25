from dataclasses import dataclass
from state import GameState, board, HAPPY, WATER
from actions import available_moves, apply_move_lists, handle_rebirth

VERBOSE = False
def evaluate_state(state: GameState, player: int):
    if state.is_terminal():
        winner = state.winner()
        if winner == player:
            return 10000
        elif winner is not None:
            return -10000
        else:
            return 0

    if player == 1:
        p_positions = state.player_1_rocks_pos
        o_positions = state.player_2_rocks_pos
    else:
        p_positions = state.player_2_rocks_pos
        o_positions = state.player_1_rocks_pos

    player_pieces_remaining = len(p_positions)
    opponent_pieces_remaining = len(o_positions)

    total_p = 0




















    
    for x in p_positions:
        total_p += x
    if player_pieces_remaining > 0:
        player_advancement = total_p / player_pieces_remaining
    else:
        player_advancement = 0.0

    total_o = 0
    for x in o_positions:
        total_o += x
    if opponent_pieces_remaining > 0:
        opponent_advancement = total_o / opponent_pieces_remaining
    else:
        opponent_advancement = 0.0

    piece_advantage = (opponent_pieces_remaining - player_pieces_remaining) * 10
    advancement_advantage = (player_advancement - opponent_advancement) * 0.5

    p_happy = 0
    for pos in p_positions:
        if pos > HAPPY:
            p_happy += 1
    o_happy = 0
    for pos in o_positions:
        if pos > HAPPY:
            o_happy += 1
    happy_bonus = (p_happy - o_happy) * 5

    p_risky = 0
    for pos in p_positions:
        try:
            if board[pos] == WATER:
                p_risky += 1
        except Exception:
            if VERBOSE:
                print(f"[warn] board check failed for pos={pos}")

    o_risky = 0
    for pos in o_positions:
        try:
            if board[pos] == WATER:
                o_risky += 1
        except Exception:
            if VERBOSE:
                print(f"[warn] board check failed for pos={pos}")

    risky_penalty = (o_risky - p_risky) * 3

    p_exit = 0
    for pos in p_positions:
        delta = pos - 20
        if delta > 0:
            p_exit += delta

    o_exit = 0
    for pos in o_positions:
        delta = pos - 20
        if delta > 0:
            o_exit += delta

    exit_bonus = (p_exit - o_exit) * 0.2

    score = piece_advantage + advancement_advantage + happy_bonus + risky_penalty + exit_bonus

    if player_pieces_remaining <= 2 and opponent_pieces_remaining <= 2:
        score += (player_advancement - opponent_advancement) * 0.15

    if VERBOSE:
        print(
            "[eval] p=%s pieces %d-%d adv %.2f-%.2f score=%.2f (happy %d-%d risky %d-%d exit %d-%d)"
            % (
                player,
                player_pieces_remaining,
                opponent_pieces_remaining,
                player_advancement,
                opponent_advancement,
                score,
                p_happy,
                o_happy,
                p_risky,
                o_risky,
                p_exit,
                o_exit,
            )
        )

    return score


def get_dice_probabilities():
    return {
        1: 4 / 16 ,
        2: 6 / 16 ,
        3: 4 / 16 ,
        4: 1 / 16 ,
        5: 1 / 16 ,
    }

def apply_move(state: GameState, move): 
    player_1_rocks_pos, player_1_rocks, player_2_rocks_pos, player_2_rocks, rock_idx = apply_move_lists(state, move)
    
    # print(p1_pos)
    # print(rock_idx)

    if state.current_player == 1: 
        player_1_rocks_pos, player_1_rocks = handle_rebirth(player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx)
    else:
        player_2_rocks_pos, player_2_rocks = handle_rebirth(player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx)
    
    if state.current_player == 1: 
        current_player = 2
    else:
        current_player = 1

    player_1_rocks_pos=tuple(player_1_rocks_pos)
    player_2_rocks_pos=tuple(player_2_rocks_pos)
    new_state = GameState(player_1_rocks_pos, player_2_rocks_pos, current_player)

    return new_state

@dataclass()
class TranspositionTable:
    table: dict = None

    def __init__(self):
        if self.table is None:
            self.table = {}

    def check(self, state, depth):
        entry = self.table.get(hash(state))
        if not entry:
            return None
        s_depth, value = entry
        if s_depth >= depth:
            return value
        return None

    def store(self, state, depth, value):
        self.table[hash(state)] = (depth, value)

    def clear(self):
        self.table.clear()

@dataclass()
class debug:
    # def __init__(self):
    #     self.nodes_visited = 0
    #     self.pruned_count = 0
    nodes_visited: int = 0
    pruned_count: int = 0

    def visit(self):
        self.nodes_visited += 1

    def pruned_branches(self):
        self.pruned_count += 1

def expectiminimax(state: GameState, depth, player, stats, reporting, tt):
    stats.visit()

    cache = tt.check(state, depth)
    if cache is not None:
        if reporting:
            print(f"TranspositionTable hit, depth={depth} value={cache:.2f}")
        return cache

    if depth == 0 or state.is_terminal():
        eval_state = evaluate_state(state, player)
        tt.store(state, depth, eval_state)
        if reporting:
            print(f"leaf depth={depth} val={eval_state:.2f}")
        return eval_state

    total_expected_value = 0.0
    probabilities = get_dice_probabilities()

    for roll, prob in probabilities.items():
        moves = available_moves(state, roll)

        if not moves:
            next_state = GameState(state.player_1_rocks_pos, state.player_2_rocks_pos, 3 - state.current_player)
            outcome_value = expectiminimax(next_state, depth - 1, player, stats, reporting, tt)
        else:
            moves_with_scores = []
            for m in moves:
                new_state = apply_move(state, m)
                score = evaluate_state(new_state, player)
                moves_with_scores.append((m, score))

            if state.current_player == player:
                best_value = float('-inf')
                for move, _ in moves_with_scores:
                    new_state = apply_move(state, move)
                    child_value = expectiminimax(new_state, depth - 1, player, stats, reporting, tt)
                    if child_value > best_value:
                        best_value = child_value
                outcome_value = best_value
            else:
                best_value = float('inf')
                for move, _ in moves_with_scores:
                    new_state = apply_move(state, move)
                    child_value = expectiminimax(new_state, depth - 1, player, stats, reporting, tt)
                    if child_value < best_value:
                        best_value = child_value
                outcome_value = best_value

        total_expected_value += prob * outcome_value

    if reporting:
        print(f"node value {total_expected_value:.2f}")

    tt.store(state, depth, total_expected_value)
    return total_expected_value


def get_best_move_expectiminimax(state: GameState, roll, depth, reporting): 
    current_player = state.current_player
    moves = available_moves(state, roll)
    deb = debug()
    tt = TranspositionTable()

    if not moves:
        if reporting:
            print("[best] no moves")
        return None, deb.nodes_visited, 0

    best_move = None
    best_score = float('-inf')
    evaluatons = []

    if reporting:
        print(f"\n decision roll={roll} depth={depth} ")

    for move in moves:
        next_st = apply_move(state, move)
        score = expectiminimax(next_st, depth - 1, current_player, deb, reporting, tt)
        evaluatons.append((move, score))
        if reporting:
            print(f"[best] move={move} score={score:.2f}")

        if score > best_score:
            best_score = score
            best_move = move

    # if best_move is None and moves:
    #     best_move = moves[0]

    if True:
        print(f" selected {best_move} score={best_score:.2f} nodes={deb.nodes_visited} pruned={deb.pruned_count} ")

    return best_move, deb.nodes_visited, best_score
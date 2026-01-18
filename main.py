import random
from state import GameState
from state import board
from actions import number_of_steps, available_moves, apply_move_lists, handle_rebirth
from game import choos_player
from state import DOUBLE, REBIRTH, HAPPY, WATER, TRIPLE, HORUS, NORMAL
from ai import get_best_move_expectiminimax


def print_board(state: GameState):
    fb = state.build_final_board()
    rows = [
        range(0, 10),
        range(19, 9, -1),
        range(20, 30),
    ]
    print("\n🏁 Current Board:")
    for row in rows:
        for i in row:
            print(fb[i], end="  ")
        print()
    print()


def print_moves(moves):
    if not moves:
        print("❌ No available moves")
        return
    print("✅ Available moves:")
    for i, (old_pos, new_pos) in enumerate(moves, start=1):
        print(f"{i}. Rock {old_pos} → Cell {new_pos}")
    print()


def choose_move(moves):
    if not moves:
        return None

    while True:
        choice = input("Choose move number or 'r' to restart: ").lower()
        if choice == "r":
            return "restart"
        if choice.isdigit() and 1 <= int(choice) <= len(moves):
            return moves[int(choice) - 1]
        print("❌ Invalid choice, try again")


def build_board(player_1_rocks, player_2_rocks):
    final_board = []

    for i in range(len(board)):
        if player_1_rocks[i]:
            cell = "1"
        elif player_2_rocks[i]:
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



def main():
    human_player = choos_player()
    computer_player = 2 if human_player == 1 else 1

    # Get AI settings from user
    while True:
        try:
            ai_depth = int(input("Enter AI search depth (e.g., 2 or 3): "))
            if ai_depth > 0:
                break
            print("❌ Depth must be a positive integer.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

    ai_reporting = input("Enable detailed AI reporting? (y/n): ").lower() == 'y'

    initialState = GameState(
        player_1_rocks_pos=(1, 3, 5, 7, 9, 11, 13),
        player_2_rocks_pos=(0, 2, 4, 6, 8, 10, 12),
        current_player=human_player,
    )

    state = initialState
    turn = 0

    while not state.is_terminal():
        print(f"🔹 Turn {turn + 1}: Player {state.current_player}")
        print_board(state)

        steps = number_of_steps()

        # Determine if it's the human or computer's turn
        if state.current_player == human_player:
            # Human player's turn
            print(f"🎲 Player {state.current_player} rolled: {steps} steps")
        else:
            # Computer player's turn - show dice result first
            print(f"🎲 Computer rolled: {steps} steps")

        moves = available_moves(state, steps)
        print_moves(moves)

        # Initialize variables for the next state
        player_1_rocks_pos = state.player_1_rocks_pos
        player_1_rocks = state.player_1_rocks
        player_2_rocks_pos = state.player_2_rocks_pos
        player_2_rocks = state.player_2_rocks

        if moves:
            # Determine if it's the human or computer's turn
            if state.current_player == human_player:
                # Human player's turn
                selected_move = choose_move(moves)
                if selected_move == "restart":
                    state = initialState
                    turn = 0
                    continue
            else:
                # Computer player's turn - show dice result and then start thinking
                print("🤖 Computer is thinking...")
                selected_move, nodes, score = get_best_move_expectiminimax(
                    state, steps, depth=ai_depth, reporting=ai_reporting
                )

                if not ai_reporting:
                    print(f"🤖 Computer explored {nodes} nodes and evaluated move with score {score:.2f}")

                if selected_move:
                    print(f"🤖 Computer chooses to move rock from position {selected_move[0]} to {selected_move[1]}")
                else:
                    print("🤖 Computer has no valid moves")
                    selected_move = None

        if selected_move:
            (
                player_1_rocks_pos_new,
                player_1_rocks_new,
                player_2_rocks_pos_new,
                player_2_rocks_new,
                rock_idx,
            ) = apply_move_lists(state, selected_move)

            if state.current_player == 1:
                player_1_rocks_pos_new, player_1_rocks_new = handle_rebirth(
                    player_1_rocks_pos_new, player_1_rocks_new, player_2_rocks_new, rock_idx
                )
            else:
                player_2_rocks_pos_new, player_2_rocks_new = handle_rebirth(
                    player_2_rocks_pos_new, player_2_rocks_new, player_1_rocks_new, rock_idx
                )

            # Update the variables with the new state after the move
            player_1_rocks_pos = player_1_rocks_pos_new
            player_1_rocks = player_1_rocks_new
            player_2_rocks_pos = player_2_rocks_pos_new
            player_2_rocks = player_2_rocks_new
        else:
            print("⏭️ No available moves, turn skipped.")

        # switch player and increment turn
        state = GameState(
            player_1_rocks_pos=player_1_rocks_pos,
            player_2_rocks_pos=player_2_rocks_pos,
            current_player=2 if state.current_player == 1 else 1,
        )
        turn += 1

    # game finished
    print_board(state)
    winner = state.winner()
    if winner:
        if winner == human_player:
            print(f"🏆 Congratulations! You win!")
        else:
            print(f"🤖 Computer wins! Better luck next time!")
    else:
        print("⚠️ Game ended with no winner!")


if __name__ == "__main__":
    main()

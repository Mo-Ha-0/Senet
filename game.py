import random
from state import GameState
from state import board
from actions import number_of_steps, available_moves, apply_move_lists


def choos_player():
    p = 0
    while p != 1 and p != 2:
        user_input = input("Which player do you want to be? (1/2) ")
        if user_input.isdigit():       # check if input is a number
            p = int(user_input)
        else:
            p = 0  # invalid input, continue the loop

    print(f"You chose Player {p}")
    return p

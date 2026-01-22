try:
    import ai_cpp
    CPP_AVAILABLE = True
    print("C++  implementation loaded successfully!")
except ImportError:
    CPP_AVAILABLE = False
    print("C++ implementation is not available, using Python implementation")
    from ai import get_best_move_expectiminimax as python_get_best_move


def get_best_move_expectiminimax(state, roll, depth=3, reporting=False, use_cpp=True):

    if not CPP_AVAILABLE or reporting or not use_cpp:
        from ai import get_best_move_expectiminimax as python_get_best_move
        return python_get_best_move(state, roll, depth, reporting)

    p1_pos = list(state.player_1_rocks_pos)
    p2_pos = list(state.player_2_rocks_pos)

    move, nodes, score = ai_cpp.get_best_move(
        p1_pos,
        p2_pos,
        state.current_player,
        roll,
        depth
    )

    if move[0] == -1:
        return None, nodes, score

    return (move[0], move[1]), nodes, score

if CPP_AVAILABLE:
    print("Using C++ Implementation")
else:
    print("Using Python implementation")
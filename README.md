# Senet Game with AI

This is an implementation of the ancient Egyptian board game Senet enhanced with an AI opponent using the expectiminimax algorithm.

## Game Overview

Senet is one of the oldest known board games, dating back to around 3100 BCE in ancient Egypt. The game involves two players moving pieces along a grid of 30 squares, with the goal of being the first to remove all pieces from the board.

## Features

- **Classic Senet gameplay** with traditional rules and board layout
- **AI opponent** powered by the expectiminimax algorithm
- **Probability-based decision making** that accounts for the random dice rolls
- **Intelligent move selection** using depth-limited search
- **Human vs Computer gameplay**

## Algorithm Implementation

### Expectiminimax AI

The computer player uses the expectiminimax algorithm, which is ideal for games with elements of chance like Senet:

- **Max Nodes**: Represent the computer's turn where it maximizes its utility
- **Min Nodes**: Represent the human player's turn where they minimize the computer's utility
- **Chance Nodes**: Represent the random dice roll outcomes with associated probabilities

### Dice Roll Probabilities

The game uses 4 binary sticks (coin-like) to determine movement:
- 0 white (4 dark): 1/16 probability → 5 steps
- 1 white (3 dark): 4/16 probability → 1 step
- 2 white (2 dark): 6/16 probability → 2 steps
- 3 white (1 dark): 4/16 probability → 3 steps
- 4 white (0 dark): 1/16 probability → 4 steps

### Evaluation Function

The AI evaluates board positions based on:
- Number of pieces remaining for each player (fewer is better as pieces exit the board)
- Average advancement of pieces toward the end
- Pieces that have passed the "safe" zones (past HAPPY)
- Risk assessment for pieces in vulnerable positions (near WATER)
- Bonus for pieces positioned near the exit (ready to leave the board)

## Files

- `main.py`: Main game loop with human vs computer gameplay
- `game.py`: Game setup and player selection
- `state.py`: Game state representation and board layout
- `actions.py`: Move generation and application logic
- `ai.py`: Expectiminimax algorithm implementation

## How to Play

1. Run `python main.py`
2. Choose whether you want to be Player 1 or Player 2
3. Take turns rolling the dice and moving your pieces
4. The first player to remove all pieces from the board wins

## AI Difficulty

The AI uses a search depth of 4 by default, providing a challenging but responsive opponent. The depth can be adjusted in the main.py file for easier or harder gameplay.

## Strategy Notes

- Pieces must reach the end of the board to win
- Landing on an opponent's piece sends it backward
- Special squares (REBIRTH, HAPPY, WATER, etc.) have unique effects
- The AI considers all possible future game states when making decisions

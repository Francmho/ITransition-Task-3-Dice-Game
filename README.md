# ITransition-Task-3-Dice-Game
A console script that implements a generalized dice game.

## Introduction

Welcome to the Dice Game! This is a general non-transitive dice game where players choose their own dice configurations and play with the computer. The dice can have any number of faces and the game is designed to highlight the non-transitive nature of dice (i.e., one die beats another, but loses to a third). The goal is to make the game both challenging and fair, where players cannot always select the highest value.

## Features

- 🎲 Dice throws for both player and computer.
- 🔢 Add your number modulo 6 for fair gameplay.
- 🧠 Play against a smart AI.
- ❓ Interactive help and exit options.
- 🕹️ Fun for all ages!

## Installation

Follow these simple steps to get started:

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/dice-game.git
    ```

2. Navigate to the project directory:

    ```bash
    cd dice-game
    ```

3. Install dependencies (if any):

    ```bash
    pip install -r requirements.txt
    ```

4. Run the game:

    ```bash
    python game.py
    ```

That's it! You're ready to play.

## Game Setup

To start the game, you specify the dice and their faces directly in the command line. Each set of numbers represents one die, and the numbers within the set are the faces of that die.

### Example Command:

```bash
java -jar game.jar 1,2,3,4,5,6 2,2,4,4,9,9 1,1,6,6,8,8

1,2,3,4,5,6: The first die has faces with the values 1, 2, 3, 4, 5, 6.
2,2,4,4,9,9: The second die has faces with the values 2, 2, 4, 4, 9, 9.
1,1,6,6,8,8: The third die has faces with the values 1, 1, 6, 6, 8, 8.
The game allows you to choose any number of dice (greater than 2) and define their faces as needed.

Additional Parameters
The number of dice and the faces of each die are defined in the command line. Make sure to pass valid dice configurations for the game to function properly.

Usage
Once the game starts, you'll be prompted to make your move:

Choose a dice number between 0 and 5.
The game will calculate your throw and add it to the computer's number modulo 6.
You’ll see the results and the winner will be displayed!
Example of gameplay:

You choose the [2, 2, 4, 4, 9, 9] die. It's time for my throw. I selected a random value in the range 0..5. Add your number modulo 6.

0 - 0
1 - 1
2 - 2
3 - 3
4 - 4
5 - 5

Your selection: 4

The result is 4 + 3 = 1 (mod 6). My throw is 8.

And the game continues from there!

Contributing
We welcome contributions! Feel free to fork this project, open an issue, or submit a pull request. Here's how you can contribute:

Fork the repository.
Create a new branch (git checkout -b feature-name).
Make your changes.
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-name).
Open a pull request.

All contributions are appreciated!

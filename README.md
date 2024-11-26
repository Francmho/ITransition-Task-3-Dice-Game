# ITransition-Task-3-Dice-Game
A console script that implements a generalized dice game.

## Introduction

Welcome to the General Non-Transitive Dice Game! In this game, players select dice with different faces and compete against the computer. The unique feature of this game is the non-transitive nature of the dice – one die may beat another, but lose to a third. This makes the game both fair and strategic.

[Demo Video](./game_dice.py)


## Features

- 🎲 Dice Throws: Both player and computer take turns rolling the dice.
- 🔢 Modulo 6 for Fair Gameplay: Dice rolls are processed with modulo 6 for balanced gameplay.
- 🧠 AI Opponent: Play against a smart AI that randomly selects dice and rolls them.
- ❓ Interactive Help: View probabilities for winning against different dice combinations.
- 🕹️ Fun for All Ages: A simple yet challenging dice game with a strategic twist.

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

Now you're ready to play!

## Game Setup

The game allows you to specify the number of dice and the number of faces for each die through the command line.


### Example Command:

```bash
python python game_dice.py 3,4,7,7,4,3 7,4,5,6,3,5 8,5,8,2,3,8
```

The first group of numbers (e.g. 3,4,7,7,4,3) represents a dice and its faces.
The second group (e.g. 3,4,7,7,4,3 7,4,5,6,3,5) must be separated by a space.
Make sure to specify valid configurations for a smooth game experience.

The game allows you to choose any number of dice (greater than 2) and the number of faces (greater than 6)

##Gameplay

Once the game starts, you'll be prompted to make a move by choosing a die and rolling it. You can also request help to view winning probabilities.

###Example of Gameplay:

1. Player's Turn: You select a dice configuration.
2. Computer's Turn: The AI selects a die and rolls it.
3. Result: The rolls are compared, and the winner is determined.

##Sample Output:
```bash
🎲 Welcome to the General Non-Transitive Dice Game! 🎲
We will play with 4 dice(s) and 7 faces per die.

Let's determine who makes the first move! Or exit the game (x).
Guess my selection (0 or 1):
```

After this, you'll choose a die to roll, and the computer will do the same. The winner is the player with the higher total roll.

###Commands
- 0, 1, 2, 3... Select a die to play.
- W: View the probabilities of winning with different dice configurations.
- X: Exit the game.



##Contributing
We welcome contributions! To contribute, follow these steps:

1. Fork the repository.
2. Create a new branch: git checkout -b feature-name.
3. Make your changes and commit them: git commit -am 'Add new feature'.
4. Push to the branch: git push origin feature-name.
5. Open a pull request to merge your changes.

All contributions are appreciated!

###Acknowledgments
- Thank you to the contributors of the tabulate and colorama libraries.

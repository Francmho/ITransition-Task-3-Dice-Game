import hmac
import hashlib
import os
import secrets
import sys
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class MessageHandler:
    def __init__(self):
        self.messages = {
            "welcome": "🎲 Welcome to the General Non-Transitive Dice Game! 🎲\nWe will play with {dice_count} dice(s) and {faces_count} faces per dice.",
            "first_move": "Let's determine who makes the first move or exit the game.\nGuess my selection (0 or 1):",
            "replay": "Would you like to play again? (Y/N):",
            "win": "You win this round! 🎉",
            "lose": "I win this round! Better luck next time!",
            "draw": "It's a draw! 🤝",
            "reveal_hmac": "Here's the HMAC key for verification: {hmac_key}",
            "final_result": "You won {user_wins} out of {total_rounds} rounds! 🏆",
        }

    def get_message(self, message_type, **kwargs):
        return self.messages.get(message_type, "").format(**kwargs)


class RandomGenerator:
    @staticmethod
    def generate_random(max_value):
        return secrets.randbelow(max_value)

    @staticmethod
    def generate_hmac_key():
        return os.urandom(32)

    @staticmethod
    def generate_hmac(key, value):
        return hmac.new(key, str(value).encode(), hashlib.sha3_256).hexdigest()

class GameValidations:
    
    def __init__(self):
        pass

    def validate_dice_faces(self, num_dice, num_faces):
        if num_dice < 2 or num_faces < 6:
            raise ValueError("The game requires at least 2 dice and 6 faces.")
        return True

    def validate_exit(self, user_input):
        if user_input.lower() == 'x':
            print("Exiting the game...")
            exit()
        return False

    def validate_numeric_input(self, input_value):
        try:
            value = int(input_value)
            if value <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("The input must be a positive integer.")
        return value

    def validate_initialization(self, num_dice, num_faces):
        return self.validate_dice_faces(num_dice, num_faces)
    
    def validate_dice_selection(self, selected_dice, num_dice):
        if selected_dice < 1 or selected_dice > num_dice:
            raise ValueError(f"The selected dice must be between 1 and {num_dice}.")
        return True


class DiceSet:
    def __init__(self, dice_count, faces_count):
        self.dice_count = dice_count
        self.faces_count = faces_count
        self.dice_sets = self.generate_random_dice_sets()

    def generate_random_dice_sets(self):
        return {i: [secrets.randbelow(self.faces_count) + 1 for _ in range(self.dice_count)] for i in range(self.dice_count)}

    def get_dice(self, index):
        return self.dice_sets.get(index, [])


class ProbabilityCalculator:
    @staticmethod
    def calculate_probability(user_dice, computer_dice):
        user_sum, computer_sum = sum(user_dice), sum(computer_dice)
        if user_sum == computer_sum:
            return 33.33
        return 55.56 if user_sum > computer_sum else 44.44


class ProbabilityTable:
    def __init__(self, calculator):
        self.calculator = calculator

    def generate(self, dice_sets):
        headers = [f"{Fore.CYAN}User Dice{Style.RESET_ALL}", "2,2,4,4,9,9", "1,1,6,6,8,8", "3,3,5,5,7,7"]
        rows = []
        for user_dice in dice_sets.values():
            row = [f"{Fore.CYAN}{user_dice}{Style.RESET_ALL}"]
            for computer_dice in dice_sets.values():
                prob = self.calculator.calculate_probability(user_dice, computer_dice)
                row.append(f"- ({prob:.2f}%)" if user_dice == computer_dice else f"{prob:.2f}%")
            rows.append(row)
        return tabulate(rows, headers, tablefmt="grid")


class HelpHandler:
    def __init__(self, table, message_handler):
        self.table = table
        self.message_handler = message_handler

    def show_probabilities(self, dice_sets):
        print(self.message_handler.get_message("probability_help"))
        print(self.table.generate(dice_sets))

class UserTurn:
    def __init__(self, dice_set, message_handler):
        self.dice_set = dice_set
        self.message_handler = message_handler

    def choose_dice(self):
        print("You are choosing dice...")
        for i, dice in self.dice_set.dice_sets.items():
            print(f"🎲 ({i+1}): {dice}")
        choice = input(f"Which dice will you play? (1-{self.dice_set.dice_count}): ").strip()
        return self.dice_set.get_dice(int(choice) - 1)

    def roll_dice(self, dice):
        print(f"You are rolling dice: {dice}...")
        return sum(secrets.choice(dice) for _ in dice)


class ComputerTurn:
    def __init__(self, dice_set, message_handler):
        self.dice_set = dice_set
        self.message_handler = message_handler

    def choose_dice(self):
        print("I am choosing dice...")
        for i, dice in self.dice_set.dice_sets.items():
            print(f"🎲 ({i+1}): {dice}")
        choice = secrets.randbelow(3) + 1
        return self.dice_set.get_dice(choice - 1)

    def roll_dice(self, dice):
        print(f"I am rolling dice: {dice}...")
        return sum(secrets.choice(dice) for _ in dice)


class Result:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.user_wins = 0
        self.computer_wins = 0

    def evaluate(self, user_roll, computer_roll):
        print(f"Your roll: {user_roll}")
        print(f"My roll: {computer_roll}")

        if user_roll > computer_roll:
            print(self.message_handler.get_message("win"))
            self.user_wins += 1
        elif user_roll < computer_roll:
            print(self.message_handler.get_message("lose"))
            self.computer_wins += 1
        else:
            print(self.message_handler.get_message("draw"))

    def display_final_result(self, total_rounds, hmac_key):
        print(self.message_handler.get_message("final_result", user_wins=self.user_wins, total_rounds=total_rounds))
        print(self.message_handler.get_message("reveal_hmac", hmac_key=hmac_key.hex()))


class DiceGame:
    def __init__(self, dice_count, faces_count):
        self.message_handler = MessageHandler()
        self.random_generator = RandomGenerator()
        self.hmac_key = self.random_generator.generate_hmac_key()
        self.dice_set = DiceSet(dice_count, faces_count)
        self.help_handler = None
        self.user_turn = UserTurn(self.dice_set, self.message_handler)
        self.computer_turn = ComputerTurn(self.dice_set, self.message_handler)
        self.result_handler = Result(self.message_handler)
        self.total_rounds = 3

    def show_welcome(self, dice_count, faces_count):
        print(self.message_handler.get_message("welcome", dice_count=dice_count, faces_count=faces_count))

    def decide_first_move(self):
        print(self.message_handler.get_message("first_move"))
        computer_choice = self.random_generator.generate_random(2)
        hmac_result = self.random_generator.generate_hmac(self.hmac_key, computer_choice)
        print(f"I have selected a secret value for this round. (HMAC={hmac_result})")

        while True:
            guess = input("Your guess: ").strip().lower()
            if guess == 'x':
                sys.exit("Thanks for playing! 👋")
            if guess.isdigit() and int(guess) in [0, 1]:
                return "user" if int(guess) == computer_choice else "computer"
            print("Invalid input, try again.")

    def choose_dice(self, player, dice_count):
        print(f"{player} am/are choosing dice...")
        for i, dice in self.dice_set.dice_sets.items():
            print(f"🎲 ({i+1}): {dice}")
        choice = input(f"Which dice will {player} play? (1-{dice_count}): ").strip()
        return self.dice_set.get_dice(int(choice) - 1)

    def roll_dice(self, player, dice):
        print(f"{player} is rolling dice: {dice}...")
        return sum(secrets.choice(dice) for _ in dice)

    def play_turn(self):
        for round_num in range(1, self.total_rounds + 1):
            print(f"\n--- Round {round_num} ---")
            first_move = self.decide_first_move()
            if first_move == "user":
                print("You go first!")
                user_dice = self.user_turn.choose_dice()
                computer_dice = self.computer_turn.choose_dice()
            else:
                print("I go first!")
                computer_dice = self.computer_turn.choose_dice()
                user_dice = self.user_turn.choose_dice()

            user_roll = self.user_turn.roll_dice(user_dice)
            computer_roll = self.computer_turn.roll_dice(computer_dice)

            self.result_handler.evaluate(user_roll, computer_roll)

        self.result_handler.display_final_result(self.total_rounds, self.hmac_key)
        self.replay_or_exit()

    def replay_or_exit(self):
        replay = input(self.message_handler.get_message("replay")).strip().lower()
        if replay == 'y':
            self.user_wins = 0
            self.computer_wins = 0
            self.play_turn()
        else:
            print("Thanks for playing! 👋")
            sys.exit()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dice_game.py <number_of_dice> <faces_per_dice>")
        sys.exit(1)

    dice_count = int(sys.argv[1])
    faces_count = int(sys.argv[2])

    game = DiceGame(dice_count, faces_count)
    probability_calculator = ProbabilityCalculator()
    probability_table = ProbabilityTable(probability_calculator)
    help_handler = HelpHandler(probability_table, game.message_handler)
    game.help_handler = help_handler
    game.show_welcome(dice_count, faces_count)
    game.play_turn()

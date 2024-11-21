import hmac
import hashlib
import os
import secrets
import sys
import random
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class MessageHandler:
    def __init__(self):
        self.messages = {
            "welcome": f"{Fore.MAGENTA}🎲 Welcome to the General Non-Transitive Dice Game! 🎲{Style.RESET_ALL}\nWe will play with {{dice_count}} dice(s) and {{faces_count}} faces per dice.",
            "first_move": f"{Fore.MAGENTA}Let's determine who makes the first move!.{Style.RESET_ALL} Or exit the game (x).{Fore.MAGENTA}\nGuess my selection (from 0 to 3):{Style.RESET_ALL}",
            "replay": f"{Fore.MAGENTA}Would you like to play again? (Y/N):{Style.RESET_ALL}",
            "win": f"{Fore.GREEN}You win this round! 🎉{Style.RESET_ALL}",
            "lose": f"{Fore.RED}I win this round! Better luck next time!{Style.RESET_ALL}",
            "draw": f"{Fore.MAGENTA}It's a draw! 🤝{Style.RESET_ALL}",
            "reveal_hmac": "Here's the HMAC key for verification: {hmac_key}",
            "final_result_win": f"{Fore.GREEN}You won {{user_wins}} out of {{total_rounds}} rounds! 🏆{Style.RESET_ALL}",
            "final_result_lose": f"{Fore.RED}🏆 I won 2 out of 3 rounds 👎!{Style.RESET_ALL}",
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

    def validate_dice_and_faces(self, dice_count, faces_count):
        if dice_count < 2 or faces_count < 6:
            print(f"Error: You must enter at least 2 dice and 6 faces. Current values: {dice_count} dice, {faces_count} faces.")
            sys.exit(1)

    def validate_exit(self, user_input):
        if user_input.lower() == 'x':
            print("Exiting the game...")
            return True
        return False

    def validate_numeric_input(self, input_value):
        try:
            value = int(input_value)
            if value <= 0:
                print("The input must be a positive integer.")
                return None
        except ValueError:
            print("Invalid input. Please enter a number.")
            return None
        return value

    def validate_initialization(self, num_dice, num_faces):
        return self.validate_dice_faces(num_dice, num_faces)
    
    def validate_dice_selection(self, selected_dice, num_dice):
        if selected_dice < 1 or selected_dice > num_dice:
            print(f"The selected dice must be between 1 and {num_dice}.")
            return False
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

1
class ProbabilityCalculator:
    @staticmethod
    def calculate_probability(user_dice, computer_dice, trials=10000):
        user_wins, computer_wins, draws = 0, 0, 0
        
        for _ in range(trials):
            user_roll = random.choice(user_dice)
            computer_roll = random.choice(computer_dice)
            
            if user_roll > computer_roll:
                user_wins += 1
            elif user_roll < computer_roll:
                computer_wins += 1
            else:
                draws += 1
        
        total_games = user_wins + computer_wins + draws
        user_probability = (user_wins / total_games) * 100
        computer_probability = (computer_wins / total_games) * 100
        
        return user_probability, computer_probability


class ProbabilityTable:
    def __init__(self, calculator):
        self.calculator = calculator

    def generate(self, dice_sets):
        headers = [f"{Fore.CYAN}User Dice{Style.RESET_ALL}"] + [f"{Fore.CYAN}{i}{Style.RESET_ALL}" for i in range(1, len(dice_sets) + 1)]
        rows = []
        for user_dice in dice_sets.values():
            row = [f"{Fore.CYAN}{user_dice}{Style.RESET_ALL}"]
            for computer_dice in dice_sets.values():
                user_prob, computer_prob = self.calculator.calculate_probability(user_dice, computer_dice)
                row.append(f"{user_prob:.2f}% (Yours) / {computer_prob:.2f}% (Mine)" if user_dice != computer_dice else f"Draw {user_prob:.2f}%")
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
    def __init__(self, dice_set, message_handler, help_handler):
        self.dice_set = dice_set
        self.message_handler = message_handler
        self.help_handler = help_handler

    def choose_dice(self):
        print("You are choosing dice...")
        for i, dice in self.dice_set.dice_sets.items():
            print(f"🎲 ({i+1}): {dice}")
        print("(W): Winning probabilities")
        print("(X): Exit")    

        while True:
            choice = input(f"{Fore.MAGENTA}Which dice will you play? (1-{self.dice_set.dice_count}, W, X): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'x':
                print("Exiting the game...")
                sys.exit()
            elif choice == 'w':
                self.help_handler.show_probabilities(self.dice_set.dice_sets)
            elif choice.isdigit() and 1 <= int(choice) <= self.dice_set.dice_count:
                return self.dice_set.get_dice(int(choice) - 1)
            else:
                print("Invalid input, please try again.")

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
        if self.user_wins >= 2:
            print(self.message_handler.get_message("final_result_win", user_wins=self.user_wins, total_rounds=total_rounds))
        else:
            print(self.message_handler.get_message("final_result_lose", total_rounds=total_rounds))
        print(self.message_handler.get_message("reveal_hmac", hmac_key=hmac_key.hex()))


class DiceGame:
    def __init__(self, dice_count, faces_count):
        self.message_handler = MessageHandler()
        self.random_generator = RandomGenerator()
        self.hmac_key = self.random_generator.generate_hmac_key()
        self.dice_set = DiceSet(dice_count, faces_count)
        self.probability_calculator = ProbabilityCalculator()
        self.probability_table = ProbabilityTable(self.probability_calculator)
        self.help_handler = HelpHandler(self.probability_table, self.message_handler)
        self.user_turn = UserTurn(self.dice_set, self.message_handler, self.help_handler)
        self.computer_turn = ComputerTurn(self.dice_set, self.message_handler)
        self.result_handler = Result(self.message_handler)
        self.total_rounds = 3
        self.total_choices = 4

    def show_welcome(self, dice_count, faces_count):
        print(self.message_handler.get_message("welcome", dice_count=dice_count, faces_count=faces_count))

    def decide_first_move(self):
        print(self.message_handler.get_message("first_move"))
        computer_choice = self.random_generator.generate_random(self.total_choices)
        hmac_result = self.random_generator.generate_hmac(self.hmac_key, computer_choice)
        print(f"I have selected a secret value for this round. (HMAC={hmac_result})")

        while True:
            guess = input(f"{Fore.MAGENTA}Your guess: {Style.RESET_ALL}").strip().lower()
            if guess == 'x':
                sys.exit("Thanks for playing! 👋")
            if guess.isdigit() and 0 <= int(guess) <= 3:
                return "user" if int(guess) == computer_choice else "computer"
            print("Invalid input, try again.")

    def choose_dice(self, player, dice_count):
        print(f"{player} am/are choosing dice...")
        for i, dice in self.dice_set.dice_sets.items():
            print(f"🎲 ({i+1}): {dice}")
        choice = input(f"{Fore.MAGENTA}Which dice will {player} play? (1-{dice_count}): {Style.RESET_ALL}").strip()
        return self.dice_set.get_dice(int(choice) - 1)

    def roll_dice(self, player, dice):
        print(f"{player} is rolling dice: {dice}...")
        return sum(secrets.choice(dice) for _ in dice)

    def play_turn(self):
        for round_num in range(1, self.total_rounds + 1):
            print(f"\n--- Round {round_num} ---")
            first_move = self.decide_first_move()
            if first_move == "user":
                print(f"{Fore.GREEN}You go first!{Style.RESET_ALL}")
                user_dice = self.user_turn.choose_dice()
                computer_dice = self.computer_turn.choose_dice()
            else:
                print(f"{Fore.RED}I go first!{Style.RESET_ALL}")
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
    validations = GameValidations()
    validations.validate_dice_and_faces(dice_count, faces_count)
    game = DiceGame(dice_count, faces_count)
    probability_calculator = ProbabilityCalculator()
    probability_table = ProbabilityTable(probability_calculator)
    help_handler = HelpHandler(probability_table, game.message_handler)
    game.help_handler = help_handler
    game.show_welcome(dice_count, faces_count)
    game.play_turn()

import argparse
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
            "first_move": f"{Fore.MAGENTA}Let's determine who makes the first move!.{Style.RESET_ALL} Exit the game anytime (x).{Fore.YELLOW}\nGuess my selection (from 0 to 3):{Style.RESET_ALL}",
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
    
    @staticmethod
    def parse_input(input_str):
        try:
            dice_groups = input_str
            dice_sets = [list(map(int, group.split(','))) for group in dice_groups]
            return dice_sets
        except ValueError:
            raise ValueError("Input format is invalid. Please use the correct format: e.g., '3,4,7,7,4,5 7,4,5,6,3,5 8,5,8,2,3,8'")

    def validate_dice_input(self, dice_groups):
        try:
            dice_sets = self.parse_input(dice_groups)
            if len(dice_sets) < 2:
                raise ValueError("You need at least 2 dice sets to play.")
            for faces in dice_sets:
                if len(faces) < 6:
                    raise ValueError("Each dice must have at least 6 faces.")
        
                return dice_sets
        except ValueError as e:
            print(f"Error: {e}")
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
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")
            return None

    def validate_dice_selection(self, selected_dice, num_dice):
        if selected_dice < 1 or selected_dice > num_dice:
            print(f"The selected dice must be between 1 and {num_dice}.")
            return False
        return True
    
    
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


class DiceSet:
    def __init__(self, dice_sets):
        self.dice_sets = {i: dice for i, dice in enumerate(dice_sets)}
        self.dice_count = len(dice_sets)
        self.faces_count = len(dice_sets[0])

    def get_dice(self, index):
        return self.dice_sets.get(index, [])
    
class PlayerTurn:
    def __init__(self, dice_manager, message_handler, help_handler, hmac_key, player_type):
        self.dice_manager = dice_manager
        self.message_handler = message_handler
        self.help_handler = help_handler
        self.random_generator = RandomGenerator()
        self.hmac_key = hmac_key
        self.player_type = player_type

    def choose_dice(self, available_dice):
        if self.player_type == "user":
            print(f"{Fore.GREEN}Choose your dice...{Style.RESET_ALL}")
            for i, dice in enumerate(available_dice.values()):
                print(f"🎲 ({i+1}): {str(dice)}")
            print("(W): Winning probability table\n(X): Exit")

            while True:
                choice = input(f"{Fore.MAGENTA}Select dice (1-{len(available_dice)}, W, X): {Style.RESET_ALL}").strip().lower()

                if choice == 'x': 
                    sys.exit("Exiting the game...")
                if choice == 'w': 
                    self.help_handler.show_probabilities(self.dice_manager.dice_sets)
                    continue
                if choice.isdigit() and 1 <= int(choice) <= len(available_dice):
                    chosen_dice = available_dice[list(available_dice.keys())[int(choice) - 1]]
                    print(f"Chosen dice: {chosen_dice}") 
                    return chosen_dice

                print(f"{Fore.RED}Invalid input, please try again.{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}I am choosing dice...{Style.RESET_ALL}")
        chosen_dice = secrets.choice(list(available_dice.values()))
        print(f"Chosen dice: {chosen_dice}") 
        return chosen_dice


    def roll_and_calculate_mod6(self, available_dice):
        chosen_dice = self.choose_dice(available_dice)
        face_obtained = random.choice((chosen_dice)) 

        random_value = self.random_generator.generate_random(6)
        mod6_value = random_value % 6
        hmac_value = self.random_generator.generate_hmac(self.hmac_key, random_value)

        if self.player_type == "user":
            print(f"We obtain a number mod 6 between 0-5 for you: {mod6_value} (HMAC: {hmac_value})")
            result = [face_obtained + mod6_value]
            print(f"{Fore.YELLOW}Your dice: {face_obtained} Your mod6: {mod6_value}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}This is your result: {result}{Style.RESET_ALL}")
        else:
            print(f"We obtain a number mod 6 between 0-5 for me: {mod6_value} (HMAC={hmac_value})")
            result = [face_obtained + mod6_value]
            print(f"{Fore.YELLOW}My dice: {face_obtained} My Mod6: {mod6_value}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}This is my result: {result}{Style.RESET_ALL}")
        
        return result

class DiceGame:
    def __init__(self, dice_sets):
        self.message_handler = MessageHandler()
        self.random_generator = RandomGenerator()
        self.hmac_key = self.random_generator.generate_hmac_key()
        self.dice_manager = DiceSet(dice_sets)
        self.probability_calculator = ProbabilityCalculator()
        self.probability_table = ProbabilityTable(self.probability_calculator)
        self.help_handler = HelpHandler(self.probability_table, self.message_handler)
        self.user_turn = PlayerTurn(self.dice_manager, self.message_handler, self.help_handler, self.hmac_key, "user")
        self.computer_turn = PlayerTurn(self.dice_manager, self.message_handler, self.help_handler, self.hmac_key, "computer")
        self.result_handler = Result(self.message_handler)
        self.total_rounds = 3
        self.total_choices = 4

    def start(self):
        available_dice = self.dice_manager.dice_sets.copy()
        dice_count = self.dice_manager.dice_count
        faces_count = self.dice_manager.faces_count
        self.show_welcome(dice_count, faces_count)
        self.play_turn(available_dice)

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
            if guess.isdigit():
                guess_num = int(guess)
                if 0 <= guess_num <= 3:
                    if guess_num == computer_choice:
                        print(f"{Fore.GREEN}You will make the first move!{Style.RESET_ALL}")
                        return "user"
                    else:
                        print(f"{Fore.RED}I will make the first move!{Style.RESET_ALL}")
                        return "computer"
                else:
                    print("Invalid choice. Please select a number between 0 and 3.")
            else:
                print("Invalid input, try again.")

    
    def play_turn(self, available_dice):
        for round_number in range(self.total_rounds):
            print(f"\n{Fore.YELLOW}--- Round {round_number + 1} ---{Style.RESET_ALL}")

            first_player = self.decide_first_move()

            if first_player == "user":
                user_roll = self.user_turn.roll_and_calculate_mod6(available_dice)
                computer_roll = self.computer_turn.roll_and_calculate_mod6(available_dice)
            else:
                computer_roll = self.computer_turn.roll_and_calculate_mod6(available_dice)
                user_roll = self.user_turn.roll_and_calculate_mod6(available_dice)

            self.result_handler.evaluate(user_roll, computer_roll)

        self.result_handler.display_final_result(self.total_rounds, self.hmac_key)
        self.replay_or_exit()

    def replay_or_exit(self):
        replay = input(self.message_handler.get_message("replay")).strip().lower()
        if replay == 'y':
            self.user_wins = 0
            self.computer_wins = 0
            available_dice = self.dice_manager.dice_sets
            self.play_turn(available_dice)
        else:
            print("Thanks for playing! 👋")
            sys.exit()

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play the General Non-Transitive Dice Game')
    parser.add_argument('dice_sets', nargs='+', help='List of dice sets (e.g., "3,4,7,7,4 7,4,5,6,3,5 8,5,8,2,3,8")')
    args = parser.parse_args()

    validations = GameValidations()
    dice_sets = validations.validate_dice_input((args.dice_sets))

    game = DiceGame(dice_sets)
    game.start()


import hmac
import hashlib
import os
import sys
import secrets


class MessageHandler:
    def __init__(self):
        self.messages = {
            "welcome": "🎲 Welcome to the Dice Game! 🎲",
            "win": "🏆 Unstoppable! The dice are with you!",
            "lose": "😢 Tough luck! Try again and beat the odds.",
            "draw": "🤝 It's a tie! The dice have spoken.",
            "replay": "Press Enter to play again or X to exit.",
            "first_move": "The first move will be made by: {player}",
            "probability_help": "Press '?' to see the probability table."

        }

    def get_message(self, message_type, **kwargs):
        return self.messages.get(message_type, "").format(**kwargs)

class RandomNumberGenerator:
    def __init__(self):
        self.secret_key = os.urandom(32) # 256-bit random key

    def generate_random_number(self, max_value):
        return secrets.randbelow(max_value)

    def calculate_hmac(self, random_number):
        hmac_obj = hmac.new(self.secret_key, str(random_number).encode(), hashlib.sha3_256)
        return hmac_obj.hexdigest()

    def get_secret_key(self):
        return self.secret_key.hex()
    
class Dice:
    def __init__(self, dice_set):
        self.dice_set = dice_set

    def get_dice(self):
        return self.dice_set
    
class ProbabilityCalculator:
    def calculate_win_probability(self, user_dice, computer_dice):
        user_wins = sum(1 for u, c in zip(user_dice, computer_dice) if u > c)
        total_possibilities = len(user_dice) * len(computer_dice)
        return user_wins / total_possibilities if total_possibilities > 0 else 0
    
class ProbabilityTable:
    def __init__(self, probability_calculator):
        self.probability_calculator = probability_calculator

    def generate_probability_table(self, all_dice_combinations):

        header = "| User dice   | Computer 1  | Computer 2  |"
        separator = "+-------------+-------------+-------------+"
        
        rows = [
            f"| {user_dice} | " + " | ".join(f"{self.probability_calculator.calculate_win_probability(user_dice, computer_dice):.4f}" for computer_dice in all_dice_combinations) + " |"
            for user_dice in all_dice_combinations
        ]
        
        return "\n".join([separator, header, separator] + rows + [separator])
    
class HelpHandler:
    def __init__(self, probability_calculator):
        self.probability_calculator = probability_calculator

    def display_probability_table(self, all_dice_combinations):
        print(self.probability_calculator.generate_probability_table(all_dice_combinations))

    def offer_win_probability(self):
        user_input = input(self.message_handler.get_message("probability_help"))
        if user_input.lower() == 'w':
            # Show the probability table
            self.display_probability_table(DiceGame().dice_sets)
        elif user_input.lower() == 'x':
            print("Exiting the game. Thanks for playing!")
            sys.exit(0)
        else:
            print(self.message_handler.get_message("invalid_input"))
            self.offer_win_probability()

class DiceGame:
    def __init__(self):
        self.message_handler = MessageHandler()
        self.random_generator = RandomNumberGenerator()
        self.show_welcome_message = True
        self.help_handler = None
        self.dice_sets = [
            [2, 2, 4, 4, 9, 9],
            [6, 8, 1, 1, 8, 6],
            [7, 5, 3, 7, 5, 3]

        ]

    def choose_dice(self, player_name="Player"):
        print("Choose your dice:")
        for i, dice_set in enumerate(self.dice_sets):
            print(f"{i} - {dice_set}")
        print("X - exit\nW - Show your chances to win")

        while True:
            user_choice = input(f"{player_name} selection: ").strip().lower()

            if user_choice == 'x': sys.exit("Thanks for playing! Goodbye! 👋")
            if user_choice == 'w': self.help_handler.offer_win_probability(); continue
            if user_choice.isdigit() and 0 <= int(user_choice) < len(self.dice_sets): return self.dice_sets[int(user_choice)]
            print("Invalid input. Please enter a number, X to exit.")


    def guess_number(self, player_name="Player"):
        print("\nChoose your number modulo 6.\n0 - 0\n1 - 1\n2 - 2\n3 - 3\n4 - 4\n5 - 5\nX - exit\n")

        while True:
            user_guess = input(f"{player_name} selection was: ").strip().lower()
            
            if user_guess == 'x': sys.exit("Thanks for playing! Goodbye! 👋")
            if user_guess == 'w': self.help_handler.offer_win_probability(); continue
            if user_guess.isdigit() and 0 <= int(user_guess) <= 5: return int(user_guess)
            
            print("Invalid input. Please enter a number between 0 and 5, X to exit.")


    def validate_arguments(self, args):
        if len(args) != 3:
            return False, "You must provide two arguments: number of dice and number of faces per dice. Example: python game.py 3 6"
        try:
            num_dice = int(args[1])
            num_faces = int(args[2])
            
            if num_dice <= 2 or num_faces <= 6:
                return False, "Number of dice must be greater than 2 and number of faces must be greater than 6."
            
        except ValueError:
            return False, "Both arguments must be integers."
        
        return True, (num_dice, num_faces) 
    
    def show_welcome(self):
        if self.show_welcome_message:
            print(self.message_handler.get_message("welcome"))
            self.show_welcome_message = False  # Don't show welcome again

        print("\nLet's get started!")


    def first_move(self):
        random_choice = self.random_generator.generate_random_number(2)
        print(f"\nI selected a random value in the range 0..1 (HMAC={self.random_generator.calculate_hmac(random_choice)}).")
        print("This value will determine who makes the first move.")

        user_guess = self.guess_number("Your")
        print(f"\nThe final result is: {(random_choice + user_guess) % 6} (mod 6)")

        dice_owner = "Computer" if random_choice == 0 else "You"
        dice = self.choose_dice(dice_owner)
        print(f"{dice_owner} makes the first move! I choose the {dice} dice." if random_choice == 0 else f"You make the first move! You choose the {dice} dice.")
        
        return random_choice, user_guess, dice


    def play_game(self):
        self.show_welcome()
        selected_dice = self.first_move()

        computer_choice = self.random_generator.generate_random_number(6)
        print(f"My number is {computer_choice} (HMAC={self.random_generator.calculate_hmac(computer_choice)})")

        user_dice = selected_dice
        computer_dice = self.choose_dice("Computer")
        print(f"User dice: {user_dice}\nComputer dice: {computer_dice}")

        win_probability = ProbabilityCalculator().calculate_win_probability(user_dice, computer_dice)
        print(f"Probability of user winning: {win_probability:.4f}")

        result = "win" if sum(user_dice) > sum(computer_dice) else "lose" if sum(user_dice) < sum(computer_dice) else "draw"
        print(self.message_handler.get_message(result))

        self.replay_or_exit()


    def replay_or_exit(self):
        user_input = input("\n" + self.message_handler.get_message("replay"))

        if user_input == '': self.play_game()  # Replay
        elif user_input == 'x': print("Thanks for playing! Goodbye! 👋")
        else: print("Invalid input. Please press Enter to play again or X to Exit.") or self.replay_or_exit()


if __name__ == "__main__":
    game = DiceGame()
    probability_calculator = ProbabilityCalculator()
    probability_table = ProbabilityTable(probability_calculator)
    help_handler = HelpHandler(probability_table)
    game.help_handler = help_handler

    validation_result, message = game.validate_arguments(sys.argv)
    if not validation_result:
        print(message)
        sys.exit(1)

    game.play_game()

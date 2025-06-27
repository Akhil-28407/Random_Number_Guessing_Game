import random

def generate_random_number():
    
    return random.randint(1, 100)

a= generate_random_number()
print("\nWelcome to the Number Guessing Game!")
print("This Game is created by Akhil-28407")
print("\n")



while True:
    user_guess= int(input("Guess a number between 1 and 100: "))
    if user_guess<1 or user_guess>100:
        print("Please enter a number between 1 and 100.")
        continue
    if user_guess == a:
        print("Congratulations! You've guessed the right number.")
        break
    elif user_guess < a:
        print("Too low! Try again.")
    else:
        print("Too high! Try again.")

print("Game Over! The number was:", a)
print("Thanks for playing!")
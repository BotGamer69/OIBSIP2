import random
import string

def generate_password(length, use_letters, use_numbers, use_symbols):
    character_pool = ''
    if use_letters:
        character_pool += string.ascii_letters  # a-z + A-Z
    if use_numbers:
        character_pool += string.digits         # 0-9
    if use_symbols:
        character_pool += string.punctuation    # !@#$%^&*()_+ etc.

    if not character_pool:
        print("Error: No character types selected. Cannot generate password.")
        return None

    return ''.join(random.choice(character_pool) for _ in range(length))


def main():
    print("=== Password Generator ===")
    try:
        length = int(input("Enter desired password length: "))
        if length <= 0:
            raise ValueError

        use_letters = input("Include letters? (y/n): ").lower() == 'y'
        use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
        use_symbols = input("Include symbols? (y/n): ").lower() == 'y'

        password = generate_password(length, use_letters, use_numbers, use_symbols)
        if password:
            print(f"\nGenerated Password: {password}")
    except ValueError:
        print("Invalid input. Please enter a positive integer for length.")

if __name__ == "__main__":
    main()

import random, os

player = []

class Player():
    def __init__(self, username, password):
        self.username = username # Required to login
        self.password = password # Required to login
        self.level = 1
        self.hp = 1000
        self.mana = 500
        self.attack = 100
        self.defense = 300
        self.evasion = 15
        self.weapon = "None"
        self.inventory = {}
        self.stash = []
    
    def check_username(self):
        return self.username
    
    def check_password(self):
        return self.password
    
    def check_level(self):
        return self.level
    
    
def main_menu(playerid):
    while True:
        print("---------------------------")
        print(Player.check_username(playerid), "- Level", Player.check_level(playerid))
        print("---------------------------")
        print("1. My Stats")
        print("2. My Inventory")
        print("3. My Stash")
        print("4. Logout")
        choice = input("Enter your choice: ")

        if choice == "1":
            os.system("cls")
            print("Stats")
        elif choice == "4":
            os.system("cls")
            break
    print("Account logged out!")
    logged_out()


def create_account():
    os.system("cls")
    print("---------------------")
    print("Create a new account!")
    print("---------------------")
    username = input("Enter your username: ")
    if len(player) > 0:
        for i in range(len(player)):
            if Player.check_username(player[i]) == username:
                print("Username already exists!")
                input("Press Enter to continue...")
                os.system("cls")
                return
    password = input("Enter your password: ")
    new_player = Player(username, password)
    player.append(new_player)
    input("Account created! Press Enter to continue...")
    os.system("cls")
    return 


def login():
    if len(player) == 0:
        print("\nNo account available to login!")
        input("Press Enter to continue...")
        os.system("cls")
        return
    else:
        os.system("cls")
        print("--------------------------")
        print("Login to existing account!")
        print("--------------------------")
        found = False
        playerid = ""
        username = input("Enter your username: ")
        for i in range(len(player)):
            if Player.check_username(player[i]) == username:
                print("Account found!")
                found = True
                playerid = player[i]
                break
        if not found:
            print("Account not found!")
            input("Press Enter to continue...")
            os.system("cls")
            return
        else:
            while True:
                password = input("Enter your password (Enter C to cancel): ")
                if Player.check_password(playerid) == password: 
                    print("\nYou successfully logged in!")
                    input("Press Enter to continue...")
                    os.system("cls")
                    return playerid
                elif password == "c" or password == "C":
                    print("Canceled!")
                    input("Press Enter to continue...")
                    os.system("cls")
                    return
                else:
                    print("Wrong Password!")


def logged_out():
    playerid = ""
    while True:
        print("----------------------")
        print("Welcome to Mython RPG!")
        print("----------------------")
        print("1. Login to existing account")
        print("2. Create a new account")
        print("3. Exit Game")
        choice = input("Enter your choice: ")
        if choice == "1":
            playerid = login()
            if playerid in player:
                break
        elif choice == "2":
            create_account()
        elif choice == "3":
            print("\nExiting program...\n")
            break
        else:
            os.system("cls")
            print("\nError: Invalid input!\n")
    
    if playerid in player:
        main_menu(playerid)
            

# Initialize Program
logged_out()
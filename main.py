import random

MAX_HAND_SIZE = 7

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

class Card:
    def __init__(self, name, card_type, power):
        self.name = name
        self.card_type = card_type
        self.power = power

    def __str__(self):
        return f"{self.name} [{self.card_type} - {self.power}]"

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.hand = []

    def draw_card(self, shared_deck, shared_discard, opponent):
        if not shared_deck and not shared_discard:
            if self.hand:
                print(f"\nNo cards in deck or discard pile! Forcing {self.name} to discard a card...")
                card = random.choice(self.hand)
                self.hand.remove(card)
                shared_discard.append(card)
                print(f"{self.name} discarded {BLUE if card.card_type == 'Defense' else RED}{card}{ENDC} to the shared discard pile.")
            elif opponent.hand:
                print(f"\nNo cards in deck or discard pile! Forcing {opponent.name} to discard a card...")
                card = random.choice(opponent.hand)
                opponent.hand.remove(card)
                shared_discard.append(card)
                print(f"{opponent.name} discarded {BLUE if card.card_type == 'Defense' else RED}{card}{ENDC} to the shared discard pile.")
            else:
                print("No cards available in any hands, deck, or discard pile! This should not happen.")
                return

        if not shared_deck and shared_discard:
            print(f"\nShared deck is empty! Reshuffling discard pile...")
            random.shuffle(shared_discard)
            shared_deck.extend(shared_discard)
            shared_discard.clear()

        if shared_deck:
            card = shared_deck.pop(0)
            self.hand.append(card)
            print(f"{self.name} drew card: {BLUE if card.card_type == 'Defense' else RED}{card}{ENDC}")
        else:
            print("Failed to draw a card due to an unexpected error.")

    def discard_card(self, shared_discard):
        if self.name == "Computer":
            if self.hand:
                card = random.choice(self.hand)
                self.hand.remove(card)
                shared_discard.append(card)
                print(f"{self.name} discarded {BLUE if card.card_type == 'Defense' else RED}{card}{ENDC}")
            else:
                print(f"{self.name} has no cards to discard.")
        else:
            if self.hand:
                print(f"\n{self.name}, choose a card to discard:")
                for i, card in enumerate(self.hand):
                    color = RED if card.card_type == "Attack" else BLUE
                    print(f"  {i + 1}: {color}{card}{ENDC}")
                choice = input("Enter the number of the card to discard: ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.hand):
                        discarded = self.hand.pop(idx)
                        shared_discard.append(discarded)
                        print(f"{self.name} discarded {BLUE if discarded.card_type == 'Defense' else RED}{discarded}{ENDC}")
                    else:
                        print("Invalid selection. No card discarded.")
                except ValueError:
                    print("Invalid input. No card discarded.")
            else:
                print("No cards to discard.")

    def show_hand(self):
        print(f"\n{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            color = RED if card.card_type == "Attack" else BLUE
            print(f"  {i + 1}: {color}{card}{ENDC}")

    def calculate_risk(self):
        """Risk is assessed as (sum of attack card powers) minus (sum of defense card powers)."""
        attack_sum = sum(card.power for card in self.hand if card.card_type == "Attack")
        defense_sum = sum(card.power for card in self.hand if card.card_type == "Defense")
        risk_score = attack_sum - defense_sum
        return risk_score

def risk_assessment(player):
    """Prints out the risk score and a qualitative label based on the player's hand."""
    risk_score = player.calculate_risk()
    if risk_score > 10:
        level = "High"
        color = RED
    elif risk_score < -10:
        level = "Low"
        color = GREEN
    else:
        level = "Moderate"
        color = YELLOW
    print(f"\n{player.name}'s risk assessment: {color}{risk_score} ({level} Risk){ENDC}")
    return risk_score

def apply_risk_effect(player):
    """Applies health effects based on risk score."""
    risk = player.calculate_risk()
    if risk > 10:
        print(f"{player.name}'s risk is high! Taking 5 damage.")
        player.health -= 5
    elif risk < -10:
        print(f"{player.name}'s risk is low! Gaining 5 health.")
        player.health = min(player.health + 5, 100)

def attack_action(attacker, defender, card, shared_discard):
    print(f"\n{attacker.name} plays attack card: {RED}{card}{ENDC}")
    shared_discard.append(card) 
    defense_cards = [c for c in defender.hand if c.card_type == "Defense"]
    if defense_cards:
        if defender.name == "Computer":
            best_defense = max(defense_cards, key=lambda c: c.power)
            print(f"{defender.name} defends with {BLUE}{best_defense}{ENDC}")
            damage = max(card.power - best_defense.power, 0)
            defender.health -= damage
            defender.hand.remove(best_defense)
            shared_discard.append(best_defense)  
        else:
            print("You have defense cards that can reduce the damage.")
            option = input("Do you want to use a defense card? (y/n): ")
            if option.lower() == 'y':
                available = [c for c in defender.hand if c.card_type == "Defense"]
                print("Select a defense card to play:")
                for i, c in enumerate(available):
                    print(f"  {i + 1}: {BLUE}{c}{ENDC}")
                choice = input("Enter the number: ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available):
                        chosen_defense = available[idx]
                        damage = max(card.power - chosen_defense.power, 0)
                        defender.health -= damage
                        defender.hand.remove(chosen_defense)
                        shared_discard.append(chosen_defense) 
                        print(f"You defended with {BLUE}{chosen_defense}{ENDC}. Damage taken: {damage}")
                    else:
                        print("Invalid selection. You take full damage.")
                        defender.health -= card.power
                except ValueError:
                    print("Invalid input. You take full damage.")
                    defender.health -= card.power
            else:
                print("No defense played. You take full damage.")
                defender.health -= card.power
    else:
        print(f"{defender.name} has no defense cards! Taking full damage of {card.power}.")
        defender.health -= card.power
    print(f"{defender.name}'s health is now {GREEN if defender.health > 50 else RED}{defender.health}{ENDC}")

def defense_action(player, card, shared_discard):
    """Playing a defense card gives a self-boost (half the card's power)."""
    print(f"\n{player.name} plays defense card for a self-boost: {BLUE}{card}{ENDC}")
    shared_discard.append(card)  
    boost = card.power // 2
    player.health = min(player.health + boost, 100)
    print(f"{player.name}'s health increases by {boost} to {GREEN if player.health > 50 else RED}{player.health}{ENDC}")

def player_turn(player, opponent, shared_deck, shared_discard):
    print("\n---- Your Turn ----")
    if len(player.hand) > MAX_HAND_SIZE:
        print("\nYour hand exceeds the maximum allowed size!")
        player.discard_card(shared_discard)

    print("\nChoose an action:")
    print(f"  1: Draw a card")
    print(f"  2: Play a card")
    print(f"  3: Discard a card")
    print(f"  4: Assess risk")
    print(f"  5: Show hand")
    choice = input("Enter your choice (1-5): ")

    if choice == "1":
        player.draw_card(shared_deck, shared_discard, opponent)
    elif choice == "2":
        if not player.hand:
            print("No cards in hand to play!")
        else:
            player.show_hand()
            selection = input("Select a card to play by entering its number: ")
            try:
                index = int(selection) - 1
                if 0 <= index < len(player.hand):
                    card = player.hand.pop(index)
                    if card.card_type == "Attack":
                        attack_action(player, opponent, card, shared_discard)
                    elif card.card_type == "Defense":
                        decision = input("Use this defense card to boost your health? (y/n): ")
                        if decision.lower() == "y":
                            defense_action(player, card, shared_discard)
                        else:
                            print("Defense card discarded without effect.")
                            shared_discard.append(card)
                    else:
                        print("Invalid card type played.")
                else:
                    print("Invalid card selection.")
            except ValueError:
                print("Invalid input. Turn skipped.")
    elif choice == "3":
        player.discard_card(shared_discard)
    elif choice == "4":
        risk_assessment(player)
    elif choice == "5":
        player.show_hand()
    else:
        print("Invalid action. Turn skipped.")
    
    apply_risk_effect(player)

def computer_turn(computer, opponent, shared_deck, shared_discard):
    print("\n---- Computer's Turn ----")
    if len(computer.hand) > MAX_HAND_SIZE:
        print("Computer's hand is too large; discarding one card.")
        computer.discard_card(shared_discard)

    attack_cards = [c for c in computer.hand if c.card_type == "Attack"]
    defense_cards = [c for c in computer.hand if c.card_type == "Defense"]

    if opponent.health < 30 and attack_cards:
        card = max(attack_cards, key=lambda c: c.power)
        computer.hand.remove(card)
        attack_action(computer, opponent, card, shared_discard)
    elif computer.health < 50 and defense_cards:
        card = random.choice(defense_cards)
        computer.hand.remove(card)
        defense_action(computer, card, shared_discard)
    else:
        if shared_deck or shared_discard or computer.hand or opponent.hand:
            computer.draw_card(shared_deck, shared_discard, opponent)
        else:
            if attack_cards:
                card = random.choice(attack_cards)
                computer.hand.remove(card)
                attack_action(computer, opponent, card, shared_discard)
            elif defense_cards:
                card = random.choice(defense_cards)
                computer.hand.remove(card)
                defense_action(computer, card, shared_discard)
            else:
                print("Computer skips its turn.")
    
    apply_risk_effect(computer)

def print_game_state(player, computer, shared_deck, shared_discard):
    print("\nCurrent Game State:")
    player_health_color = GREEN if player.health > 50 else RED
    computer_health_color = GREEN if computer.health > 50 else RED
    print(f"Your Health: {player_health_color}{player.health}{ENDC}")
    print(f"Computer's Health: {computer_health_color}{computer.health}{ENDC}")
    print(f"Your Hand: {len(player.hand)} cards")
    print(f"Computer's Hand: {len(computer.hand)} cards")
    print(f"Shared Deck: {len(shared_deck)} cards")
    print(f"Shared Discard Pile: {len(shared_discard)} cards")

def build_deck():
    """Creates a deck containing two copies each of attack and defense cards."""
    master_cards = [
        Card("Phishing", "Attack", 15),
        Card("SQL Injection", "Attack", 20),
        Card("DoS Attack", "Attack", 25),
        Card("XSS Attack", "Attack", 18),
        Card("Man-in-the-Middle", "Attack", 22),
        Card("Firewall", "Defense", 15),
        Card("Access Control", "Defense", 20),
        Card("Security Training", "Defense", 10),
        Card("Network Monitoring", "Defense", 18),
        Card("Malware Protection", "Defense", 20)
    ]
    deck = []
    for card in master_cards:
        deck.append(Card(card.name, card.card_type, card.power))
        deck.append(Card(card.name, card.card_type, card.power))
    random.shuffle(deck)
    return deck

def main():
    print("Welcome to the Cybersecurity Card Game!")
    print("--------------------------------------------------")
    print("Game Instructions:")
    print(" - You and the computer start with 100 security health points.")
    print(" - You draw from a shared deck of Attack and Defense cards themed around cybersecurity.")
    print(" - Played or discarded cards go to a shared discard pile, reshuffled into the deck when empty.")
    print(" - If no cards are available, a card is automatically discarded from a player's hand to continue play.")
    print(" - On your turn, you can draw a card, play a card, discard a card, assess your risk, or show your hand.")
    print("   * Attack cards deal damage to your opponent, who may defend to reduce damage.")
    print("   * Defense cards boost your health by half their power when played independently.")
    print("   * Your hand size is limited to", MAX_HAND_SIZE, "cards. Excess cards must be discarded.")
    print("   * Risk is calculated as (sum of attack card powers) - (sum of defense card powers).")
    print("   * High risk (>10) deals 5 damage; low risk (<-10) heals 5 health per turn.")
    print(" - The goal is to reduce your opponent's security health to zero while managing risk.")
    print(" - Enjoy the game and manage your resources wisely!")
    print("--------------------------------------------------\n")
    input("Press Enter to start the game...")

    shared_deck = build_deck()
    shared_discard = []

    player = Player("Player")
    computer = Player("Computer")

    for _ in range(3):
        player.draw_card(shared_deck, shared_discard, computer)
        computer.draw_card(shared_deck, shared_discard, player)

    while player.health > 0 and computer.health > 0:
        print_game_state(player, computer, shared_deck, shared_discard)
        player_turn(player, computer, shared_deck, shared_discard)
        if computer.health <= 0:
            break
        computer_turn(computer, player, shared_deck, shared_discard)
        print("\n-------------------------")
        print(f"Status Update: Your Health: {GREEN if player.health > 50 else RED}{player.health}{ENDC} | "
              f"Computer Health: {GREEN if computer.health > 50 else RED}{computer.health}{ENDC}")
        print("-------------------------\n")

    if player.health > 0:
        print("\nCongratulations! You’ve secured your network and defeated the attacker!")
        print("--- Game Over ---")
    else:
        print("\nYour network has been compromised! The attacker prevails.")
        print("--- Game Over ---")

if __name__ == "__main__":
    main()

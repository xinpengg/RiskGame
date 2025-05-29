import random

MAX_HAND_SIZE = 7


class Card:
    def __init__(self, name, card_type, power):
        self.name = name
        self.card_type = card_type
        self.power = power

    def __str__(self):
        return f"{self.name} [{self.card_type} - {self.power}]"


class Player:
    def __init__(self, name, deck):
        self.name = name
        self.health = 100
        self.deck = deck
        self.hand = []

    def draw_card(self):
        if self.deck:
            card = self.deck.pop(0)
            self.hand.append(card)
            print(f"{self.name} drew card: {card}")
        else:
            print(f"{self.name} has no more cards to draw.")

    def discard_card(self):
        if self.hand:
            print(f"\n{self.name}, choose a card to discard:")
            for i, card in enumerate(self.hand):
                print(f"  {i + 1}: {card}")
            choice = input("Enter the number of the card to discard: ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.hand):
                    discarded = self.hand.pop(idx)
                    print(f"{self.name} discarded {discarded}")
                else:
                    print("Invalid selection. No card discarded.")
            except:
                print("Invalid input. No card discarded.")
        else:
            print("No cards to discard.")

    def show_hand(self):
        print(f"\n{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            print(f"  {i + 1}: {card}")

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
    elif risk_score < -10:
        level = "Low"
    else:
        level = "Moderate"
    print(f"\n{player.name}'s risk assessment: {risk_score} ({level} Risk)")
    return risk_score


def attack_action(attacker, defender, card):
    print(f"\n{attacker.name} plays attack card: {card}")
    defense_cards = [c for c in defender.hand if c.card_type == "Defense"]
    if defense_cards:
        if defender.name == "Computer":
            best_defense = max(defense_cards, key=lambda c: c.power)
            print(f"{defender.name} defends with {best_defense}")
            damage = max(card.power - best_defense.power, 0)
            defender.health -= damage
            defender.hand.remove(best_defense)
        else:
            print("You have defense cards that can reduce the damage.")
            option = input("Do you want to use a defense card? (y/n): ")
            if option.lower() == 'y':
                available = [c for c in defender.hand if c.card_type == "Defense"]
                print("Select a defense card to play:")
                for i, c in enumerate(available):
                    print(f"  {i + 1}: {c}")
                choice = input("Enter the number: ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available):
                        chosen_defense = available[idx]
                        damage = max(card.power - chosen_defense.power, 0)
                        defender.health -= damage
                        defender.hand.remove(chosen_defense)
                        print(f"You defended with {chosen_defense}. Damage taken: {damage}")
                    else:
                        print("Invalid selection. You take full damage.")
                        defender.health -= card.power
                except:
                    print("Invalid input. You take full damage.")
                    defender.health -= card.power
            else:
                print("No defense played. You take full damage.")
                defender.health -= card.power
    else:
        print(f"{defender.name} has no defense cards! Taking full damage of {card.power}.")
        defender.health -= card.power
    print(f"{defender.name}'s health is now {defender.health}")


def defense_action(player, card):
    """
    When playing a defense card independent of an attack, it gives a self-boost.
    The boost is half the card's power.
    """
    print(f"\n{player.name} plays defense card for a self-boost: {card}")
    boost = card.power // 2
    player.health += boost
    print(f"{player.name}'s health increases by {boost} to {player.health}")


def player_turn(player, opponent):
    print("\n---- Your Turn ----")
    print(f"Your Health: {player.health}")
    risk_assessment(player)

    if len(player.hand) > MAX_HAND_SIZE:
        print("\nYour hand exceeds the maximum allowed size!")
        player.discard_card()

    print("\nChoose an action:")
    print("  1: Draw a card")
    print("  2: Play a card")
    print("  3: Discard a card")
    print("  4: Assess risk")
    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        player.draw_card()
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
                        attack_action(player, opponent, card)
                    elif card.card_type == "Defense":
                        decision = input("Do you want to use this defense card to boost your health? (y/n): ")
                        if decision.lower() == "y":
                            defense_action(player, card)
                        else:
                            print("You decided not to activate the defense effect. (Card is discarded.)")
                    else:
                        print("Invalid card type played.")
                else:
                    print("Invalid card selection.")
            except:
                print("Invalid input.")
    elif choice == "3":
        player.discard_card()
    elif choice == "4":
        risk_assessment(player)
    else:
        print("Invalid action. Turn skipped.")


def computer_turn(computer, opponent):
    print("\n---- Computer's Turn ----")
    if len(computer.hand) > MAX_HAND_SIZE:
        print("Computer's hand is too large; discarding one card.")
        computer.discard_card()

    attack_cards = [c for c in computer.hand if c.card_type == "Attack"]
    defense_cards = [c for c in computer.hand if c.card_type == "Defense"]

    if attack_cards and random.random() < 0.7:
        card = random.choice(attack_cards)
        computer.hand.remove(card)
        attack_action(computer, opponent, card)
    elif defense_cards and random.random() < 0.5:
        card = random.choice(defense_cards)
        computer.hand.remove(card)
        defense_action(computer, card)
    else:
        if computer.deck:
            computer.draw_card()
        else:
            if attack_cards:
                card = random.choice(attack_cards)
                computer.hand.remove(card)
                attack_action(computer, opponent, card)
            elif defense_cards:
                card = random.choice(defense_cards)
                computer.hand.remove(card)
                defense_action(computer, card)
            else:
                print("Computer skips its turn.")


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
    print(" - Your deck is composed of Attack and Defense cards themed around cybersecurity.")
    print(" - On your turn, you can choose to draw a card, play a card, discard a card, or assess your risk.")
    print(
        "   * When playing an Attack card, your opponent may defend with one of their defense cards to reduce damage.")
    print("   * Playing a Defense card gives you a self-boost (increases health by half the card's power).")
    print(" - Your hand size is limited to", MAX_HAND_SIZE,
          "cards. If you exceed this limit, you will need to discard a card.")
    print(" - The goal is to reduce your opponent's security health to zero while managing the risk in your hand.")
    print(" - Enjoy the game and manage your resources wisely!")
    print("--------------------------------------------------\n")

    deck = build_deck()
    half = len(deck) // 2
    player_deck = deck[:half]
    computer_deck = deck[half:]

    player = Player("Player", player_deck)
    computer = Player("Computer", computer_deck)

    for _ in range(3):
        player.draw_card()
        computer.draw_card()

    while player.health > 0 and computer.health > 0:
        player_turn(player, computer)
        if computer.health <= 0:
            break
        computer_turn(computer, player)
        print("\n-------------------------")
        print(f"Status Update: Your Health: {player.health} | Computer Health: {computer.health}")
        print("-------------------------\n")

    if player.health > 0:
        print("\nCongratulations! You have secured your network and defeated the computer attacker!")
    else:
        print("\nYour network has been compromised! The computer attacker has taken down your security.")


if __name__ == "__main__":
    main()

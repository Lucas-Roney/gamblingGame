from deck import *
from chips import *

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    def total(self):
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == "A":
                aces += 1
            total += card.value
                
        while total > 21 and aces > 0:
             total -= 10
             aces -= 1

        return total
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.total() == 21
            
    def is_bust(self):
        return self.total() > 21
    
    def is_soft(self):
        if not any(card.rank == "A" for card in self.cards):
            return False
        hard_total = sum(card.value for card in self.cards)
        adjusted_total = self.total()
        return hard_total == adjusted_total

class BlackjackGame:
    def __init__(self, num_decks=1):
        self.deck = Deck(num_decks)
        self.player = Hand()
        self.dealer = Hand()
        self.in_round = False
        
        self.player_money = 1000
        self.current_bet = 0
        
        
    def start_round(self):
        self.in_round = True
        
        # Reset hands
        self.player = Hand()
        self.dealer = Hand()
        
        # Reshuffling if needed
        if len(self.deck.cards) < 13:
            self.deck = Deck(1)
        self.deck.shuffle()
        
        # Deal initial cards
        self.dealer.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        
        #Check for BJ
        if self.player.is_blackjack():
            if self.dealer.is_blackjack():
                return "push"
            else:
                return "player_blackjack"
        
        elif self.dealer.is_blackjack():
            return "dealer_blackjack"
        
        else:
            return "continue"
        
    def player_hit(self):
        # Deal the player a card
        self.player.add_card(self.deck.deal())
        
        #Check for bust
        if self.player.is_bust():
            return "player_bust"
        return "continue"
    
    def player_stand(self):
        return self.dealer_play()
    
    def player_double(self):
        # Player doubles their bet
        if self.player_money >= self.current_bet:
            self.player_money -= self.current_bet
            self.current_bet *= 2
        else:
            return "not_enough"

        # Deal only one card
        self.player.add_card(self.deck.deal())

        # Check bust
        if self.player.is_bust():
            return "player_bust"

        # Otherwise dealer plays
        return self.dealer_play()
        
    def dealer_play(self):
        while self.dealer.total() < 17:
            self.dealer.add_card(self.deck.deal())
        
        if self.dealer.total() > 21:
            return "dealer_bust"
        
        # Check for winner when game concludes
        return self.determine_winner()
        
    def determine_winner(self):
        p = self.player.total()
        d = self.dealer.total()
        
        if p > d:
            return "player_win"
        elif p < d:
            return "dealer_win"
        return "push"
    
    def place_bet(self, amount):
        # Check if amount is available
        if amount > self.player_money:
            return False
        
        # Take money and add to bet
        self.player_money -= amount
        self.current_bet = amount
        return True

    def payout(self, result):
        if result == "player_win":
            self.player_money += self.current_bet * 2
        elif result == "push":
            self.player_money += self.current_bet
        elif result == "player_blackjack":
            self.player_money += int(self.current_bet * 2.5)
            
        # Reset bet after payout
        self.current_bet = 0

    def reset_round(self):
        self.current_bet = 0
        self.in_round = False

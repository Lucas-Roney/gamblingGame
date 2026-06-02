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
        
    def start_round():
        
import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit  
        if rank == "A":
            self.value = 11
        elif rank == "J" or rank == "Q" or rank == "K":
            self.value = 10
        else:
            self.value = int(rank)

            
class Deck:
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    SUITS = ["S", "C", "D", "H"]

    def __init__(self, num_decks=1):
        self.cards = []
        for _ in range(num_decks):
            for rank in Deck.RANKS:
                for suit in Deck.SUITS:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

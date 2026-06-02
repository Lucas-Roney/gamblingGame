class ChipBank:
    def __init__(self, starting_amount):
        self.balance = starting_amount

    def can_bet(self, amount):
        return self.balance >= amount

    def add(self, amount):
        self.balance += amount

    def subtract(self, amount):
        self.balance -= amount

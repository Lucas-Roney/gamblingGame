import pygame
from blackjack import BlackjackGame
from buttons import Button

class BlackjackUI:
    def __init__(self, screen):
        self.screen = screen
        self.game = BlackjackGame()
        self.in_betting_phase = True

        # Betting buttons
        self.bet_buttons = {
            5: Button(780, self.screen.get_height() - 100, 80, 60, "$5"),
            10: Button(900, self.screen.get_height() - 100, 80, 60, "$10"),
            20: Button(1020, self.screen.get_height() - 100, 80, 60, "$20"),
            50: Button(1160, self.screen.get_height() - 100, 80, 60, "$50"),
        }

        # Background
        self.background = pygame.image.load("assets/images/blackjack_table.png").convert()

        # Layout positions
        self.dealer_pos = (screen.get_width() // 2 - 150, 40)
        self.deck_pos = (screen.get_width() // 2 + 200, 40)
        self.player_pos = (screen.get_width() // 2 - 150, screen.get_height() - 220)
        self.money_pos = (40, screen.get_height() - 60)

        # Action buttons
        self.buttons = {
            "hit": pygame.Rect(screen.get_width()//2 - 200, screen.get_height() - 100, 120, 50),
            "stand": pygame.Rect(screen.get_width()//2 - 60, screen.get_height() - 100, 120, 50),
            "double": pygame.Rect(screen.get_width()//2 + 80, screen.get_height() - 100, 120, 50),
        }

        self.message = ""
        self.show_dealer_hole = False

    # --------------------------------------------------

    def start_round(self):
        self.game.start_round()
        self.show_dealer_hole = False
        self.message = ""

    # --------------------------------------------------

    def update(self):
        FINAL_RESULTS = {
            "player_bust", "dealer_bust",
            "player_win", "dealer_win",
            "push",
            "player_blackjack", "dealer_blackjack"
        }

        if self.message in FINAL_RESULTS:
            self.show_dealer_hole = True
            self.game.payout(self.message)

    # --------------------------------------------------

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Betting phase
        if self.in_betting_phase:
            self.draw_bet_buttons()
            pygame.display.flip()
            return

        # Normal gameplay
        self.draw_hands()
        self.draw_buttons()
        self.draw_money()
        self.draw_message()

        # Result overlay
        self.draw_result_overlay()

        pygame.display.flip()

    # --------------------------------------------------

    def draw_result_overlay(self):
        FINAL_RESULTS = {
            "player_bust", "dealer_bust",
            "player_win", "dealer_win",
            "push",
            "player_blackjack", "dealer_blackjack"
        }

        if self.message not in FINAL_RESULTS:
            return

        # Determine which overlay to show
        if self.message in {"dealer_bust", "player_win", "player_blackjack"}:
            path = "assets/images/Player Wins.png"
        elif self.message in {"player_bust", "dealer_win", "dealer_blackjack"}:
            path = "assets/images/Dealer Wins.png"
        else:
            path = "assets/images/Push.png"

        overlay = pygame.image.load(path).convert_alpha()
        overlay.set_alpha(200)

        rect = overlay.get_rect(center=(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2
        ))

        self.screen.blit(overlay, rect)

    # --------------------------------------------------

    def draw_hands(self):
        # Dealer
        x, y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            if i == 1 and not self.show_dealer_hole:
                self.draw_card_back(x + i*80, y)
            else:
                self.draw_card(card, x + i*80, y)

        # Player
        x, y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            self.draw_card(card, x + i*80, y)

        # Deck
        self.draw_card_back(*self.deck_pos)

    # --------------------------------------------------

    def draw_card(self, card, x, y):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 70, 100))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 70, 100), 2)

        font = pygame.font.SysFont(None, 32)
        text = font.render(f"{card.rank}{card.suit}", True, (0, 0, 0))
        self.screen.blit(text, (x + 10, y + 10))

    def draw_card_back(self, x, y):
        pygame.draw.rect(self.screen, (0, 0, 150), (x, y, 70, 100))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 70, 100), 2)

    # --------------------------------------------------

    def draw_buttons(self):
        font = pygame.font.SysFont(None, 32)

        for name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            text = font.render(name.capitalize(), True, (0, 0, 0))
            self.screen.blit(text, (rect.x + 10, rect.y + 10))

    # --------------------------------------------------

    def draw_bet_buttons(self):
        for btn in self.bet_buttons.values():
            btn.draw(self.screen)

    # --------------------------------------------------

    def draw_money(self):
        font = pygame.font.SysFont(None, 36)
        money_text = font.render(f"$: {self.game.player_money}", True, (255, 255, 0))
        self.screen.blit(money_text, self.money_pos)

    # --------------------------------------------------

    def draw_message(self):
        if not self.message:
            return
        font = pygame.font.SysFont(None, 48)
        text = font.render(self.message, True, (255, 255, 255))
        self.screen.blit(text, (self.screen.get_width()//2 - text.get_width()//2, 20))

    # --------------------------------------------------

    def handle_event(self, event):
        FINAL_RESULTS = {
            "player_bust", "dealer_bust",
            "player_win", "dealer_win",
            "push",
            "player_blackjack", "dealer_blackjack"
        }

        # SPACE resets after round ends
        if self.message in FINAL_RESULTS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.reset_round()
                self.in_betting_phase = True
                self.message = ""
            return

        # Betting phase
        if self.in_betting_phase:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for amount, btn in self.bet_buttons.items():
                    if btn.is_clicked():
                        if self.game.place_bet(amount):
                            self.in_betting_phase = False
                            self.start_round()
                        else:
                            self.message = "Not enough money"
            return

        # Gameplay buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.buttons["hit"].collidepoint(mx, my):
                self.message = self.game.player_hit()

            elif self.buttons["stand"].collidepoint(mx, my):
                self.show_dealer_hole = True
                self.message = self.game.player_stand()

            elif self.buttons["double"].collidepoint(mx, my):
                self.show_dealer_hole = True
                self.message = self.game.player_double()

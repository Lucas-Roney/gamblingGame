import pygame
import os
from blackjack import BlackjackGame
from buttons import Button
from buttons import CircleButton
from card_cosmetics import CardCosmetics
from settings import *

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

        # --- Load card faces ---
        self.card_images = {}

        face_folder = "assets/images/cards/faces"
        CARD_HEIGHT = 200  # adjust later if needed

        def scale_preserve_aspect(img, target_height):
            ratio = img.get_width() / img.get_height()
            target_width = int(target_height * ratio)
            return pygame.transform.smoothscale(img, (target_width, target_height))

        for filename in os.listdir(face_folder):
            if filename.endswith(".png"):
                key = filename.replace(".png", "")  # e.g. "AH"
                path = os.path.join(face_folder, filename)

                img = pygame.image.load(path).convert_alpha()
                img = scale_preserve_aspect(img, CARD_HEIGHT)

                self.card_images[key] = img

        # Layout positions
        self.dealer_pos = (screen.get_width() // 2 - 90, 60)
        self.deck_pos = (screen.get_width() // 2 + 230, 60)
        self.player_pos = (screen.get_width() // 2 - 90, screen.get_height() - 200)
        self.money_pos = (40, screen.get_height() - 60)

        # Action buttons
        self.hit_button = Button(200, screen.get_height() - 230, 150, 60, "HIT")
        self.stand_button = Button(screen.get_width() - 350, screen.get_height() - 230, 150, 60, "STAND")
        self.double_button = CircleButton(screen.get_width() // 2 - 193, screen.get_height() - 77, 40, "x2")


        self.message = ""
        self.show_dealer_hole = False
        self.cosmetics = CardCosmetics()
        
        # Load card faces
        self.card_images = {}
        face_folder = "assets/images/cards/faces"

        for filename in os.listdir(face_folder):
            if filename.endswith(".png"):
                key = filename.replace(".png", "")  # e.g. "AH"
                img = pygame.image.load(os.path.join(face_folder, filename)).convert_alpha()
                img = pygame.transform.scale(img, (105, 150))
                self.card_images[key] = img


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
        self.hit_button.draw(self.screen)
        self.stand_button.draw(self.screen)
        self.double_button.draw(self.screen)
        self.draw_money()
        self.draw_player_total()

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
                self.draw_card_back(x + i*40, y)
            else:
                self.draw_card(card, x + i*80, y)

        # Player
        x, y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            self.draw_card(card, x + i*40, y)

        # Deck
        self.draw_card_back(*self.deck_pos)

    # --------------------------------------------------

    def draw_card(self, card, x, y):
        key = f"{card.rank}{card.suit}"  # ex "AH"
        img = self.card_images.get(key)

        if img:
            self.screen.blit(img, (x, y))
        else:
            # fallback if missing
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 70, 100))
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 70, 100), 2)


    def draw_card_back(self, x, y):
        img = self.cosmetics.get_card_back()
        self.screen.blit(img, (x, y))



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
        
    def draw_player_total(self):
        total = self.game.player.total()

        font = pygame.font.Font(BUTTON_FONT, 25)
        text = font.render(f"Total: {total}", True, (255, 255, 255))

        # Center it under the player's hand
        x = self.player_pos[0] + 20  # adjust if needed
        y = self.player_pos[1] + 158
        # just below the cards

        self.screen.blit(text, (x, y))

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

            if self.hit_button.is_clicked():
                self.hit()

            if self.stand_button.is_clicked():
                self.stand()

            if self.double_button.is_clicked():
                self.double_down()
    def hit(self):
        self.message = self.game.player_hit()

    def stand(self):
        self.show_dealer_hole = True
        self.message = self.game.player_stand()

    def double_down(self):
        self.show_dealer_hole = True
        self.message = self.game.player_double()



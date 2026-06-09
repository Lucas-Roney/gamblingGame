import pygame
import os
from blackjack import BlackjackGame
from buttons import Button
from buttons import no_mask_ImageButton
from buttons import CircleButton
from card_cosmetics import CardCosmetics
from settings import *

class BlackjackUI:
    def __init__(self, screen, chips):
        self.screen = screen
        self.chip_bank = chips
        self.game = BlackjackGame()
        self.game.player_money = chips.get_balance()
        self.in_betting_phase = True
        self.deal_sequence = []
        self.dealt_cards = set()
        self.dealing_in_progress = False

        # Betting buttons
        self.bet_buttons = {
            5: no_mask_ImageButton(830, self.screen.get_height() - 110, 80, 80, "assets/images/chips/pokerchip1.png", "$5"),
            10: no_mask_ImageButton(950, self.screen.get_height() - 110, 80, 80, "assets/images/chips/pokerchip2.png", "$10"),
            50: no_mask_ImageButton(1070, self.screen.get_height() - 110, 80, 80, "assets/images/chips/pokerchip3.png", "$50"),
            100: no_mask_ImageButton(1190, self.screen.get_height() - 110, 80, 80, "assets/images/chips/pokerchip4.png", "$100")
        }
        
        # Chip images
        self.selected_chip_image = None
        self.selected_chip_pos = (screen.get_width() // 2 - 234, screen.get_height() - 117)


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
        self.hit_button.text_color = (240, 255, 17)
        self.stand_button = Button(screen.get_width() - 350, screen.get_height() - 230, 150, 60, "STAND")
        self.stand_button.text_color = (240, 255, 17)
        self.double_button = CircleButton(screen.get_width() // 2 - 193, screen.get_height() - 76, 37, "x2")
        self.double_button.text_color = (240, 255, 17)


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
                
        self.animations = []
        self.animating = False



    # --------------------------------------------------

    def start_round(self):
        # Run game logic
        self.message = self.game.start_round()
        self.show_dealer_hole = False
        self.can_double = True

        # Clear old animations and sequence
        self.animations.clear()
        self.animating = False
        self.deal_sequence.clear()
        self.dealing_in_progress = True

        # Dealer first card
        card = self.game.dealer.cards[0]
        end_pos = (self.dealer_pos[0], self.dealer_pos[1])
        self.deal_sequence.append((card, end_pos))
        

        # Player first card
        card = self.game.player.cards[0]
        end_pos = (self.player_pos[0], self.player_pos[1])
        self.deal_sequence.append((card, end_pos))

        # Dealer second card (hole)
        card = self.game.dealer.cards[1]
        end_pos = (self.dealer_pos[0] + 40, self.dealer_pos[1])
        self.deal_sequence.append((card, end_pos))

        # Player second card
        card = self.game.player.cards[1]
        end_pos = (self.player_pos[0] + 40, self.player_pos[1])
        self.deal_sequence.append((card, end_pos))

        # Kick off first animation
        self.start_next_deal_animation()



    # --------------------------------------------------

    def update(self):
        # Sync money
        self.chip_bank.set_balance(self.game.player_money)

        FINAL_RESULTS = {
            "player_bust", "dealer_bust",
            "player_win", "dealer_win",
            "push",
            "player_blackjack", "dealer_blackjack"
        }

        if self.message in FINAL_RESULTS:
            self.show_dealer_hole = True
            self.game.payout(self.message)
            
        if self.animating:
            dt = 1 / 60  # assuming 60 FPS
            finished = []

            for anim in self.animations:
                anim["time"] += dt
                if anim["time"] >= anim["duration"]:
                    finished.append(anim)

            for anim in finished:
                self.animations.remove(anim)
                self.dealt_cards.add(anim["card"])

            if finished:
                self.start_next_deal_animation()

            if not self.animations:
                self.animating = False
                
            if not self.animations and not self.deal_sequence:
                self.animating = False
                self.dealing_in_progress = False



    # --------------------------------------------------

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Betting phase
        if self.in_betting_phase:
            self.draw_bet_buttons()
            self.draw_money()
            pygame.display.flip()
            return

        # Normal gameplay
        self.draw_hands()
        
        # Draw active animations
        for anim in self.animations:
            t = anim["time"] / anim["duration"]
            t = min(max(t, 0), 1)

            # Linear interpolation
            sx, sy = anim["start"]
            ex, ey = anim["end"]
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t

            # Detect if this is the dealer's hole card
            is_hole_card = (
                anim["card"] is self.game.dealer.cards[1]
                and not self.show_dealer_hole
            )

            if is_hole_card:
                # Animate using the card back
                self.draw_card_back(x, y)
            else:
                # Normal animation
                self.draw_card(anim["card"], x, y)

        
        if self.selected_chip_image:
            self.screen.blit(self.selected_chip_image, self.selected_chip_pos)
        self.hit_button.draw(self.screen)
        self.stand_button.draw(self.screen)
        if self.game.can_double:
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
        # Skip if dealing
        if self.dealing_in_progress:
            self.draw_partial_hands()
            return


        # Dealer
        x, y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):

            # Skip if this card is currently animating
            if self.is_card_animating(card):
                continue

            if i == 1 and not self.show_dealer_hole:
                self.draw_card_back(x + i*40, y)
            else:
                self.draw_card(card, x + i*40, y)

        # Player
        x, y = self.player_pos
        for i, card in enumerate(self.game.player.cards):

            # Skip if animating
            if self.is_card_animating(card):
                continue

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
        
    def draw_partial_hands(self):
        # Dealer
        x, y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            # Skip cards still waiting for animation
            if card not in self.dealt_cards:
                continue

            if i == 1 and not self.show_dealer_hole:
                self.draw_card_back(x + i*40, y)
            else:
                self.draw_card(card, x + i*40, y)

        # Player
        x, y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            if card not in self.dealt_cards:
                continue

            self.draw_card(card, x + i*40, y)

        # Deck stays visible
        self.draw_card_back(*self.deck_pos)



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
        if self.dealing_in_progress:
            total = self.get_dealt_total()
        else:
            total = self.game.player.total()

        font = pygame.font.Font(BUTTON_FONT, 25)
        text = font.render(f"Total: {total}", True, (255, 255, 255))

        x = self.player_pos[0] + 20
        y = self.player_pos[1] + 158

        self.screen.blit(text, (x, y))

        
    def get_dealt_total(self):
        total = 0
        aces = 0

        for card in self.game.player.cards:
            if card not in self.dealt_cards:
                continue

            if card.rank in ["J", "Q", "K"]:
                total += 10
            elif card.rank == "A":
                aces += 1
                total += 11
            else:
                total += int(card.rank)

        # Adjust Aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total


    # --------------------------------------------------
    
    def start_next_deal_animation(self):
        if not self.deal_sequence:
            return

        card, end_pos = self.deal_sequence.pop(0)
        self.animate_card(card, self.deck_pos, end_pos)


    # --------------------------------------------------

    def handle_event(self, event):
        # No inputs while animating
        if self.animating:
            return
        
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
                self.selected_chip_image = None
            return

        # Betting phase
        if self.in_betting_phase:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for amount, btn in self.bet_buttons.items():
                    if btn.is_clicked():
                        if self.game.place_bet(amount):

                            # Store the selected chip image
                            self.selected_chip_image = btn.image

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

            if self.double_button.is_clicked() and self.game.can_double:
                self.double_down()

    # --------------------------------------------------

    def hit(self):
        self.message = self.game.player_hit()

    def stand(self):
        self.show_dealer_hole = True
        self.message = self.game.player_stand()

    def double_down(self):
        self.show_dealer_hole = True
        self.message = self.game.player_double()
        
    # --------------------------------------------------
        
    def animate_card(self, card, start_pos, end_pos, duration=0.4):
        anim = {
            "card": card,
            "start": start_pos,
            "end": end_pos,
            "time": 0,
            "duration": duration
        }
        self.animations.append(anim)
        self.animating = True
        
    # --------------------------------------------------

    def is_card_animating(self, card):
        for anim in self.animations:
            if anim["card"] is card:
                return True
        return False




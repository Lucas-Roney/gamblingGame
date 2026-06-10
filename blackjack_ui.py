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
        self.discard = []
        self.clock = pygame.time.Clock()
        self.result_handled = False

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
        self.discard_pos = (screen.get_width() // 2 + 530, 60)
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
        
        self.chip_animation = None



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

        if self.message in FINAL_RESULTS and not self.dealing_in_progress and not self.result_handled:
            self.result_handled = True
            self.show_dealer_hole = True
            self.draw()
            self.pause(45)

            # Draw final table
            self.draw()

            # Fade out
            self.fade()

            # Draw overlay
            self.draw_result_overlay()
            self.pause(90)
            # Fade in
            self.fade_in()
            
            if self.message in {"player_win", "player_blackjack", "dealer_bust"}:
                self.animate_chip(direction="down")

            elif self.message in {"dealer_win", "dealer_blackjack", "player_bust"}:
                self.animate_chip(direction="up")

            elif self.message == "push":
                self.animate_chip(direction="down")


            # Wait for chip animation to finish
            while self.chip_animation:
                self.update()   # allow animation time to advance
                self.draw()
                self.clock.tick(60)



            # Discard animation
            self.animate_discard_sequence()

            # Reset game state
            self.game.payout(self.message)
            self.game.reset_round()
            self.in_betting_phase = True
            self.message = ""
            self.selected_chip_image = None
            self.dealt_cards.clear()
            self.result_handled = False


        # Handle dealing card updates (Keep this block exactly as you have it)
        if self.animating:
            dt = 1 / 60  
            finished = []

            for anim_card in self.animations:
                anim_card["time"] += dt
                if anim_card["time"] >= anim_card["duration"]:
                    finished.append(anim_card)

            for anim_card in finished:
                self.animations.remove(anim_card)
                self.dealt_cards.add(anim_card["card"])

            if finished:
                self.start_next_deal_animation()

            if not self.animations:
                self.animating = False
                self.dealing_in_progress = False
                
        # Chip animation update
        if self.chip_animation:
            anim = self.chip_animation

            if anim["direction"] == "up":
                anim["y"] -= anim["speed"]
            elif anim["direction"] == "down":
                anim["y"] += anim["speed"]

            # Remove when off-screen
            if anim["y"] < -200 or anim["y"] > self.screen.get_height() + 200:
                self.chip_animation = None
                self.selected_chip_image = None


    def fade(self, speed=5):
        # Draw without forcing a display flip so we can copy a clean buffer
        self.draw()
        snapshot = self.screen.copy()
        fade_surface = pygame.Surface(snapshot.get_size(), pygame.SRCALPHA)

        for alpha in range(0, 151, speed):
            self.screen.blit(snapshot, (0, 0))
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()  # Smoothly flip the transition frames instead
            self.clock.tick(60)

    def fade_in(self, speed=5):
        # Draw the NEW state to the backbuffer quietly without showing it yet
        self.draw()
        snapshot = self.screen.copy()
        fade_surface = pygame.Surface(snapshot.get_size(), pygame.SRCALPHA)

        for alpha in range(150, -1, -speed):
            self.screen.blit(snapshot, (0, 0))
            fade_surface.fill((0, 0, 0, max(0, alpha)))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            
    def pause(self, frames=60):
        for _ in range(frames):
            pygame.display.update()
            self.clock.tick(60)


    # --------------------------------------------------

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Betting phase
        if self.in_betting_phase:
            self.draw_bet_buttons()
            self.draw_money()
            self.draw_card_back(*self.deck_pos)
            if self.discard:
                self.draw_card_back(*self.discard_pos)
            pygame.display.flip()
            return

        # Normal gameplay
        self.draw_hands()

        # Draw active card animations
        for anim_card in self.animations:
            t = anim_card["time"] / anim_card["duration"]
            t = min(max(t, 0), 1)

            sx, sy = anim_card["start"]
            ex, ey = anim_card["end"]
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t

            is_hole_card = (
                anim_card["card"] is self.game.dealer.cards[1]
                and not self.show_dealer_hole
            )

            if is_hole_card:
                self.draw_card_back(x, y)
            else:
                self.draw_card(anim_card["card"], x, y)

        # Chip anim
        if self.chip_animation:
            anim = self.chip_animation
            img = anim["image"]
            self.screen.blit(img, (anim["x"], anim["y"]))
        else:
            if self.selected_chip_image:
                self.screen.blit(self.selected_chip_image, self.selected_chip_pos)


                # ALWAYS draw UI elements
                self.hit_button.draw(self.screen)
                self.stand_button.draw(self.screen)
                if self.game.can_double:
                    self.double_button.draw(self.screen)

                self.draw_money()
                self.draw_player_total()
                self.draw_dealer_total()

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
        
        # Discard
        if self.discard:
                self.draw_card_back(*self.discard_pos)


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
        
        # Discard stays visible
        if self.discard:
                self.draw_card_back(*self.discard_pos)



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
            total = self.get_dealt_total_player()
        else:
            total = self.game.player.total()

        font = pygame.font.Font(BUTTON_FONT, 25)
        text = font.render(f"Total: {total}", True, (255, 255, 255))

        x = self.player_pos[0] + 20
        y = self.player_pos[1] + 158

        self.screen.blit(text, (x, y))
        
    def draw_dealer_total(self):
        total = self.get_dealt_total_dealer()

        font = pygame.font.Font(BUTTON_FONT, 25)
        text = font.render(f"Total: {total}", True, (255, 255, 255))

        x = self.dealer_pos[0] + 20
        y = self.dealer_pos[1] + 158

        self.screen.blit(text, (x, y))

        
    def get_dealt_total_player(self):
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

    def get_dealt_total_dealer(self):
        total = 0
        aces = 0

        for card in self.game.dealer.cards:
            if card not in self.dealt_cards:
                continue
            
            if card == self.game.dealer.cards[1]:
                if not self.show_dealer_hole: 
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
        # Count current cards to calculate the exact layout offset
        num_cards_before = len(self.game.player.cards)
        
        # Advance backend engine logic
        self.message = self.game.player_hit()
        
        # If a card was successfully added, animate it from the deck
        if len(self.game.player.cards) > num_cards_before:
            new_card = self.game.player.cards[-1]
            end_x = self.player_pos[0] + (num_cards_before * 40)
            end_y = self.player_pos[1]
            
            self.dealing_in_progress = True
            self.animate_card(new_card, self.deck_pos, (end_x, end_y))

    def stand(self):
        self.show_dealer_hole = True
        self.draw()
        self.draw_dealer_total()
        self.pause(45)
        
        # Let the dealer draw cards according to AI logic rules
        old_dealer_cards = list(self.game.dealer.cards)
        self.message = self.game.player_stand()
        new_dealer_cards = self.game.dealer.cards
        
        # Queue up any cards the dealer took so they roll out sequentially
        if len(new_dealer_cards) > len(old_dealer_cards):
            self.dealing_in_progress = True
            for i in range(len(old_dealer_cards), len(new_dealer_cards)):
                card = new_dealer_cards[i]
                end_x = self.dealer_pos[0] + (i * 40)
                end_y = self.dealer_pos[1]
                self.deal_sequence.append((card, (end_x, end_y)))
            
            self.start_next_deal_animation()

    def double_down(self):
        self.show_dealer_hole = True
        self.draw_hands()
        self.pause(45)
        num_cards_before = len(self.game.player.cards)
        
        self.message = self.game.player_double()
        
        if len(self.game.player.cards) > num_cards_before:
            new_card = self.game.player.cards[-1]
            end_x = self.player_pos[0] + (num_cards_before * 40)
            end_y = self.player_pos[1]
            
            self.dealing_in_progress = True
            self.animate_card(new_card, self.deck_pos, (end_x, end_y))
        
    # --------------------------------------------------
        
    def animate_card(self, card, start_pos, end_pos, duration=0.4):
        anim_card = {
            "card": card,
            "start": start_pos,
            "end": end_pos,
            "time": 0,
            "duration": duration
        }
        self.animations.append(anim_card)
        self.animating = True
        
        
    def animate_discard_sequence(self):
        """Slides all cards from their current hand positions into a neat discard pile."""
        discard_anims = []
        dest_x, dest_y = self.discard_pos
        
        # 1. Gather all active player cards and their current visual locations
        p_x, p_y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            discard_anims.append({
                "card": card, 
                "start": (p_x + i * 40, p_y), 
                "end": (dest_x, dest_y),
                "time": 0, 
                "duration": 0.4
            })
            
        # 2. Gather all active dealer cards
        d_x, d_y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            # If the hole card was never revealed, we should slide it face-down
            is_hole = (i == 1 and not self.show_dealer_hole)
            discard_anims.append({
                "card": card, 
                "start": (d_x + i * 40, d_y), 
                "end": (dest_x, dest_y),
                "time": 0, 
                "duration": 0.4,
                "is_hole": is_hole
            })
            
        # 3. Main animation loop execution
        dt = 1 / 60
        while discard_anims:
            for anim_card in discard_anims[:]:
                anim_card["time"] += dt
                if anim_card["time"] >= anim_card["duration"]:
                    discard_anims.remove(anim_card)
                    
            # Clear screen with background table
            self.screen.blit(self.background, (0, 0))
            self.draw_money()
            self.draw_card_back(*self.deck_pos)
            if self.discard:
                self.draw_card_back(*self.discard_pos)
            
            if self.selected_chip_image:
                self.screen.blit(self.selected_chip_image, self.selected_chip_pos)
                
            # Draw moving cards heading toward the pile
            for anim_card in discard_anims:
                t = min(anim_card["time"] / anim_card["duration"], 1.0)
                # Smooth movement calculation
                cx = anim_card["start"][0] + (anim_card["end"][0] - anim_card["start"][0]) * t
                cy = anim_card["start"][1] + (anim_card["end"][1] - anim_card["start"][1]) * t
                
                if anim_card.get("is_hole"):
                    self.draw_card_back(cx, cy)
                else:
                    self.draw_card(anim_card["card"], cx, cy)
                
            pygame.display.flip()
            self.clock.tick(60)
        self.draw_card_back(*self.discard_pos)
        self.discard.extend(self.game.player.cards)
        self.discard.extend(self.game.dealer.cards)
        
    # --------------------------------------------------

    def is_card_animating(self, card):
        for anim_card in self.animations:
            if anim_card["card"] is card:
                return True
        return False
    
    # --------------------------------------------------
    
    def animate_chip(self, direction="up", speed=8):
        if not self.selected_chip_image:
            return

        x, y = self.selected_chip_pos

        self.chip_animation = {
            "image": self.selected_chip_image,
            "x": x,
            "y": y,
            "direction": direction,
            "speed": speed
        }





import pygame
import os
from blackjack import BlackjackGame
from buttons import Button, no_mask_ImageButton, CircleButton
from card_cosmetics import CardCosmetics
from settings import *


# Results that end a round
FINAL_RESULTS = {
    "player_bust", "dealer_bust",
    "player_win", "dealer_win",
    "push",
    "player_blackjack", "dealer_blackjack"
}

PLAYER_WINS = {"player_win", "player_blackjack", "dealer_bust"}
DEALER_WINS = {"dealer_win", "dealer_blackjack", "player_bust"}


class BlackjackUI:
    def __init__(self, screen, chips):
        self.screen = screen
        self.chip_bank = chips
        self.game_ref = None

        # Game state
        self.game = BlackjackGame()
        self.game.player_money = chips.get_balance()
        self.in_betting_phase = True
        self.show_action_buttons = True
        self.message = ""
        self.show_dealer_hole = False
        self.result_handled = False

        # Dealing state
        self.deal_sequence = []
        self.dealt_cards = set()
        self.dealing_in_progress = False
        self.discard = []

        # Animation state
        self.animations = []
        self.animating = False
        self.chip_animations = []
        self.selected_chip_image = None

        # Double-down state
        self.in_double_down_animation = False
        self.dd_phase = None  # None | "player_card" | "reveal_hole" | "dealer_cards"
        self._dd_old_dealer_cards = []
        self._dd_new_dealer_cards = []

        self.clock = pygame.time.Clock()
        self.cosmetics = CardCosmetics()

        # Layout positions
        w, h = screen.get_size()
        self.dealer_pos    = (w // 2 - 90, 60)
        self.deck_pos      = (w // 2 + 230, 60)
        self.discard_pos   = (w // 2 + 530, 60)
        self.player_pos    = (w // 2 - 90, h - 200)
        self.money_pos     = (40, h - 60)
        self.selected_chip_pos = (w // 2 - 234, h - 117)

        # Assets
        self.background = pygame.image.load("assets/images/blackjack_table.png").convert()
        self.card_images = self._load_card_images()
        self.overlay_images = self._load_overlay_images()

        # Buttons
        self.bet_buttons = {
            5:   no_mask_ImageButton(830,  h - 110, 80, 80, "assets/images/chips/pokerchip1.png", "$5"),
            10:  no_mask_ImageButton(950,  h - 110, 80, 80, "assets/images/chips/pokerchip2.png", "$10"),
            50:  no_mask_ImageButton(1070, h - 110, 80, 80, "assets/images/chips/pokerchip3.png", "$50"),
            100: no_mask_ImageButton(1190, h - 110, 80, 80, "assets/images/chips/pokerchip4.png", "$100"),
        }

        self.hit_button    = Button(200, h - 230, 150, 60, "HIT")
        self.stand_button  = Button(w - 350, h - 230, 150, 60, "STAND")
        self.double_button = CircleButton(w // 2 - 193, h - 76, 37, "x2")

        self.hit_button.text_color    = (240, 255, 17)
        self.stand_button.text_color  = (240, 255, 17)
        self.double_button.text_color = (240, 255, 17)

    # --------------------------------------------------
    # Asset loading
    # --------------------------------------------------

    def _load_card_images(self):
        images = {}
        face_folder = "assets/images/cards/faces"
        for filename in os.listdir(face_folder):
            if filename.endswith(".png"):
                key = filename.replace(".png", "")
                img = pygame.image.load(os.path.join(face_folder, filename)).convert_alpha()
                img = pygame.transform.scale(img, (105, 150))
                images[key] = img
        return images

    def _load_overlay_images(self):
        def load(path):
            img = pygame.image.load(path).convert_alpha()
            img.set_alpha(200)
            return img
        return {
            "player": load("assets/images/Player Wins.png"),
            "dealer": load("assets/images/Dealer Wins.png"),
            "push":   load("assets/images/Push.png"),
        }

    # --------------------------------------------------
    # Round management
    # --------------------------------------------------

    def start_round(self):
        self.message = self.game.start_round()
        self.show_dealer_hole = False
        self.game.player_doubled = False
        self.show_action_buttons = True

        self.animations.clear()
        self.animating = False
        self.deal_sequence.clear()
        self.dealt_cards.clear()
        self.dealing_in_progress = True

        # Queue initial deal: D1, P1, D2(hole), P2
        d_x, d_y = self.dealer_pos
        p_x, p_y = self.player_pos
        self.deal_sequence = [
            (self.game.dealer.cards[0], (d_x,      d_y)),
            (self.game.player.cards[0], (p_x,      p_y)),
            (self.game.dealer.cards[1], (d_x + 40, d_y)),
            (self.game.player.cards[1], (p_x + 40, p_y)),
        ]
        self.start_next_deal_animation()

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(self):
        self.chip_bank.set_balance(self.game.player_money)

        # Result handling
        if (
            self.message in FINAL_RESULTS
            and not self.dealing_in_progress
            and not self.result_handled
            and not self.in_double_down_animation
        ):
            self._handle_result()
            return

        # Card animation tick
        if self.animating:
            self._tick_card_animations()

        # Chip animation tick
        if self.chip_animations:
            self._tick_chip_animations()

        # Double-down phase sequencing
        if self.in_double_down_animation and not self.animating and not self.dealing_in_progress:
            self._advance_dd_phase()

    def _tick_card_animations(self):
        dt = 1 / 60
        finished = []

        for anim in self.animations:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_ref.pause_screen()
                        
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
            self.dealing_in_progress = False
            return  # prevent same-frame dd phase trigger

    def _tick_chip_animations(self):
        for anim in self.chip_animations:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_ref.pause_screen()
                        
            anim["y"] += -anim["speed"] if anim["direction"] == "up" else anim["speed"]

        self.chip_animations = [
            a for a in self.chip_animations
            if -200 < a["y"] < self.screen.get_height() + 200
        ]

        if not self.chip_animations:
            self.selected_chip_image = None

    def _advance_dd_phase(self):
        if self.dd_phase == "player_card":
            self.dd_phase = "reveal_hole"
            self.draw()
            self.pause(30)
            self.show_dealer_hole = True
            self.draw()
            self.pause(30)

            old_cards = self._dd_old_dealer_cards
            new_cards = self._dd_new_dealer_cards

            if len(new_cards) > len(old_cards):
                self.dd_phase = "dealer_cards"
                self.dealing_in_progress = True
                d_x, d_y = self.dealer_pos
                for i in range(len(old_cards), len(new_cards)):
                    self.deal_sequence.append((new_cards[i], (d_x + i * 40, d_y)))
                self.start_next_deal_animation()
            else:
                self.dd_phase = None
                self.in_double_down_animation = False

        elif self.dd_phase == "dealer_cards":
            self.dd_phase = None
            self.in_double_down_animation = False

    def _handle_result(self):
        self.result_handled = True
        self.show_dealer_hole = True
        self.draw()
        self.pause(45)

        self.show_result_with_fade()

        # Chip animations
        if self.message in PLAYER_WINS:
            chip_count = 4 if self.game.player_doubled else 2
            self.show_static_chips(chip_count)
            self.draw()
            self.pause(45)
            for anim in self.chip_animations:
                anim["speed"] = 3
        elif self.message in DEALER_WINS:
            self.animate_chip(direction="up", count=2 if self.game.player_doubled else 1, speed=8)
        elif self.message == "push":
            self.animate_chip(direction="down", count=2 if self.game.player_doubled else 1)

        # Wait for chip animation
        while self.chip_animations:
            self.update()
            self.draw()
            self.clock.tick(60)

        self.animate_discard_sequence()

        # Reset
        self.game.payout(self.message)
        self.game.reset_round()
        self.in_betting_phase = True
        self.message = ""
        self.selected_chip_image = None
        self.dealt_cards.clear()
        self.result_handled = False

    # --------------------------------------------------
    # Fade / pause helpers
    # --------------------------------------------------

    def show_result_with_fade(self, speed=5):
        snapshot = self.screen.copy()
        fade_surface = pygame.Surface(snapshot.get_size(), pygame.SRCALPHA)

        # Fade down
        for alpha in range(0, 151, speed):
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_ref.pause_screen()
            
            self.screen.blit(snapshot, (0, 0))
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

        # Show overlay on darkened screen
        self.screen.blit(snapshot, (0, 0))
        fade_surface.fill((0, 0, 0, 150))
        self.screen.blit(fade_surface, (0, 0))
        self.draw_result_overlay()
        pygame.display.flip()

        # Hold overlay
        overlay_snapshot = self.screen.copy()
        for _ in range(90):
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_ref.pause_screen()
            
            self.screen.blit(overlay_snapshot, (0, 0))
            pygame.event.pump()
            pygame.display.flip()
            self.clock.tick(60)

        # Fade back up (using original snapshot, not overlay snapshot)
        for alpha in range(150, -1, -speed):
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_ref.pause_screen()
            
            self.screen.blit(snapshot, (0, 0))
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    def pause(self, frames=60):
        snapshot = self.screen.copy()
        for _ in range(frames):
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
            
            pygame.event.pump()
            self.screen.blit(snapshot, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    # --------------------------------------------------
    # Draw
    # --------------------------------------------------

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if self.in_betting_phase:
            self._draw_betting_ui()
            pygame.display.flip()
            return

        self.draw_hands()
        self._draw_animating_cards()
        self._draw_chips()
        self._draw_action_buttons()
        self.draw_money()
        self.draw_player_total()
        self.draw_dealer_total()
        pygame.display.flip()

    def _draw_betting_ui(self):
        for btn in self.bet_buttons.values():
            btn.draw(self.screen)
        self.draw_money()
        self.draw_card_back(*self.deck_pos)
        if self.discard:
            self.draw_card_back(*self.discard_pos)

    def _draw_animating_cards(self):
        for anim in self.animations:
            t = min(max(anim["time"] / anim["duration"], 0), 1)
            sx, sy = anim["start"]
            ex, ey = anim["end"]
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t

            is_hole = (
                anim["card"] is self.game.dealer.cards[1]
                and not self.show_dealer_hole
            )
            if is_hole:
                self.draw_card_back(x, y)
            else:
                self.draw_card(anim["card"], x, y)

    def _draw_chips(self):
        if self.chip_animations:
            for anim in self.chip_animations:
                self.screen.blit(anim["image"], (anim["x"], anim["y"]))
        elif self.selected_chip_image:
            self.screen.blit(self.selected_chip_image, self.selected_chip_pos)

    def _draw_action_buttons(self):
        if not self.show_action_buttons:
            return
        if self.message in {"player_bust", "dealer_blackjack", "player_blackjack"}:
            return
        self.hit_button.draw(self.screen)
        self.stand_button.draw(self.screen)
        if self.game.can_double:
            self.double_button.draw(self.screen)

    def draw_result_overlay(self):
        if self.message in PLAYER_WINS:
            img = self.overlay_images["player"]
        elif self.message in DEALER_WINS:
            img = self.overlay_images["dealer"]
        elif self.message == "push":
            img = self.overlay_images["push"]
        else:
            return

        rect = img.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(img, rect)

    def draw_hands(self):
        if self.dealing_in_progress or self.in_double_down_animation:
            self._draw_partial_hands()
            return

        d_x, d_y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            if self.is_card_animating(card):
                continue
            if i == 1 and not self.show_dealer_hole:
                self.draw_card_back(d_x + i * 40, d_y)
            else:
                self.draw_card(card, d_x + i * 40, d_y)

        p_x, p_y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            if not self.is_card_animating(card):
                self.draw_card(card, p_x + i * 40, p_y)

        self.draw_card_back(*self.deck_pos)
        if self.discard:
            self.draw_card_back(*self.discard_pos)

    def _draw_partial_hands(self):
        d_x, d_y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            if card not in self.dealt_cards:
                continue
            if self.dd_phase == "player_card" and i == 1:
                self.draw_card_back(d_x + i * 40, d_y)
            elif i == 1 and not self.show_dealer_hole:
                self.draw_card_back(d_x + i * 40, d_y)
            else:
                self.draw_card(card, d_x + i * 40, d_y)

        p_x, p_y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            if card in self.dealt_cards:
                self.draw_card(card, p_x + i * 40, p_y)

        self.draw_card_back(*self.deck_pos)
        if self.discard:
            self.draw_card_back(*self.discard_pos)

    def draw_card(self, card, x, y):
        key = f"{card.rank}{card.suit}"
        img = self.card_images.get(key)
        if img:
            self.screen.blit(img, (x, y))
        else:
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 70, 100))
            pygame.draw.rect(self.screen, (0, 0, 0),       (x, y, 70, 100), 2)

    def draw_card_back(self, x, y):
        self.screen.blit(self.cosmetics.get_card_back(), (x, y))

    def draw_money(self):
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"$: {self.game.player_money}", True, (255, 255, 0))
        self.screen.blit(text, self.money_pos)

    def draw_player_total(self):
        total = self._get_dealt_total_player() if self.dealing_in_progress else self.game.player.total()
        self._draw_total(total, self.player_pos, offset_y=158)

    def draw_dealer_total(self):
        total = self._get_dealt_total_dealer()
        self._draw_total(total, self.dealer_pos, offset_y=158)

    def _draw_total(self, total, pos, offset_y):
        font = pygame.font.Font(BUTTON_FONT, 25)
        text = font.render(f"Total: {total}", True, (255, 255, 255))
        self.screen.blit(text, (pos[0] + 20, pos[1] + offset_y))

    # --------------------------------------------------
    # Total calculations
    # --------------------------------------------------

    def _hand_total(self, cards, filter_fn=None):
        total, aces = 0, 0
        for card in cards:
            if filter_fn and not filter_fn(card):
                continue
            if card.rank in ("J", "Q", "K"):
                total += 10
            elif card.rank == "A":
                aces += 1
                total += 11
            else:
                total += int(card.rank)
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def _get_dealt_total_player(self):
        return self._hand_total(self.game.player.cards, lambda c: c in self.dealt_cards)

    def _get_dealt_total_dealer(self):
        hole = self.game.dealer.cards[1]
        return self._hand_total(
            self.game.dealer.cards,
            lambda c: c in self.dealt_cards and (c is not hole or self.show_dealer_hole)
        )

    # --------------------------------------------------
    # Event handling
    # --------------------------------------------------

    def handle_event(self, event):
        if self.animating:
            return

        if self.in_betting_phase:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for amount, btn in self.bet_buttons.items():
                    if btn.is_clicked():
                        if self.game.place_bet(amount):
                            self.selected_chip_image = btn.image
                            self.in_betting_phase = False
                            self.start_round()
                        else:
                            self.message = "Not enough money"
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hit_button.is_clicked():
                self.hit()
            elif self.stand_button.is_clicked():
                self.stand()
            elif self.double_button.is_clicked() and self.game.can_double:
                self.double_down()

    # --------------------------------------------------
    # Player actions
    # --------------------------------------------------

    def hit(self):
        num_before = len(self.game.player.cards)
        self.message = self.game.player_hit()
        if len(self.game.player.cards) > num_before:
            new_card = self.game.player.cards[-1]
            p_x, p_y = self.player_pos
            self.dealing_in_progress = True
            self.animate_card(new_card, self.deck_pos, (p_x + num_before * 40, p_y))

    def stand(self):
        self.show_dealer_hole = True
        self.show_action_buttons = False
        self.draw()
        self.pause(45)

        old_cards = list(self.game.dealer.cards)
        self.message = self.game.player_stand()
        new_cards = self.game.dealer.cards

        if len(new_cards) > len(old_cards):
            self.dealing_in_progress = True
            d_x, d_y = self.dealer_pos
            for i in range(len(old_cards), len(new_cards)):
                self.deal_sequence.append((new_cards[i], (d_x + i * 40, d_y)))
            self.start_next_deal_animation()

    def double_down(self):
        self.dd_phase = "player_card"
        self.in_double_down_animation = True
        self.show_action_buttons = False
        self.game.player_doubled = True
        self.dealing_in_progress = True

        # Static doubled chips
        cx, cy = self.selected_chip_pos
        self.chip_animations = [
            {"image": self.selected_chip_image, "x": cx - 20, "y": cy, "direction": "down", "speed": 0},
            {"image": self.selected_chip_image, "x": cx + 20, "y": cy, "direction": "down", "speed": 0},
        ]

        num_before = len(self.game.player.cards)
        self._dd_old_dealer_cards = list(self.game.dealer.cards)
        self.message = self.game.player_double()
        self._dd_new_dealer_cards = self.game.dealer.cards

        new_card = self.game.player.cards[-1]
        p_x, p_y = self.player_pos
        self.animate_card(new_card, self.deck_pos, (p_x + num_before * 40, p_y))

    # --------------------------------------------------
    # Animation helpers
    # --------------------------------------------------

    def animate_card(self, card, start_pos, end_pos, duration=0.4):
        self.animations.append({
            "card": card,
            "start": start_pos,
            "end": end_pos,
            "time": 0,
            "duration": duration,
        })
        self.animating = True

    def start_next_deal_animation(self):
        if self.deal_sequence:
            card, end_pos = self.deal_sequence.pop(0)
            self.animate_card(card, self.deck_pos, end_pos)

    def is_card_animating(self, card):
        return any(a["card"] is card for a in self.animations)

    def animate_chip(self, direction="up", count=1, speed=3):
        if not self.selected_chip_image:
            return
        x, y = self.selected_chip_pos
        spacing = 40
        offset = -(count - 1) * spacing // 2
        self.chip_animations = [
            {"image": self.selected_chip_image, "x": x + offset + i * spacing,
             "y": y, "direction": direction, "speed": speed}
            for i in range(count)
        ]

    def show_static_chips(self, count, direction="down"):
        if not self.selected_chip_image:
            return
        x, y = self.selected_chip_pos
        spacing = 40
        offset = -(count - 1) * spacing // 2
        self.chip_animations = [
            {"image": self.selected_chip_image, "x": x + offset + i * spacing,
             "y": y, "direction": direction, "speed": 0}
            for i in range(count)
        ]

    def animate_discard_sequence(self):
        dest = self.discard_pos
        discard_anims = []

        p_x, p_y = self.player_pos
        for i, card in enumerate(self.game.player.cards):
            discard_anims.append({"card": card, "start": (p_x + i * 40, p_y), "end": dest, "time": 0, "duration": 0.4, "is_hole": False})

        d_x, d_y = self.dealer_pos
        for i, card in enumerate(self.game.dealer.cards):
            discard_anims.append({"card": card, "start": (d_x + i * 40, d_y), "end": dest, "time": 0, "duration": 0.4, "is_hole": i == 1 and not self.show_dealer_hole})

        dt = 1 / 60
        while discard_anims:
            for anim in discard_anims[:]:
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        return
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_ref.pause_screen()
                            
                anim["time"] += dt
                if anim["time"] >= anim["duration"]:
                    discard_anims.remove(anim)

            self.screen.blit(self.background, (0, 0))
            self.draw_money()
            self.draw_card_back(*self.deck_pos)
            if self.discard:
                self.draw_card_back(*self.discard_pos)
            if self.selected_chip_image:
                self.screen.blit(self.selected_chip_image, self.selected_chip_pos)

            for anim in discard_anims:
                t = min(anim["time"] / anim["duration"], 1.0)
                cx = anim["start"][0] + (anim["end"][0] - anim["start"][0]) * t
                cy = anim["start"][1] + (anim["end"][1] - anim["start"][1]) * t
                if anim["is_hole"]:
                    self.draw_card_back(cx, cy)
                else:
                    self.draw_card(anim["card"], cx, cy)

            pygame.display.flip()
            self.clock.tick(60)

        self.draw_card_back(*self.discard_pos)
        self.discard.extend(self.game.player.cards)
        self.discard.extend(self.game.dealer.cards)
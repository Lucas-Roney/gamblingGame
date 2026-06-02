import pygame
from settings import *
from ui import *
from buttons import Button
from buttons import ImageButton
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"


class Game:
    def __init__(self):
        info = pygame.display.Info()
        self.WIDTH = info.current_w
        self.HEIGHT = info.current_h
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT - 80))
        self.background = pygame.image.load("assets/images/background.png").convert()
        self.background = pygame.transform.scale(
            self.background,
            (self.WIDTH, self.HEIGHT - 60)
        )




        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Game states
        self.state = "MENU"

        # Play button
        self.play_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 - 60, 200, 60, "Play")
        self.store_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 20, 200, 60, "Store")
        self.exit_button = Button(self.WIDTH//2 - 100, self.HEIGHT//2 + 100, 200, 60, "Exit")
        self.back_button = Button(40, 40, 150, 50, "Back")
        
        self.blackjack_btn = ImageButton(
            self.WIDTH//2 - 450, self.HEIGHT//2 - 200,
            350, 200,
            "assets/images/blackjack.png",
            "Blackjack"
        )

        self.roulette_btn = ImageButton(
            self.WIDTH//2 + 100, self.HEIGHT//2 - 200,
            350, 200,
            "assets/images/roulette.png",
            "Roulette"
        )

        self.letitride_btn = ImageButton(
            self.WIDTH//2 - 450, self.HEIGHT//2 + 50,
            350, 200,
            "assets/images/letitride.png",
            "Let It Ride"
        )

        self.slots_btn = ImageButton(
            self.WIDTH//2 + 100, self.HEIGHT//2 + 50,
            350, 200,
            "assets/images/slots.png",
            "Slots"
        )
        
        self.shop_category = "CARDS"

        self.card_items = [
            #ShopItem(200, 300, 180, 260, card_back_default.image, "Classic Back", 0),
            #ShopItem(420, 300, 180, 260, card_back_gold.image, "Gold Back", 500),
        ]
        self.chip_items = []
        self.table_items = []

        self.shop_bg = pygame.image.load("assets/images/shop.png").convert()
        self.shop_bg = pygame.transform.scale(self.shop_bg, (self.WIDTH, self.HEIGHT - 60))
        
        self.cards_tab = Button(30, 450, 200, 60, "Cards")
        self.chips_tab = Button(30, 530, 200, 60, "Chips")
        self.tables_tab = Button(30, 610, 200, 60, "Tables")


        self.blackjack_popup = PopupWindow(
            self, 700, 500,
            "How to Play Blackjack",
            [
                "• Goal: Get as close to 21 as possible without going over.",
                "• You may Hit to draw a card.",
                "• You may Stand to keep your total.",
                "• You may Double to double your bet and draw one final card.",
                "• No splitting in this version.",
                "• Dealer hits on 16 and stands on 17.",
                "• A natural 21 (first two cards) pays double."
            ]
        )


        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "MENU" and self.play_button.is_clicked():
                    self.state = "GAME_SELECT"
                if self.state == "MENU" and self.store_button.is_clicked():
                    self.fade()
                    self.state = "STORE"
                    self.fade_in()
                if self.state == "MENU" and self.exit_button.is_clicked():
                    self.running = False
                    
                if self.state == "GAME_SELECT" and self.blackjack_btn.is_clicked():
                    self.state = "BLACKJACK_RULES"
                if self.state == "GAME_SELECT" and self.roulette_btn.is_clicked():
                    self.state = "ROULETTE"
                if self.state == "GAME_SELECT" and self.letitride_btn.is_clicked():
                    self.state = "LETITRIDE"
                if self.state == "GAME_SELECT" and self.slots_btn.is_clicked():
                    self.state = "SLOTS"
                if self.state == "BLACKJACK_RULES":
                    if self.blackjack_popup.is_play_clicked():
                        self.fade()
                        self.state = "BLACKJACK"
                        self.fade_in()

                if self.back_button.is_clicked():
                    if self.state == "STORE":  
                        self.fade()
                        self.state = "MENU"
                        self.fade_in()
                    else:
                        self.state = "MENU"
                if self.state == "STORE":
                    if self.cards_tab.is_clicked():
                        self.shop_category = "CARDS"
                    if self.chips_tab.is_clicked():
                        self.shop_category = "CHIPS"
                    if self.tables_tab.is_clicked():
                        self.shop_category = "TABLES"



                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False


    def update(self):
        pass  # logic goes here

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        if self.state == "MENU":
            draw_text_outline_shadow(
                self.screen,
                "Roney Casino",
                90,
                self.WIDTH // 2,
                200,
                text_color=(255, 255, 255),   # gold
                outline_color=(0, 0, 0),    # black outline
                shadow_color=(0, 0, 0),     # black shadow
                outline_width=3,
                shadow_offset=6
            )
            self.play_button.draw(self.screen)
            self.store_button.draw(self.screen)
            self.exit_button.draw(self.screen)

        elif self.state == "GAME_SELECT":
            self.screen.blit(self.background, (0, 0))
            draw_text_outline_shadow(
                self.screen,
                "Select a Game",
                80,
                self.WIDTH // 2,
                120,
                text_color=(255, 255, 255),
                outline_color=(0, 0, 0),
                shadow_color=(0, 0, 0),
                outline_width=3,
                shadow_offset=6
            )

            self.blackjack_btn.draw(self.screen)
            self.roulette_btn.draw(self.screen)
            self.letitride_btn.draw(self.screen)
            self.slots_btn.draw(self.screen)
            self.back_button.draw(self.screen)

            
        elif self.state == "BLACKJACK_RULES":
            self.blackjack_popup.draw(self.screen, self.background)
            
            
        elif self.state == "STORE":
            self.screen.blit(self.shop_bg, (0, 0))
            self.back_button.draw(self.screen)
            self.cards_tab.draw(self.screen)
            self.chips_tab.draw(self.screen)
            self.tables_tab.draw(self.screen)


            if self.shop_category == "CARDS":
                for item in self.card_items:
                    item.draw(self.screen)

            elif self.shop_category == "CHIPS":
                for item in self.chip_items:
                    item.draw(self.screen)

            elif self.shop_category == "TABLES":
                for item in self.table_items:
                    item.draw(self.screen)

            
            
        pygame.display.flip()
        
        
    def fade(self, speed=5):
        snapshot = self.screen.copy()

        fade_surface = pygame.Surface(snapshot.get_size(), pygame.SRCALPHA)

        for alpha in range(0, 255, speed):
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(snapshot, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(60)


    def fade_in(self, speed=5):
        self.draw()
        snapshot = self.screen.copy()

        fade_surface = pygame.Surface(snapshot.get_size(), pygame.SRCALPHA)

        for alpha in range(255, 0, -speed):
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(snapshot, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(60)

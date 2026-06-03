import pygame
import os

class CardCosmetics:
    """
    Handles:
    - Loading all card back images
    - Tracking owned cosmetics
    - Tracking equipped cosmetic
    - Providing the correct image to the renderer
    """

    def __init__(self, card_width=105, card_height=150):
        self.card_width = card_width
        self.card_height = card_height

        # --- Cosmetic State ---
        self.equipped_back = "default"       # ID of currently equipped card back
        self.owned_backs = {"default"}       # Set of owned card backs

        # --- Loaded Images ---
        self.card_backs = {}                 # id -> pygame.Surface

        # Load all available cosmetics
        self.load_all_card_backs()

    # -------------------------------------------------------------

    def load_all_card_backs(self):
        """
        Loads all card back images from assets/images/card_backs/
        Filenames must follow: <id>.png
        Example: default.png, gold.png, neon.png
        """

        folder = "assets/images/cards/card_backs"

        if not os.path.exists(folder):
            print(f"[CardCosmetics] Folder not found: {folder}")
            return

        for filename in os.listdir(folder):
            if not filename.lower().endswith(".png"):
                continue

            cosmetic_id = filename[:-4]  # remove .png
            path = os.path.join(folder, filename)

            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (self.card_width, self.card_height))
                self.card_backs[cosmetic_id] = img
            except Exception as e:
                print(f"[CardCosmetics] Failed to load {filename}: {e}")

        # Ensure default exists
        if "default" not in self.card_backs:
            # fallback: simple colored rectangle
            fallback = pygame.Surface((self.card_width, self.card_height))
            fallback.fill((0, 0, 150))
            pygame.draw.rect(fallback, (255, 255, 255), fallback.get_rect(), 2)
            self.card_backs["default"] = fallback

    # -------------------------------------------------------------

    def get_card_back(self):
        """
        Returns the pygame.Surface for the currently equipped card back.
        Falls back to default if missing.
        """
        return self.card_backs.get(self.equipped_back, self.card_backs["default"])

    # -------------------------------------------------------------

    def equip(self, cosmetic_id):
        """
        Equips a card back if the player owns it.
        """
        if cosmetic_id in self.owned_backs:
            self.equipped_back = cosmetic_id
            return True
        return False

    # -------------------------------------------------------------

    def unlock(self, cosmetic_id):
        """
        Adds a new card back to the player's owned cosmetics.
        """
        self.owned_backs.add(cosmetic_id)

    # -------------------------------------------------------------

    def list_owned(self):
        return list(self.owned_backs)

    def list_available(self):
        return list(self.card_backs.keys())

    def scale_preserve_aspect(img, target_height):
        ratio = img.get_width() / img.get_height()
        target_width = int(target_height * ratio)
        return pygame.transform.smoothscale(img, (target_width, target_height))


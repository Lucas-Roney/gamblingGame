import pygame
from settings import *

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

        self.base_color = (200, 0, 0)      # deep red
        self.hover_color = (235, 25, 25)   # brighter red
        self.border_color = BLACK
        self.text_color = WHITE

        self.font = pygame.font.Font("assets/fonts/PlayfairDisplaySC-Black.ttf", 35)
        self.hovered = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Button color changes on hover
        color = self.hover_color if self.hovered else self.base_color

        # Draw rounded rectangle
        pygame.draw.rect(surface, color, self.rect, border_radius=12)

        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=12)

        # Optional: glow effect on hover
        if self.hovered:
            glow_rect = self.rect.inflate(10, 10)
            pygame.draw.rect(surface, (255, 215, 0), glow_rect, width=3, border_radius=16)

        # Render text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

class ImageButton:
    def __init__(self, x, y, w, h, image_path, label):
        self.rect = pygame.Rect(x, y, w, h)

        # Load and scale image
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))

        # Rounded corner mask
        self.rounded_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.rounded_mask, (255, 255, 255), (0, 0, w, h), border_radius=20)

        self.label = label
        self.font = pygame.font.Font(TITLE_FONT, 40)

        self.hovered = False

    def draw_text_outline(self, surface, text, center):
        # Outline
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue
                outline = self.font.render(text, True, (0, 0, 0))
                rect = outline.get_rect(center=(center[0] + dx, center[1] + dy))
                surface.blit(outline, rect)

        # Main text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, text_rect)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Hover scale effect
        if self.hovered:
            img = pygame.transform.scale(self.image, (self.rect.width + 10, self.rect.height + 10))
            img_pos = (self.rect.x - 5, self.rect.y - 5)
        else:
            img = self.image
            img_pos = self.rect.topleft

        # Apply rounded mask
        masked = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        masked.blit(img, (0, 0))
        mask = pygame.transform.scale(self.rounded_mask, img.get_size())
        masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw image
        surface.blit(masked, img_pos)

        # Dark overlay (removed on hover)
        if not self.hovered:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                overlay,
                (0, 0, 0, 120),   # semi-transparent black
                overlay.get_rect(),
                border_radius=20
            )
            surface.blit(overlay, self.rect.topleft)


        # Glow border on hover
        if self.hovered:
            glow_rect = self.rect.inflate(14, 14)
            pygame.draw.rect(surface, (255, 215, 0), glow_rect, width=4, border_radius=20)

        # Black border always
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=4, border_radius=20)

        # Draw text with outline
        self.draw_text_outline(surface, self.label, self.rect.center)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
class no_mask_ImageButton:
    def __init__(self, x, y, w, h, image_path, label):
        self.rect = pygame.Rect(x, y, w, h)

        # Load and scale image
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        
        self.rounded_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.rounded_mask, (255, 255, 255), (0, 0, w, h), border_radius=40)


        self.label = label
        self.font = pygame.font.Font(BUTTON_FONT, 21)

        self.hovered = False

    def draw_text(self, surface, text, center):
        # Main text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=center)
        surface.blit(text_surf, text_rect)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Hover scale effect
        if self.hovered:
            img = pygame.transform.scale(self.image, (self.rect.width + 10, self.rect.height + 10))
            img_pos = (self.rect.x - 5, self.rect.y - 5)
            self.font = pygame.font.Font(BUTTON_FONT, 24)
        else:
            img = self.image
            img_pos = self.rect.topleft
            self.font = pygame.font.Font(BUTTON_FONT, 21)

        # Blit image
        masked = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        masked.blit(img, (0, 0))

        # Draw image
        surface.blit(masked, img_pos)


        # Glow border on hover
        if self.hovered:
            cx = self.rect.centerx + 1
            cy = self.rect.centery + 1

            # radius slightly larger than the chip
            radius = max(self.rect.width, self.rect.height) // 2 + 8

            pygame.draw.circle(surface, (255, 215, 0), (cx, cy), radius, width=4)


        # Draw text
        self.draw_text(surface, self.label, self.rect.center)

    def is_clicked(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

class CircleButton:
    def __init__(self, x, y, radius, text="x2"):
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text

        self.base_color = (200, 0, 0)
        self.hover_color = (255, 50, 50)
        self.border_color = (0, 0, 0)
        self.text_color = (255, 255, 255)

        self.font = pygame.font.SysFont(None, 40)

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        hovered = (mouse[0] - self.x)**2 + (mouse[1] - self.y)**2 <= self.radius**2

        color = self.hover_color if hovered else self.base_color

        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, self.border_color, (self.x, self.y), self.radius, width=3)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        dx = mouse[0] - self.x
        dy = mouse[1] - self.y

        return pressed and (dx*dx + dy*dy <= self.radius*self.radius)

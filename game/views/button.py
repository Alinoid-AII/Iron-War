import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_selected = False
        
    def draw(self, surface):
        base_color = self.hover_color if (self.is_hovered or self.is_selected) else self.color
        pygame.draw.rect(surface, base_color, self.rect)
        border_color = (208, 217, 208)
        
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.bottom - 1), (self.rect.right, self.rect.bottom - 1), 3)
        pygame.draw.line(surface, border_color, (self.rect.left, self.rect.top), (self.rect.left, self.rect.bottom), 3)
        pygame.draw.line(surface, border_color, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom), 3)
        pygame.draw.rect(surface, border_color, (self.rect.left, self.rect.top, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.right - 3, self.rect.top, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.left, self.rect.bottom - 3, 3, 3))
        pygame.draw.rect(surface, border_color, (self.rect.right - 3, self.rect.bottom - 3, 3, 3))
        
        font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 15)
        text_surface = font.render(self.text, True, (208, 217, 208))
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        if self.is_hovered or self.is_selected:
            text_rect.y += 2
            shadow_surface = font.render(self.text, True, (80, 80, 80))
            shadow_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 2))
            surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click
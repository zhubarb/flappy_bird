import pygame
import random

class Food:
    def __init__(self, x, y, game_speed=3):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = game_speed * 1.5  # Food moves faster than pipes
        self.active = True
        self.food_type = random.choice(["seed", "worm", "berry"])
        self.color = {
            "seed": (240, 230, 140),  # Khaki
            "worm": (255, 105, 180),  # Hot Pink
            "berry": (65, 105, 225)  # Royal Blue
        }[self.food_type]

    def update(self):
        self.x -= self.speed
        # Return True if still on screen
        return self.x > -self.width

    def draw(self, screen):
        if self.food_type == "seed":
            # Draw a seed
            pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.line(screen, (139, 69, 19), (self.x + self.width // 2, self.y - 5),
                             (self.x + self.width // 2 + 5, self.y - 10), 2)

        elif self.food_type == "worm":
            # Draw a worm
            for i in range(3):
                offset = i * (self.width // 3)
                pygame.draw.circle(screen, self.color,
                                  (self.x + offset + self.width // 6, self.y + self.height // 2),
                                  self.width // 6)
            # Worm eyes
            pygame.draw.circle(screen, (0, 0, 0),
                              (self.x + 5, self.y + self.height // 2 - 2), 2)

        elif self.food_type == "berry":
            # Draw a berry
            pygame.draw.circle(screen, self.color,
                              (self.x + self.width // 2, self.y + self.height // 2),
                              self.width // 2)
            # Berry stem
            pygame.draw.line(screen, (0, 100, 0),
                             (self.x + self.width // 2, self.y),
                             (self.x + self.width // 2, self.y - 5), 2)
            # Berry highlight
            pygame.draw.circle(screen, (255, 255, 255),
                              (self.x + self.width // 3, self.y + self.height // 3), 3)

    def collide(self, bird):
        # Create rectangles for collision detection
        food_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Use the bird's collision rectangle if available, otherwise create one
        if hasattr(bird, 'get_collision_rect'):
            bird_rect = bird.get_collision_rect()
        else:
            bird_rect = pygame.Rect(
                bird.x - bird.collision_width // 2,
                bird.y - bird.collision_height // 2,
                bird.collision_width,
                bird.collision_height
            )

        return food_rect.colliderect(bird_rect)
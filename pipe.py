import pygame
import random

class Pipe:
    def __init__(self, x, score_count, total_pipes, screen_width, screen_height, ground_height, game_speed):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.GROUND_HEIGHT = ground_height
        self.GAME_SPEED = game_speed
        self.PIPE_TOP = pygame.Surface((screen_width // 10, screen_height))
        self.PIPE_TOP.fill((0, 128, 0))  # GREEN
        self.PIPE_BOTTOM = pygame.Surface((screen_width // 10, screen_height))
        self.PIPE_BOTTOM.fill((0, 128, 0))  # GREEN
        self.passed = False

        # Calculate gap size parameters
        self.PIPE_GAP_START = 400  # Starting gap size
        self.PIPE_GAP_MIN = 250    # Minimum gap size

        # Calculate the current gap size based on how many pipes have been generated
        progress = min(1.0, total_pipes / 50)  # Reaches minimum after 50 pipes
        self.gap = self.PIPE_GAP_START - (self.PIPE_GAP_START - self.PIPE_GAP_MIN) * progress

        self.set_height()

    def set_height(self):
        # Create a true random height between 20% and 80% of usable screen space
        usable_height = self.SCREEN_HEIGHT - self.GROUND_HEIGHT

        # Ensure the gap can fit within the usable height
        max_pipe_height = usable_height - self.gap

        # Choose a random position for the gap center point
        gap_center = random.randint(
            int(usable_height * 0.2),  # Not too close to the top
            int(usable_height * 0.8)  # Not too close to the ground
        )

        # Calculate top and bottom pipe positions based on the gap center
        self.height = gap_center - (self.gap // 2)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = gap_center + (self.gap // 2)

        # Safety checks to prevent pipes from extending beyond screen boundaries
        if self.bottom > self.SCREEN_HEIGHT - self.GROUND_HEIGHT:
            shift = self.bottom - (self.SCREEN_HEIGHT - self.GROUND_HEIGHT)
            self.bottom -= shift
            self.height -= shift
            self.top -= shift

        if self.height < 0:
            shift = abs(self.height)
            self.height += shift
            self.top += shift
            self.bottom += shift

    def update(self):
        self.x -= self.GAME_SPEED
        return self.x > -self.PIPE_TOP.get_width()

    def draw(self, screen):
        # Draw pipe bodies
        screen.blit(self.PIPE_TOP, (self.x, self.top))
        screen.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

        # Draw pipe caps
        cap_width = int(self.SCREEN_WIDTH // 8)
        cap_height = 20

        # Top pipe cap
        pygame.draw.rect(screen, (0, 100, 0), (
            self.x - 5,
            self.height - cap_height,
            cap_width,
            cap_height
        ))

        # Bottom pipe cap
        pygame.draw.rect(screen, (0, 100, 0), (
            self.x - 5,
            self.bottom,
            cap_width,
            cap_height
        ))

    def collide(self, bird):
        # Get collision rectangles - only for visible parts of pipes
        bird_rect = bird.get_collision_rect()
        
        # Top pipe: only the part from y=0 to self.height (visible part)
        if self.height > 0:
            top_pipe = pygame.Rect(self.x, 0, self.PIPE_TOP.get_width(), self.height)
        else:
            top_pipe = pygame.Rect(0, 0, 0, 0)  # No visible top pipe
            
        # Bottom pipe: from self.bottom to screen bottom
        bottom_pipe = pygame.Rect(self.x, self.bottom, self.PIPE_BOTTOM.get_width(), 
                                 self.SCREEN_HEIGHT - self.GROUND_HEIGHT - self.bottom)

        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)
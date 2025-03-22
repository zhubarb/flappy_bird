import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
GAME_SPEED = 4
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.SysFont('Arial', 30)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.radius = 15

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity

        # Prevent bird from going off the top of the screen
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0

        # Prevent bird from going off the bottom of the screen
        if self.y > SCREEN_HEIGHT - self.radius:
            self.y = SCREEN_HEIGHT - self.radius
            self.velocity = 0

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), self.radius)

    def get_mask(self):
        # Simple collision circle
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(150, 400)
        self.passed = False
        self.width = 50

    def update(self):
        self.x -= GAME_SPEED

    def draw(self):
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.height, self.width, SCREEN_HEIGHT - self.height))
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.height - PIPE_GAP))

    def collide(self, bird):
        bird_mask = bird.get_mask()

        # Create collision rectangles for the pipes
        bottom_pipe = pygame.Rect(self.x, self.height, self.width, SCREEN_HEIGHT - self.height)
        top_pipe = pygame.Rect(self.x, 0, self.width, self.height - PIPE_GAP)

        # Check if the bird collides with either pipe
        return bird_mask.colliderect(bottom_pipe) or bird_mask.colliderect(top_pipe)


def main():
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    last_pipe = pygame.time.get_ticks()

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart the game
                        bird = Bird()
                        pipes = []
                        score = 0
                        game_over = False
                        last_pipe = pygame.time.get_ticks()
                    else:
                        bird.flap()

        if not game_over:
            # Generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = time_now

            # Update objects
            bird.update()

            # Update and remove pipes that have gone off screen
            pipes_to_remove = []
            for pipe in pipes:
                pipe.update()

                # Check for collision
                if pipe.collide(bird):
                    game_over = True

                # Check if passed pipe and not already counted
                if pipe.x + pipe.width < bird.x and not pipe.passed:
                    pipe.passed = True
                    score += 1

                # Remove pipes that are off screen
                if pipe.x + pipe.width < 0:
                    pipes_to_remove.append(pipe)

            # Remove pipes marked for removal
            for pipe in pipes_to_remove:
                pipes.remove(pipe)

        # Draw background
        screen.fill(SKY_BLUE)

        # Draw bird and pipes
        bird.draw()
        for pipe in pipes:
            pipe.draw()

        # Draw score
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (10, 10))

        # Draw game over message
        if game_over:
            game_over_text = font.render('Game Over! Press SPACE to restart', True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

        # Update display
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
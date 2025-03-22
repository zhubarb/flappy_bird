import pygame
import sys
import random
from bird import Bird
from pipe import Pipe

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Improved Flappy Bird')

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.3
FLAP_STRENGTH = -10
GAME_SPEED = 3
PIPE_FREQUENCY = 1800  # milliseconds
PIPE_GAP_START = 400  # Starting gap size
PIPE_GAP_MIN = 250  # Minimum gap size
GAP_DECREASE_RATE = 0.05  # How quickly the gap narrows
GROUND_HEIGHT = 100

# Score tracking
score = 0
font = pygame.font.SysFont('Arial', 32)


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = GAME_SPEED * 1.5  # Food moves faster than pipes
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

    def draw(self):
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

def draw_ground():
    # Draw ground
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

    # Draw grass
    pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 10))

    # Use a fixed seed for consistent y-positions
    random.seed(42)

    # Create fixed y-positions for ground decorations
    ground_y_positions = []
    for i in range(16):
        ground_y_positions.append(random.randint(SCREEN_HEIGHT - GROUND_HEIGHT + 20, SCREEN_HEIGHT - 10))

    # Calculate ground scroll based on game time and speed
    ground_scroll = (pygame.time.get_ticks() * GAME_SPEED // 50) % 50

    # Draw ground patterns that only move horizontally, not vertically
    for i in range(16):
        x = (i * 50 - ground_scroll) % SCREEN_WIDTH
        y = ground_y_positions[i]  # Use fixed y-position for each circle
        pygame.draw.circle(screen, (165, 100, 42), (int(x), int(y)), 5)

    # Reset the random seed
    random.seed()


def draw_clouds():
    # Set a seed so clouds appear in same positions each frame
    random.seed(42)
    for i in range(5):
        cloud_x = (i * 100 + pygame.time.get_ticks() // 100) % (SCREEN_WIDTH + 200) - 100
        cloud_y = 50 + i * 30

        for j in range(3):
            radius = random.randint(20, 30)
            pygame.draw.circle(screen, WHITE, (cloud_x + j * 15, cloud_y), radius)

    # Reset the seed
    random.seed()


def display_score(score):
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))


def game_over_screen():
    game_over_text = font.render('Game Over!', True, WHITE)
    restart_text = font.render('Press R to Restart', True, WHITE)
    final_score = font.render(f'Final Score: {score}', True, WHITE)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


# Main game function
def main():
    global score

    # Reset score when starting a new game
    score = 0

    # Create bird with all necessary parameters
    bird = Bird(
        screen=screen,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        gravity=GRAVITY,
        flap_strength=FLAP_STRENGTH,
        ground_height=GROUND_HEIGHT
    )

    pipes = []
    foods = []
    last_pipe_time = pygame.time.get_ticks()
    last_food_time = pygame.time.get_ticks()
    food_frequency = 3000  # milliseconds between food spawns
    total_pipes_generated = 0
    game_over = False

    # Food counter display
    food_count = 0

    # Game loop
    running = True
    while running:
        clock.tick(FPS)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.flap()
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    main()
                    return

        # Draw background
        screen.fill(SKY_BLUE)
        draw_clouds()

        # Add new pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_FREQUENCY and not game_over:
            total_pipes_generated += 1
            # Create pipe with additional parameters
            pipes.append(Pipe(
                x=SCREEN_WIDTH,
                score_count=score,
                total_pipes=total_pipes_generated,
                screen_width=SCREEN_WIDTH,
                screen_height=SCREEN_HEIGHT,
                ground_height=GROUND_HEIGHT,
                game_speed=GAME_SPEED
            ))
            last_pipe_time = current_time

        # Add new food items
        if current_time - last_food_time > food_frequency and not game_over:
            # Generate food at random height
            food_y = random.randint(50, SCREEN_HEIGHT - GROUND_HEIGHT - 50)
            foods.append(Food(SCREEN_WIDTH, food_y))
            last_food_time = current_time
            # Gradually increase food frequency as game progresses
            food_frequency = max(1500, 3000 - score * 50)  # Gets more frequent with score

        # Update and draw pipes
        for pipe in pipes[:]:
            if not pipe.update():
                pipes.remove(pipe)
            else:
                pipe.draw(screen)  # Pass screen to draw method

                # Check for collisions - ONLY if bird is not in buffer zone
                if bird.y > 0 and pipe.collide(bird):
                    game_over = True
                    bird.alive = False

                # Check if pipe is passed
                if not pipe.passed and pipe.x < bird.x - 20:
                    pipe.passed = True
                    score += 1

        # Update and draw food
        for food in foods[:]:
            if not food.update():
                foods.remove(food)
            else:
                # Check for collision with bird
                if food.active and food.collide(bird):
                    bird.eat_food(food.food_type)
                    food.active = False  # Deactivate food after collision
                    foods.remove(food)  # Remove food from list
                    food_count += 1

                    # Play a sound if you have one
                    # Add a visual effect for food eaten
                    # food_sound.play()

                    continue  # Skip drawing this food

                # Only draw active food
                if food.active:
                    food.draw()

        # Update and draw bird
        if not game_over:
            bird.update()
        bird.draw()

        # Draw ground
        draw_ground()

        # Display score
        display_score(score)

        # Display food count
        food_text = font.render(f'Food: {food_count}', True, WHITE)
        screen.blit(food_text, (10, 50))

        # Display bird size
        size_text = font.render(f'Size: {bird.size_factor:.1f}x', True, WHITE)
        screen.blit(size_text, (10, 90))

        # Check if bird has hit the ground
        if not bird.alive:
            game_over = True
            game_over_screen()

        pygame.display.update()

    pygame.quit()
    sys.exit()


# Run the game
if __name__ == "__main__":
    main()
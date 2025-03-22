import pygame
import random

# Colors for the bird
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)


class Bird:
    def __init__(self, screen, screen_width, screen_height, gravity, flap_strength, ground_height):
        # Store references to game parameters
        self.screen = screen
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.GRAVITY = gravity
        self.FLAP_STRENGTH = flap_strength
        self.GROUND_HEIGHT = ground_height

        # Bird position and physics
        self.x = screen_width // 4
        self.y = screen_height // 2
        self.vel_y = 0

        # Animation state
        self.wing_up = False
        self.wing_counter = 0

        # Game state
        self.alive = True

        # How high the bird can go before being stopped
        self.top_buffer = -30

        # Bird collision box dimensions - starts relatively small
        self.collision_width = 30
        self.collision_height = 30

        # Bird size factor - increases when eating food
        self.size_factor = 1.0
        self.max_size_factor = 2.0

        # Food eaten counter
        self.food_eaten = 0
        self.size_increase = 0.1

        # Bounce effect variables
        self.is_bouncing = False
        self.bounce_time = 0
        self.bounce_duration = 200  # milliseconds
        self.bounce_strength = -8  # Initial upward velocity when bouncing
        self.bounce_count = 0
        self.max_bounces = 3  # Maximum number of bounces before game over

    def update(self):
        # Apply gravity - heavier birds fall faster
        self.vel_y += self.GRAVITY * self.size_factor
        self.y += self.vel_y

        # Wing animation
        self.wing_counter += 1
        if self.wing_counter > 10:
            self.wing_up = not self.wing_up
            self.wing_counter = 0

        # Check boundaries
        if self.y >= self.SCREEN_HEIGHT - self.GROUND_HEIGHT:
            # Bird hits ground
            self.y = self.SCREEN_HEIGHT - self.GROUND_HEIGHT

            # Handle bouncing
            if not self.is_bouncing:
                # Start a new bounce
                self.is_bouncing = True
                self.bounce_time = pygame.time.get_ticks()
                self.vel_y = self.bounce_strength  # Bounce up
                self.bounce_count += 1

                # Check if max bounces exceeded
                if self.bounce_count >= self.max_bounces:
                    self.alive = False
            # If already bouncing, just make sure velocity is bounce strength
            elif self.vel_y > 0:  # If moving downward
                self.vel_y = self.bounce_strength  # Reset the bounce

        # Check if bounce has ended
        if self.is_bouncing and pygame.time.get_ticks() - self.bounce_time > self.bounce_duration:
            self.is_bouncing = False

        # Allow the bird to go slightly above screen but stop velocity
        if self.y <= self.top_buffer:
            self.y = self.top_buffer
            self.vel_y = 0

    def flap(self):
        # Heavier birds have weaker flaps
        self.vel_y = self.FLAP_STRENGTH / self.size_factor

    def eat_food(self, food_type):
        # Increase size based on food type
        self.food_eaten += 1

        # Increase size factor
        if self.size_factor < self.max_size_factor:
            self.size_factor += self.size_increase
            # Ensure we don't exceed max size
            if self.size_factor > self.max_size_factor:
                self.size_factor = self.max_size_factor

        # Update collision box dimensions
        self.collision_width = int(30 * self.size_factor)
        self.collision_height = int(30 * self.size_factor)

    def get_collision_rect(self):
        # Create collision rectangle - adjusted when bird is above screen
        # This prevents collision detection when the bird is in the buffer zone
        if self.y < 0:
            # Make collision box smaller at the top to avoid collisions in buffer zone
            return pygame.Rect(
                self.x - self.collision_width // 2,
                max(0, self.y - self.collision_height // 2),  # Ensure bottom of collision box is visible
                self.collision_width,
                max(1, self.collision_height // 2 + self.y)  # Only the visible part
            )
        else:
            # Normal collision box
            return pygame.Rect(
                self.x - self.collision_width // 2,
                self.y - self.collision_height // 2,
                self.collision_width,
                self.collision_height
            )

    def draw(self):
        # Skip drawing if bird is completely above screen
        if self.y + 15 * self.size_factor < 0:
            return

        # Create a more detailed bird with sprite-like drawing
        # Calculate scaled dimensions based on size factor
        width = int(40 * self.size_factor)
        height = int(30 * self.size_factor)

        # Bird body
        pygame.draw.ellipse(self.screen, YELLOW, (
            self.x - width // 2,
            self.y - height // 2,
            width,
            height
        ))

        # Add shading to body for more dimension
        pygame.draw.ellipse(self.screen, (240, 210, 0), (
            self.x - int(15 * self.size_factor),
            self.y - int(12 * self.size_factor),
            int(30 * self.size_factor),
            int(20 * self.size_factor)
        ))

        # Bird belly
        pygame.draw.ellipse(self.screen, WHITE, (
            self.x - int(10 * self.size_factor),
            self.y - int(5 * self.size_factor),
            int(25 * self.size_factor),
            int(15 * self.size_factor)
        ))

        # Bird wing - more detailed and animated
        wing_y = self.y - int(10 * self.size_factor) if self.wing_up else self.y + int(5 * self.size_factor)
        pygame.draw.ellipse(self.screen, ORANGE, (
            self.x - int(15 * self.size_factor),
            wing_y,
            int(25 * self.size_factor),
            int(12 * self.size_factor)
        ))

        # Wing details
        pygame.draw.arc(self.screen, (200, 100, 0), (
            self.x - int(15 * self.size_factor),
            wing_y,
            int(25 * self.size_factor),
            int(12 * self.size_factor)
        ), 0, 3.14, 2)

        # Bird beak - more pointed and bird-like
        pygame.draw.polygon(self.screen, ORANGE, [
            (self.x + int(18 * self.size_factor), self.y - int(5 * self.size_factor)),
            (self.x + int(32 * self.size_factor), self.y),
            (self.x + int(18 * self.size_factor), self.y + int(5 * self.size_factor))
        ])

        # Bird eye - larger with more detail
        pygame.draw.circle(self.screen, BLACK, (
            self.x + int(12 * self.size_factor),
            self.y - int(8 * self.size_factor)
        ), int(5 * self.size_factor))

        pygame.draw.circle(self.screen, WHITE, (
            self.x + int(14 * self.size_factor),
            self.y - int(10 * self.size_factor)
        ), int(2 * self.size_factor))

        # Bird tail feathers - more feather-like
        pygame.draw.polygon(self.screen, ORANGE, [
            (self.x - int(20 * self.size_factor), self.y - int(10 * self.size_factor)),
            (self.x - int(35 * self.size_factor), self.y - int(18 * self.size_factor)),
            (self.x - int(35 * self.size_factor), self.y - int(8 * self.size_factor)),
            (self.x - int(30 * self.size_factor), self.y),
            (self.x - int(35 * self.size_factor), self.y + int(8 * self.size_factor)),
            (self.x - int(35 * self.size_factor), self.y + int(18 * self.size_factor)),
            (self.x - int(20 * self.size_factor), self.y + int(10 * self.size_factor))
        ])

        # Add details to tail feathers
        pygame.draw.line(self.screen, (200, 100, 0),
                         (self.x - int(25 * self.size_factor), self.y - int(5 * self.size_factor)),
                         (self.x - int(30 * self.size_factor), self.y - int(15 * self.size_factor)),
                         max(1, int(2 * self.size_factor)))

        pygame.draw.line(self.screen, (200, 100, 0),
                         (self.x - int(25 * self.size_factor), self.y + int(5 * self.size_factor)),
                         (self.x - int(30 * self.size_factor), self.y + int(15 * self.size_factor)),
                         max(1, int(2 * self.size_factor)))

        # Draw legs when bouncing off the ground
        if self.is_bouncing and pygame.time.get_ticks() - self.bounce_time < 150:
            # Only draw legs during the first part of the bounce animation
            leg_length = int(15 * self.size_factor)
            foot_length = int(10 * self.size_factor)

            # Left leg
            pygame.draw.line(self.screen, ORANGE,
                             (self.x - int(5 * self.size_factor), self.y + int(15 * self.size_factor)),
                             (self.x - int(10 * self.size_factor), self.y + leg_length),
                             max(1, int(2 * self.size_factor)))

            # Left foot
            pygame.draw.line(self.screen, ORANGE,
                             (self.x - int(10 * self.size_factor), self.y + leg_length),
                             (self.x - int(15 * self.size_factor), self.y + leg_length),
                             max(1, int(2 * self.size_factor)))

            # Right leg
            pygame.draw.line(self.screen, ORANGE,
                             (self.x + int(5 * self.size_factor), self.y + int(15 * self.size_factor)),
                             (self.x + int(10 * self.size_factor), self.y + leg_length),
                             max(1, int(2 * self.size_factor)))

            # Right foot
            pygame.draw.line(self.screen, ORANGE,
                             (self.x + int(10 * self.size_factor), self.y + leg_length),
                             (self.x + int(20 * self.size_factor), self.y + leg_length),
                             max(1, int(2 * self.size_factor)))

        # Uncomment to debug collision box
        # collision_rect = self.get_collision_rect()
        # pygame.draw.rect(self.screen, (255, 0, 0), collision_rect, 1)
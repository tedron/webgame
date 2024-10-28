import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set up the screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube and Laser Beams Enhanced")

# Set up the clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player properties
player_size = 50
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5

# Create player surface and mask
player_surface = pygame.Surface((player_size, player_size))
player_surface.fill(BLUE)
player_mask = pygame.mask.from_surface(player_surface)

# Laser properties
laser_width = 10
laser_warning_time = 1000  # milliseconds
laser_active_time = 1000   # milliseconds
laser_interval = 2000      # milliseconds
laser_timer = 0
lasers = []

# Difficulty scaling
difficulty_timer = 0
difficulty_interval = 5000  # Increase difficulty every 5 seconds

# Define the Laser class
class Laser:
    def __init__(self, orientation):
        self.orientation = orientation
        self.state = 'warning'  # 'warning' or 'active'
        self.warning_timer = laser_warning_time
        self.active_timer = laser_active_time
        self.move = random.choice([True, False])  # Randomly decide if the laser will move
        self.speed = 2  # Speed of moving lasers

        if orientation == 'horizontal':
            self.x = 0
            self.y = random.randint(0, HEIGHT - laser_width)
            self.rect = pygame.Rect(0, self.y, WIDTH, laser_width)
            self.vx = 0
            self.vy = 0
            if self.move:
                self.vy = random.choice([-1, 1]) * self.speed  # Move up or down
        elif orientation == 'vertical':
            self.x = random.randint(0, WIDTH - laser_width)
            self.y = 0
            self.rect = pygame.Rect(self.x, 0, laser_width, HEIGHT)
            self.vx = 0
            self.vy = 0
            if self.move:
                self.vx = random.choice([-1, 1]) * self.speed  # Move left or right
        elif orientation == 'diagonal':
            # For diagonal lasers, pick a random angle (45 or -45 degrees)
            self.angle = random.choice([45, -45])
            self.length = int(math.hypot(WIDTH, HEIGHT)) * 2  # Ensure laser covers the screen
            self.image = pygame.Surface((laser_width, self.length), pygame.SRCALPHA)
            pygame.draw.rect(self.image, RED, (0, 0, laser_width, self.length))
            self.image_orig = self.image
            self.image = pygame.transform.rotate(self.image_orig, self.angle)
            self.rect = self.image.get_rect()
            # Position the laser such that it covers the screen
            if self.angle == 45:
                self.rect.center = (-WIDTH // 2, HEIGHT + HEIGHT // 2)
                if self.move:
                    self.vx = self.speed
                    self.vy = -self.speed
                else:
                    self.vx = 0
                    self.vy = 0
            else:
                self.rect.center = (-WIDTH // 2, -HEIGHT // 2)
                if self.move:
                    self.vx = self.speed
                    self.vy = self.speed
                else:
                    self.vx = 0
                    self.vy = 0
            # Create a mask for collision detection
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
            self.vx = 0
            self.vy = 0
            self.mask = None

    def update(self, dt):
        if self.state == 'warning':
            self.warning_timer -= dt
            if self.warning_timer <= 0:
                self.state = 'active'
        elif self.state == 'active':
            self.active_timer -= dt
            if self.active_timer <= 0:
                return True  # Remove the laser
            # Move the laser if it can move
            if self.move:
                self.rect.x += self.vx
                self.rect.y += self.vy
        return False

    def draw(self, surface):
        if self.state == 'warning':
            if self.orientation == 'diagonal':
                s = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                s.blit(self.image, (0, 0))
                s.fill((255, 0, 0, 100), None, pygame.BLEND_RGBA_MULT)
                surface.blit(s, self.rect)
            else:
                s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 100))
                surface.blit(s, self.rect.topleft)
        elif self.state == 'active':
            if self.orientation == 'diagonal':
                surface.blit(self.image, self.rect)
            else:
                pygame.draw.rect(surface, RED, self.rect)

# Game loop
running = True
while running:
    dt = clock.tick(FPS)
    laser_timer += dt
    difficulty_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        player_pos[1] += player_speed
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed

    # Keep player on the screen
    player_pos[0] = max(0, min(WIDTH - player_size, player_pos[0]))
    player_pos[1] = max(0, min(HEIGHT - player_size, player_pos[1]))

    # Increase difficulty over time
    if difficulty_timer >= difficulty_interval:
        difficulty_timer = 0
        if laser_interval > 500:  # Minimum interval
            laser_interval -= 200  # Decrease interval by 200 ms

    # Spawn lasers occasionally
    if laser_timer >= laser_interval:
        laser_timer = 0
        num_lasers = random.randint(1, 3)  # Spawn 1 to 3 lasers
        for _ in range(num_lasers):
            orientation = random.choice(['horizontal', 'vertical', 'diagonal'])
            laser = Laser(orientation)
            lasers.append(laser)

    # Update lasers
    for laser in lasers[:]:
        remove = laser.update(dt)
        if remove:
            lasers.remove(laser)

    # Check for collisions
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    for laser in lasers:
        if laser.state == 'active':
            if laser.orientation == 'diagonal':
                # Use masks for collision detection
                offset = (int(laser.rect.x - player_rect.x), int(laser.rect.y - player_rect.y))
                overlap = player_mask.overlap(laser.mask, offset)
                if overlap:
                    running = False  # End the game
            else:
                if player_rect.colliderect(laser.rect):
                    running = False  # End the game

    # Drawing everything
    screen.fill(WHITE)
    screen.blit(player_surface, player_rect)
    for laser in lasers:
        laser.draw(screen)

    pygame.display.flip()

pygame.quit()

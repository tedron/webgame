import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set up the screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube and Laser Beams with Undertale Mechanics")

# Set up the clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
ORANGE_TRANS = (255, 165, 0, 100)
BLUE = (0, 0, 255)
BLUE_TRANS = (0, 0, 255, 100)
PLAYER_COLOR = (0, 255, 0)  # Green color for the player

# Player properties
player_size = 50
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_moving = False  # To track if the player is moving

# Create player surface and mask
player_surface = pygame.Surface((player_size, player_size))
player_surface.fill(PLAYER_COLOR)
player_mask = pygame.mask.from_surface(player_surface)
player_rect = player_surface.get_rect(topleft=player_pos)

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

# Maximum number of lasers to prevent overload
MAX_LASERS = 10

# Define the Laser class
class Laser:
    # Pre-create surfaces for warnings and lasers
    horizontal_warning_surfaces = {}
    vertical_warning_surfaces = {}
    horizontal_active_surfaces = {}
    vertical_active_surfaces = {}
    diagonal_images = {}
    diagonal_warning_images = {}

    def __init__(self, orientation):
        self.orientation = orientation
        self.state = 'warning'  # 'warning' or 'active'
        self.warning_timer = laser_warning_time
        self.active_timer = laser_active_time
        self.move = random.choice([True, False])  # Randomly decide if the laser will move
        self.speed = 2  # Speed of moving lasers

        # Randomly choose laser type: 'red', 'blue', or 'orange'
        self.laser_type = random.choice(['red', 'blue', 'orange'])

        # Set colors based on laser type
        if self.laser_type == 'red':
            self.color = RED
            self.color_trans = RED + (100,)
        elif self.laser_type == 'blue':
            self.color = BLUE
            self.color_trans = BLUE + (100,)
        elif self.laser_type == 'orange':
            self.color = ORANGE
            self.color_trans = ORANGE + (100,)

        # Initialize surfaces if not already done
        if self.laser_type not in Laser.horizontal_warning_surfaces:
            # Horizontal surfaces
            Laser.horizontal_warning_surfaces[self.laser_type] = pygame.Surface((WIDTH, laser_width), pygame.SRCALPHA)
            Laser.horizontal_warning_surfaces[self.laser_type].fill(self.color_trans)
            Laser.horizontal_active_surfaces[self.laser_type] = pygame.Surface((WIDTH, laser_width))
            Laser.horizontal_active_surfaces[self.laser_type].fill(self.color)
            # Vertical surfaces
            Laser.vertical_warning_surfaces[self.laser_type] = pygame.Surface((laser_width, HEIGHT), pygame.SRCALPHA)
            Laser.vertical_warning_surfaces[self.laser_type].fill(self.color_trans)
            Laser.vertical_active_surfaces[self.laser_type] = pygame.Surface((laser_width, HEIGHT))
            Laser.vertical_active_surfaces[self.laser_type].fill(self.color)

        if orientation == 'horizontal':
            self.y = random.randint(0, HEIGHT - laser_width)
            self.vx = 0
            self.vy = self.speed if self.move else 0
            self.x = 0
            self.surface = Laser.horizontal_warning_surfaces[self.laser_type]
            self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        elif orientation == 'vertical':
            self.x = random.randint(0, WIDTH - laser_width)
            self.vx = self.speed if self.move else 0
            self.vy = 0
            self.y = 0
            self.surface = Laser.vertical_warning_surfaces[self.laser_type]
            self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        elif orientation == 'diagonal':
            # For diagonal lasers, pick a random angle (45 or -45 degrees)
            self.angle = random.choice([45, -45])

            # Check if images are already created
            if (self.angle, self.laser_type) not in Laser.diagonal_images:
                # Create the active laser image
                length = int(math.hypot(WIDTH, HEIGHT)) * 2
                base_surface = pygame.Surface((laser_width, length), pygame.SRCALPHA)
                base_surface.fill(self.color)
                rotated_image = pygame.transform.rotate(base_surface, self.angle)
                Laser.diagonal_images[(self.angle, self.laser_type)] = rotated_image
                # Create the warning image
                base_surface.fill(self.color_trans)
                rotated_warning_image = pygame.transform.rotate(base_surface, self.angle)
                Laser.diagonal_warning_images[(self.angle, self.laser_type)] = rotated_warning_image

            self.image = Laser.diagonal_images[(self.angle, self.laser_type)]
            self.warning_image = Laser.diagonal_warning_images[(self.angle, self.laser_type)]
            self.surface = self.warning_image
            self.rect = self.surface.get_rect()

            self.vx = self.speed if self.move else 0
            self.vy = self.speed if self.move else 0
            if self.angle == 45:
                self.vy *= -1
                self.rect.center = (-WIDTH // 2, HEIGHT + HEIGHT // 2)
            else:
                self.rect.center = (-WIDTH // 2, -HEIGHT // 2)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
            self.vx = 0
            self.vy = 0
            self.mask = None

    def update(self, dt):
        if self.state == 'warning':
            # Move the warning if the laser will move
            if self.move:
                self.rect.x += self.vx
                self.rect.y += self.vy
            self.warning_timer -= dt
            if self.warning_timer <= 0:
                self.state = 'active'
                # Update the surface to active laser
                if self.orientation == 'horizontal':
                    self.surface = Laser.horizontal_active_surfaces[self.laser_type]
                elif self.orientation == 'vertical':
                    self.surface = Laser.vertical_active_surfaces[self.laser_type]
                else:
                    self.surface = self.image
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
        surface.blit(self.surface, self.rect)

# Game loop
running = True
while running:
    dt = clock.tick(FPS)
    laser_timer += dt
    difficulty_timer += dt

    player_moving = False  # Reset movement flag

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement controls
    keys = pygame.key.get_pressed()
    old_player_pos = player_pos.copy()

    if keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        player_pos[1] += player_speed
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed

    # Check if the player has moved
    if player_pos != old_player_pos:
        player_moving = True

    # Update player rect
    player_rect.topleft = player_pos

    # Keep player on the screen
    player_rect.clamp_ip(screen.get_rect())

    # Increase difficulty over time
    if difficulty_timer >= difficulty_interval:
        difficulty_timer = 0
        if laser_interval > 500:  # Minimum interval
            laser_interval -= 200  # Decrease interval by 200 ms

    # Spawn lasers occasionally
    if laser_timer >= laser_interval and len(lasers) < MAX_LASERS:
        laser_timer = 0
        num_lasers = random.randint(1, 2)  # Limit the number of lasers spawned
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
    for laser in lasers:
        if laser.state == 'active':
            if laser.orientation == 'diagonal':
                # Use masks for collision detection
                offset = (laser.rect.left - player_rect.left, laser.rect.top - player_rect.top)
                if player_mask.overlap(laser.mask, offset):
                    # Apply Undertale mechanics
                    if laser.laser_type == 'blue' and player_moving:
                        running = False  # Player was moving during blue laser
                    elif laser.laser_type == 'orange' and not player_moving:
                        running = False  # Player was stationary during orange laser
                    elif laser.laser_type == 'red':
                        running = False  # Red lasers always damage
            else:
                if player_rect.colliderect(laser.rect):
                    # Apply Undertale mechanics
                    if laser.laser_type == 'blue' and player_moving:
                        running = False  # Player was moving during blue laser
                    elif laser.laser_type == 'orange' and not player_moving:
                        running = False  # Player was stationary during orange laser
                    elif laser.laser_type == 'red':
                        running = False  # Red lasers always damage

    # Drawing everything
    screen.fill(WHITE)
    screen.blit(player_surface, player_rect)
    for laser in lasers:
        laser.draw(screen)

    pygame.display.flip()

pygame.quit()

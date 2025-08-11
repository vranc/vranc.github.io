# === GAME SETTINGS: Set Gauntlet Base Values and Fight Multipliers Here ===
# Base score required for each gauntlet (8 total)
gauntlet_bases = [50, 100, 200, 400, 800, 1600, 3200, 6400]

# Multipliers for each fight type in a gauntlet: Easy, Medium, Boss
fight_multipliers = [1.0, 1.5, 2.0]  # Easy, Medium, Boss
# Example: To get required score for gauntlet 3, boss fight:
# gauntlet_idx = 2  # (0-based, so 2 is the 3rd gauntlet)
# fight_type = 2    # 0=Easy, 1=Medium, 2=Boss
# required_score = int(gauntlet_bases[gauntlet_idx] * fight_multipliers[fight_type])
# === END GAME SETTINGS ===
import pygame  # Import the pygame library for game development


pygame.init()  # Initialize all imported pygame modules


# Launch in large resizable windowed mode with window decorations
gameDisplay = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
pygame.display.set_caption('Wordler')  # Set the window title to 'Wordler'

# Get current screen width for centering
screen_width, screen_height = gameDisplay.get_size()

# Set up font for displaying text
font = pygame.font.SysFont(None, 60)

# Load a word list from a file (e.g., words_alpha.txt from https://github.com/dwyl/english-words)
with open("words_alpha.txt", "r") as f:
    word_set = set(word.strip().lower() for word in f)

black = (0,0,0)  # Define the color black as an RGB tuple
white = (255,255,255)  # Define the color white as an RGB tuple
green = (0, 200, 0)  # Color for valid word
red = (200, 0, 0)    # Color for invalid word

clock = pygame.time.Clock()  # Create a clock object to control the frame rate


# Number of input boxes (scalable)
input_length = 4  # Change this value to set number of boxes

# User input string
user_text = ""

# Score counter
score = 0

# Money counter
money = 0

fight_types = ["Easy", "Medium", "Boss"] * 2 + ["Easy", "Medium"]  # 8 fights: Easy, Medium, Boss, Easy, Medium, Boss, Easy, Medium
fight_rewards = [3, 5, 10] * 2 + [3, 5]  # 8 rewards
current_fight = 1
required_score = int(gauntlet_bases[0] * fight_multipliers[0])

# Result of dictionary check
is_valid_word = None

# Animation for word result message
result_anim = {
    'active': False,
    'text': '',
    'color': (0,0,0),
    'y': 0,
    'alpha': 255,
    'timer': 0.0
}


# Shop button state
shop_button_rect = None
shop_open = False
shop_instance = None


# Shop class
class Shop:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.buttons = []
        self.selected = None
        self.back_button = None
        self.chisel_cost = 2
        self.hovered = None
        self.create_buttons()

    def create_buttons(self):
        # Layout: 2 on top, 3 below, all rectangular
        screen_width, screen_height = self.screen.get_size()
        btn_w, btn_h = 220, 70
        margin_x = 40
        margin_y = 30
        start_x = (screen_width - (btn_w * 2 + margin_x)) // 2
        start_y = (screen_height - (btn_h * 2 + margin_y)) // 2
        self.buttons.clear()
        # Top row (2 buttons)
        for i in range(2):
            rect = pygame.Rect(start_x + i * (btn_w + margin_x), start_y, btn_w, btn_h)
            if i == 0:
                self.buttons.append((rect, "Chisel"))
            else:
                self.buttons.append((rect, f"ShopBtn {i+1}"))
        # Bottom row (3 buttons)
        start_x2 = (screen_width - (btn_w * 3 + margin_x * 2)) // 2
        for i in range(3):
            rect = pygame.Rect(start_x2 + i * (btn_w + margin_x), start_y + btn_h + margin_y, btn_w, btn_h)
            self.buttons.append((rect, f"ShopBtn {i+3+1}"))
        # Back button (bottom right corner)
        back_w, back_h = 180, 60
        back_x = screen_width - back_w - 40
        back_y = screen_height - back_h - 40
        self.back_button = pygame.Rect(back_x, back_y, back_w, back_h)

    def draw(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # Draw shop box higher up
        sw, sh = self.screen.get_size()
        shop_rect = pygame.Rect(sw//2-400, sh//2-250-100, 800, 500)
        pygame.draw.rect(self.screen, (245, 245, 245), shop_rect, border_radius=18)
        pygame.draw.rect(self.screen, (30, 144, 255), shop_rect, 4, border_radius=18)
        # Draw shop buttons (rectangular)
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = None
        for idx, (rect, label) in enumerate(self.buttons):
            color = (50, 205, 50) if self.selected == idx else (30, 144, 255)
            if rect.collidepoint(mouse_pos):
                self.hovered = (rect, label)
            pygame.draw.rect(self.screen, color, rect, border_radius=14)
            pygame.draw.rect(self.screen, (0,0,0), rect, 3, border_radius=14)
            # Show cost for Chisel
            if label == "Chisel":
                text = self.font.render(f"Chisel (${self.chisel_cost})", True, (255,255,255))
            else:
                text = self.font.render(label, True, (255,255,255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        # Draw description window if hovering
        if self.hovered:
            rect, label = self.hovered
            if label == "Chisel":
                desc = "Increases max letters by 1!\nEach purchase increases the cost by $4."
            else:
                desc = f"Description for {label}"
            desc_font = pygame.font.SysFont(None, 36)
            # Render multi-line description
            lines = desc.split("\n")
            surfaces = [desc_font.render(line, True, (30,30,30)) for line in lines]
            width = max(s.get_width() for s in surfaces)
            height = sum(s.get_height() for s in surfaces) + (len(surfaces)-1)*4
            desc_bg = pygame.Surface((width+24, height+16), pygame.SRCALPHA)
            desc_bg.fill((255,255,255,230))
            px = rect.right + 20
            py = rect.top
            self.screen.blit(desc_bg, (px, py))
            y_offset = py + 8
            for s in surfaces:
                self.screen.blit(s, (px+12, y_offset))
                y_offset += s.get_height() + 4
        # Draw Back button (curved)
        pygame.draw.rect(self.screen, (220, 20, 60), self.back_button, border_radius=14)
        pygame.draw.rect(self.screen, (0,0,0), self.back_button, 3, border_radius=14)
        back_text = self.font.render("Back", True, (255,255,255))
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)

    def handle_event(self, event):
        global money
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, (rect, label) in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected = idx
                    # Chisel purchase logic
                    if label == "Chisel":
                        if money >= self.chisel_cost:
                            money -= self.chisel_cost
                            self.chisel_cost += 4
                            return "Chisel"
                        else:
                            return None
                    return label
            if self.back_button and self.back_button.collidepoint(event.pos):
                return "BACK"
        return None

crashed = False  # Variable to control the main game loop


while not crashed:  # Main game loop


    for event in pygame.event.get():  # Get all events from the event queue
        if event.type == pygame.QUIT:  # If the user clicks the close button
            crashed = True  # Exit the main loop

        if shop_open:
            # Pass events to shop instance
            result = shop_instance.handle_event(event)
            if result == "BACK":
                shop_open = False
                shop_instance = None
            elif result == "Chisel":
                input_length += 1
                shop_instance.create_buttons()  # Recreate shop buttons for new layout
            elif result:
                print(f"Clicked {result}")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                shop_open = False
                shop_instance = None
        else:
            # Handle key presses for text input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check if the entered word is valid using the word set
                    if len(user_text) > 0:
                        is_valid_word = user_text.lower() in word_set
                        if is_valid_word:
                            # 5 for first letter, 10 for second, 15 for third, etc.
                            word_score = sum((i + 1) * 5 for i in range(len(user_text)))
                            score += word_score
                            # Start animation for valid word
                            result_anim['active'] = True
                            result_anim['text'] = "Valid word!"
                            result_anim['color'] = green
                            result_anim['timer'] = 0.0
                        else:
                            # Start animation for invalid word
                            result_anim['active'] = True
                            result_anim['text'] = "Not a valid word!"
                            result_anim['color'] = red
                            result_anim['timer'] = 0.0
                    else:
                        is_valid_word = None
                    # Check if player can advance to next fight
                    # Only check for fight advancement after a valid word submission
                    if is_valid_word:
                        if score >= required_score:
                            # Award money for this fight
                            money += fight_rewards[current_fight-1]
                            if current_fight < 8:
                                current_fight += 1
                                gauntlet_idx = (current_fight-1) // 3
                                fight_idx = (current_fight-1) % 3
                                required_score = int(gauntlet_bases[gauntlet_idx] * fight_multipliers[fight_idx])
                            else:
                                # Completed all gauntlets, reset and increment rewards
                                current_fight = 1
                                required_score = int(gauntlet_bases[0] * fight_multipliers[0])
                                for i in range(len(fight_rewards)):
                                    fight_rewards[i] += 1
                            # Reset score after advancing fight
                            score = 0
                    user_text = ""  # Always clear input after pressing Enter
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key <= 127:
                    # Only allow standard ASCII characters and up to input_length
                    if event.unicode.isalpha() and len(user_text) < input_length:
                        user_text += event.unicode

            # Handle mouse click for shop button
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if shop_button_rect and shop_button_rect.collidepoint(event.pos):
                    shop_open = True
                    shop_instance = Shop(gameDisplay, font)


    # Fill background
    gameDisplay.fill(white)

    # Get current window size for centering
    screen_width, screen_height = gameDisplay.get_size()

    # Always draw main game UI (score, money, gauntlet, letter boxes, shop button)
    # Draw score counter (top left)
    score_surface = font.render(f"Score: {score}", True, (30, 144, 255))
    gameDisplay.blit(score_surface, (40, 30))
    # Draw money counter under score
    money_surface = font.render(f"Money: ${money}", True, (34, 139, 34))
    gameDisplay.blit(money_surface, (40, 100))
    # Draw gauntlet fight info
    fight_type = fight_types[current_fight-1]
    fight_surface = font.render(f"Fight: {current_fight} ({fight_type})", True, (255, 69, 0))
    req_surface = font.render(f"Required Score: {required_score}", True, (255, 140, 0))
    gameDisplay.blit(fight_surface, (40, 170))
    gameDisplay.blit(req_surface, (40, 240))
    box_size = 80
    box_margin = 20
    total_width = input_length * box_size + (input_length - 1) * box_margin
    start_x = (screen_width - total_width) // 2  # Center horizontally in current window
    # Place boxes in the bottom half of the screen
    start_y = screen_height // 2 + screen_height // 4 - box_size // 2
    # Draw Shop button (bottom right corner)
    button_width, button_height = 180, 70
    button_x = screen_width - button_width - 40
    button_y = screen_height - button_height - 40
    shop_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(gameDisplay, (30, 144, 255), shop_button_rect, border_radius=12)
    pygame.draw.rect(gameDisplay, black, shop_button_rect, 3, border_radius=12)
    shop_text = font.render("Shop", True, white)
    shop_text_rect = shop_text.get_rect(center=shop_button_rect.center)
    gameDisplay.blit(shop_text, shop_text_rect)
    for i in range(input_length):
        rect = pygame.Rect(start_x + i * (box_size + box_margin), start_y, box_size, box_size)
        pygame.draw.rect(gameDisplay, black, rect, 2)
        if i < len(user_text):
            char_surface = font.render(user_text[i], True, black)
            # Center the character in the box
            char_rect = char_surface.get_rect(center=rect.center)
            gameDisplay.blit(char_surface, char_rect)
    # If shop is open, draw it as an overlay
    if shop_open:
        shop_instance.draw()


    # Show result if checked (only in main game, not shop)

    # Animated result message above input boxes
    if not shop_open and result_anim['active']:
        # Animation parameters
        # Start just above the input boxes, scroll up and fade out
        anim_duration = 1.0  # seconds to linger before fade/scroll
        fade_duration = 1.0  # seconds to fade/scroll out
        dt = clock.get_time() / 1000.0
        result_anim['timer'] += dt
        # Get current window size and input box position
        screen_width, screen_height = gameDisplay.get_size()
        box_size = 80
        box_margin = 20
        total_width = input_length * box_size + (input_length - 1) * box_margin
        start_x = (screen_width - total_width) // 2
        start_y = screen_height // 2 + screen_height // 4 - box_size // 2
        msg_y = start_y - 60
        # Linger, then scroll up and fade
        if result_anim['timer'] < anim_duration:
            y = msg_y
            alpha = 255
        else:
            t = min((result_anim['timer'] - anim_duration) / fade_duration, 1.0)
            y = msg_y - int(60 * t)
            alpha = int(255 * (1.0 - t))
        # Render with alpha
        msg_surface = font.render(result_anim['text'], True, result_anim['color'])
        msg_surface.set_alpha(alpha)
        msg_rect = msg_surface.get_rect(center=(screen_width // 2, y))
        gameDisplay.blit(msg_surface, msg_rect)
        # End animation
        if result_anim['timer'] >= anim_duration + fade_duration:
            result_anim['active'] = False

    pygame.display.update()  # Update the contents of the entire display
    clock.tick(60)  # Limit the loop to 60 frames per second

pygame.quit()  # Uninitialize all pygame modules
quit()  # Exit the program

import pygame
import random
import asyncio
import platform
import json
from uuid import uuid4

# Initialize Pygame
pygame.init()

# Window dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack")

# Load existing images
CHIP_50 = pygame.transform.scale(pygame.image.load("assets/chip_50.png"), (80, 80))
CHIP_100 = pygame.transform.scale(pygame.image.load("assets/chip_100.png"), (80, 80))
CHIP_200 = pygame.transform.scale(pygame.image.load("assets/chip_200.png"), (80, 80))
CHIP_500 = pygame.transform.scale(pygame.image.load("assets/chip_500.png"), (80, 80))

CARD_WIDTH, CARD_HEIGHT = 150, 210
CARDS = {}
suits = ["hearts", "diamonds", "clubs", "spades"]
values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
for suit in suits:
    for value in values:
        CARDS[f"{value}_of_{suit}"] = pygame.transform.scale(
            pygame.image.load(f"assets/cards/{value}_of_{suit}.png"), (CARD_WIDTH, CARD_HEIGHT)
        )
CARD_BACK = pygame.transform.scale(pygame.image.load("assets/cards/back.png"), (CARD_WIDTH, CARD_HEIGHT))

# Load wallpapers
WALLPAPERS = {
    "default": pygame.transform.scale(pygame.image.load("assets/wallpaper1.png"), (WIDTH, HEIGHT)),
    "wood": pygame.transform.scale(pygame.image.load("assets/wallpaper2.png"), (WIDTH, HEIGHT)),
    "marble": pygame.transform.scale(pygame.image.load("assets/wallpaper3.png"), (WIDTH, HEIGHT))
}
WALLPAPER_PRICES = {"default": 0, "wood": 500, "marble": 1000}
OWNED_WALLPAPERS = ["default"]
CURRENT_WALLPAPER = "default"

# Colors and fonts
GREEN_FELT = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (200, 0, 0)
font = pygame.font.SysFont("arial", 30)
small_font = pygame.font.SysFont("arial", 24)
large_font = pygame.font.SysFont("arial", 50)

# File for persistent storage
SAVE_FILE = "game_state.json"

# Load game state from file
def load_game_state():
    global LOCAL_STORAGE, OWNED_WALLPAPERS, CURRENT_WALLPAPER
    try:
        with open(SAVE_FILE, 'r') as f:
            LOCAL_STORAGE.update(json.load(f))
    except FileNotFoundError:
        LOCAL_STORAGE = {"balance": 1000, "owned_wallpapers": ["default"], "current_wallpaper": "default"}
    game.balance = LOCAL_STORAGE.get("balance", 1000)
    OWNED_WALLPAPERS = LOCAL_STORAGE.get("owned_wallpapers", ["default"])
    CURRENT_WALLPAPER = LOCAL_STORAGE.get("current_wallpaper", "default")
    print(f"Loaded game state - Balance: {game.balance}, Wallpaper: {CURRENT_WALLPAPER}")

# Save game state to file
def save_game_state():
    global LOCAL_STORAGE
    LOCAL_STORAGE["balance"] = game.balance
    LOCAL_STORAGE["owned_wallpapers"] = OWNED_WALLPAPERS
    LOCAL_STORAGE["current_wallpaper"] = CURRENT_WALLPAPER
    with open(SAVE_FILE, 'w') as f:
        json.dump(LOCAL_STORAGE, f)
    print(f"Saved game state - Balance: {LOCAL_STORAGE['balance']}, Wallpaper: {LOCAL_STORAGE['current_wallpaper']}")

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.clicked = False

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        text_surf = small_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

# Text input class
class TextInput:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self):
        pygame.draw.rect(screen, WHITE if self.active else (200, 200, 200), self.rect, border_radius=5)
        text_surf = small_font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

# Blackjack game class
class Blackjack:
    def __init__(self):
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.balance = LOCAL_STORAGE.get("balance", 1000)
        self.bet = 0
        self.state = "main_menu"
        self.stats = {"games": 0, "wins": 0, "losses": 0, "pushes": 0}
        self.buttons = []
        self.result_displayed = False
        self.result_message = ""
        self.error_message = ""
        self.chip_buttons = [
            Button(50, 50, 100, 50, "Bet 50", (0, 128, 0), (0, 200, 0)),
            Button(50, 120, 100, 50, "Bet 100", (0, 128, 0), (0, 200, 0)),
            Button(50, 190, 100, 50, "Bet 200", (0, 128, 0), (0, 200, 0)),
            Button(50, 260, 100, 50, "Bet 500", (0, 128, 0), (0, 200, 0))
        ]
        self.main_menu_buttons = [
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 100, 165, 60, "Start", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 100, HEIGHT // 2 - 20, 165, 60, "Buy", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 165, 60, "Change Wallpaper", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 140, 165, 60, "Exit", (128, 0, 0), (200, 0, 0))
        ]
        self.purchase_buttons = [
            Button(WIDTH // 2 - 300, HEIGHT // 2 + 200, 120, 50, "Buy 500", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 150, HEIGHT // 2 + 200, 120, 50, "Buy 1000", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 + 0, HEIGHT // 2 + 200, 120, 50, "Buy 2000", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 260, 200, 80, "Back", (128, 0, 0), (200, 0, 0))
        ]
        self.wallpaper_buttons = [
            Button(WIDTH // 2 - 250, HEIGHT // 2 - 20, 120, 50, "Default", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 250, HEIGHT // 2 + 40, 120, 50, "Wood", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 250, HEIGHT // 2 + 100, 120, 50, "Flower", (0, 128, 0), (0, 200, 0)),
            Button(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 80, "Back", (128, 0, 0), (200, 0, 0))
        ]
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 80, "Start", (0, 128, 0), (0, 200, 0))
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 80, "Exit", (128, 0, 0), (200, 0, 0))
        self.card_input = TextInput(WIDTH // 2 - 350, HEIGHT // 2 - 40, 600, 40)
        self.exp_date_input = TextInput(WIDTH // 2 - 350, HEIGHT // 2 + 20, 600, 40)
        self.cvv_input = TextInput(WIDTH // 2 - 350, HEIGHT // 2 + 80, 600, 40)
        self.main_menu_button = Button(WIDTH - 200, 20, 150, 50, "Main Menu", (0, 128, 0), (0, 200, 0))
        self.create_deck()

    def create_deck(self):
        self.deck = [f"{value}_of_{suit}" for suit in suits for value in values]
        random.shuffle(self.deck)

    def deal_initial_cards(self):
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

    def get_card_value(self, card):
        value = card.split("_")[0]
        if value in ["jack", "queen", "king"]:
            return 10
        elif value == "ace":
            return 11
        return int(value)

    def calculate_hand(self, hand):
        score = 0
        aces = 0
        for card in hand:
            value = self.get_card_value(card)
            if value == 11:
                aces += 1
            score += value
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def dealer_play(self):
        while self.calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

    def determine_winner(self):
        if self.result_displayed:
            return self.result_message
        self.result_displayed = True
        player_score = self.calculate_hand(self.player_hand)
        dealer_score = self.calculate_hand(self.dealer_hand)
        self.stats["games"] += 1
        result = ""
        if player_score > 21:
            self.stats["losses"] += 1
            result = "Dealer wins!"
        elif dealer_score > 21 or player_score > dealer_score:
            self.balance += self.bet * 2
            self.stats["wins"] += 1
            result = "Player wins!"
        elif dealer_score > player_score:
            self.stats["losses"] += 1
            result = "Dealer wins!"
        else:
            self.balance += self.bet
            self.stats["pushes"] += 1
            result = "Push!"
        self.bet = 0
        self.result_message = result
        save_game_state()
        return result

    def validate_card(self, card_num, exp_date, cvv):
        try:
            if len(card_num) != 16 or not card_num.isdigit():
                return False, "Card number must be 16 digits!"
            month, year = map(int, exp_date.split('/'))
            if month < 1 or month > 12 or year < 25 or len(exp_date) != 5:
                return False, "Invalid expiration date! Use MM/YY."
            if len(cvv) != 3 or not cvv.isdigit():
                return False, "CVV must be 3 digits!"
            return True, "Transaction simulated successfully!"
        except:
            return False, "Invalid data!"

    def draw(self):
        screen.blit(WALLPAPERS[CURRENT_WALLPAPER], (0, 0))

        if self.state == "main_menu":
            window_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 250, 500, 500)
            pygame.draw.rect(screen, BLACK, window_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, window_rect, 5, border_radius=20)
            title_text = large_font.render("Blackjack", True, GOLD)
            screen.blit(title_text, (WIDTH // 2 - 100, HEIGHT // 2 - 200))
            subtitle_text = font.render(f"Balance: ${self.balance}", True, WHITE)
            screen.blit(subtitle_text, (WIDTH // 2 - 80, HEIGHT // 2 - 140))
            for button in self.main_menu_buttons:
                button.draw()
            return

        if self.state == "purchase":
            window_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
            pygame.draw.rect(screen, BLACK, window_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, window_rect, 5, border_radius=20)
            title_text = large_font.render("Buy Currency", True, GOLD)
            screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 2 - 250))

            # Define positions and spacing
            label_x = WIDTH // 2 - 350
            label_y_start = HEIGHT // 2 - 140
            label_spacing = 100
            input_width = 400
            input_height = 30
            input_x = label_x + 320

            # Card Number
            card_label = small_font.render("Card Number (16 digits):", True, WHITE)
            screen.blit(card_label, (label_x, label_y_start + 10))
            self.card_input.rect.x = input_x
            self.card_input.rect.y = label_y_start + 5
            self.card_input.rect.width = input_width
            self.card_input.rect.height = input_height
            self.card_input.draw()

            # Exp Date
            exp_label = small_font.render("Exp Date (MM/YY):", True, WHITE)
            screen.blit(exp_label, (label_x, label_y_start + label_spacing + 10))
            self.exp_date_input.rect.x = input_x
            self.exp_date_input.rect.y = label_y_start + label_spacing + 5
            self.exp_date_input.rect.width = input_width
            self.exp_date_input.rect.height = input_height
            self.exp_date_input.draw()

            # CVV
            cvv_label = small_font.render("CVV (3 digits):", True, WHITE)
            screen.blit(cvv_label, (label_x, label_y_start + 2 * label_spacing + 10))
            self.cvv_input.rect.x = input_x
            self.cvv_input.rect.y = label_y_start + 2 * label_spacing + 5
            self.cvv_input.rect.width = input_width
            self.cvv_input.rect.height = input_height
            self.cvv_input.draw()

            # Purchase buttons
            for button in self.purchase_buttons[:-1]:
                button.draw()
            self.purchase_buttons[-1].draw()

            # Error or success message
            if self.error_message:
                error_text = small_font.render(self.error_message, True, RED)
                screen.blit(error_text, (WIDTH // 2 - 390, HEIGHT // 2 + 150))
            return

        if self.state == "wallpaper":
            window_rect = pygame.Rect(WIDTH // 2 - 400, HEIGHT // 2 - 300, 800, 600)
            pygame.draw.rect(screen, BLACK, window_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, window_rect, 5, border_radius=20)
            title_text = large_font.render("Change Wallpaper", True, GOLD)
            screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 2 - 250))
            balance_text = font.render(f"Balance: ${self.balance}", True, WHITE)
            screen.blit(balance_text, (WIDTH // 2 - 390, HEIGHT // 2 - 180))

            # Define positions and spacing
            label_x = WIDTH // 2 - 390
            button_x = label_x + 200
            y_offset = HEIGHT // 2 - 80
            button_spacing = 60

            # Display wallpapers with buttons aligned to the right
            wallpaper_options = [("Default", "default", "Owned" if "default" in OWNED_WALLPAPERS else None),
                                ("Wood", "wood",
                                 f"${WALLPAPER_PRICES['wood']}" if "wood" not in OWNED_WALLPAPERS else "Owned"),
                                ("Flower", "flower",
                                 f"${WALLPAPER_PRICES['marble']}" if "marble" not in OWNED_WALLPAPERS else "Owned")]
            for i, (button_text, wp, status) in enumerate(wallpaper_options):
                status_text = small_font.render(f"{button_text}: {status}", True, WHITE)
                screen.blit(status_text, (label_x, y_offset + i * button_spacing))
                self.wallpaper_buttons[i].rect.x = button_x
                self.wallpaper_buttons[i].rect.y = y_offset + i * button_spacing - 5
                self.wallpaper_buttons[i].draw()

            # Back button
            self.wallpaper_buttons[3].rect.x = WIDTH // 2 - 50
            self.wallpaper_buttons[3].rect.y = y_offset + 3 * button_spacing + 10
            self.wallpaper_buttons[3].draw()

            if self.error_message:
                error_text = small_font.render(self.error_message, True, RED)
                screen.blit(error_text, (WIDTH // 2 - 390, HEIGHT // 2 + 150))
            return

        if self.state == "start":
            window_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 200, 500, 500)
            pygame.draw.rect(screen, BLACK, window_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, window_rect, 5, border_radius=20)
            title_text = large_font.render("Blackjack", True, GOLD)
            screen.blit(title_text, (WIDTH // 2 - 100, HEIGHT // 2 - 150))
            subtitle_text = font.render("Welcome to the Casino!", True, WHITE)
            screen.blit(subtitle_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
            self.start_button.draw()
            self.exit_button.draw()
            return

        if self.state == "game_over":
            window_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 180, 580, 500)
            pygame.draw.rect(screen, BLACK, window_rect, border_radius=20)
            pygame.draw.rect(screen, GOLD, window_rect, 5, border_radius=20)
            game_over_text = large_font.render("Game Over!", True, GOLD)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 150))
            stats_text = font.render(
                f"Games: {self.stats['games']} | Wins: {self.stats['wins']} | Losses: {self.stats['losses']} | Pushes: {self.stats['pushes']}",
                True, WHITE
            )
            screen.blit(stats_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
            balance_change = self.balance - 1000
            balance_text = font.render(f"Balance Change: {'+' if balance_change >= 0 else ''}{balance_change}$", True,
                                       WHITE)
            screen.blit(balance_text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
            for button in self.buttons:
                button.draw()
            return

        balance_text = font.render(f"Balance: ${self.balance}", True, GOLD)
        screen.blit(balance_text, (50, HEIGHT - 50))
        bet_text = font.render(f"Bet: ${self.bet}", True, GOLD)
        screen.blit(bet_text, (50, HEIGHT - 100))

        screen.blit(CHIP_50, (170, 50))
        screen.blit(CHIP_100, (170, 120))
        screen.blit(CHIP_200, (170, 190))
        screen.blit(CHIP_500, (170, 260))

        for i, card in enumerate(self.player_hand):
            offset = min(80, 400 // max(1, len(self.player_hand)))
            start_x = WIDTH // 2 - (len(self.player_hand) * offset) // 2
            screen.blit(CARDS[card], (start_x + i * offset, HEIGHT - 250))
        for i, card in enumerate(self.dealer_hand):
            if self.state == "playing" and i == 1:
                screen.blit(CARD_BACK, (WIDTH // 2 - 100 + i * 80, 50))
            else:
                screen.blit(CARDS[card], (WIDTH // 2 - 100 + i * 80, 50))

        if self.state in ["playing", "result"]:
            player_score = self.calculate_hand(self.player_hand)
            dealer_score = self.calculate_hand(self.dealer_hand) if self.state == "result" else 0
            player_score_text = font.render(f"Player: {player_score}", True, WHITE)
            screen.blit(player_score_text, (WIDTH // 2 - 100, HEIGHT - 300))
            dealer_score_text = font.render(f"Dealer: {dealer_score}", True, WHITE)
            screen.blit(dealer_score_text, (WIDTH // 2 - 100, 20))

        if self.state == "result":
            result_text = font.render(self.result_message, True, GOLD)
            screen.blit(result_text, (WIDTH // 2 - 100, HEIGHT // 2))

        # Draw buttons, including Main Menu button during betting, playing, or result states
        buttons_to_draw = self.buttons + (self.chip_buttons if self.state in ["betting", "playing"] else [])
        if self.state in ["betting", "playing", "result"]:
            buttons_to_draw.append(self.main_menu_button)
        for button in buttons_to_draw:
            button.draw()

    def reset(self, new_state="betting"):
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.bet = 0
        self.state = new_state
        self.buttons = []
        self.result_displayed = False
        self.result_message = ""
        self.error_message = ""
        self.create_deck()
        save_game_state()

    def reset_game(self):
        self.balance = 1000
        self.stats = {"games": 0, "wins": 0, "losses": 0, "pushes": 0}
        self.result_displayed = False
        self.result_message = ""
        self.error_message = ""
        self.reset(new_state="main_menu")

# Initialize game
LOCAL_STORAGE = {}  # Initialize as empty to be populated by load_game_state
game = Blackjack()
load_game_state()

def setup():
    game.create_deck()

async def update_loop():
    global game, OWNED_WALLPAPERS, CURRENT_WALLPAPER
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game_state()
            pygame.quit()
            return

        if game.state == "main_menu":
            for i, button in enumerate(game.main_menu_buttons):
                if button.is_clicked(event):
                    if button.text == "Start":
                        game.state = "start"
                    elif button.text == "Buy":
                        game.state = "purchase"
                    elif button.text == "Change Wallpaper":
                        game.state = "wallpaper"
                    elif button.text == "Exit":
                        save_game_state()
                        pygame.quit()
                        return

        if game.state == "purchase":
            game.card_input.handle_event(event)
            game.exp_date_input.handle_event(event)
            game.cvv_input.handle_event(event)
            for button in game.purchase_buttons:
                if button.is_clicked(event):
                    if button.text.startswith("Buy"):
                        amount = int(button.text.split()[1])
                        card_num = game.card_input.text
                        exp_date = game.exp_date_input.text
                        cvv = game.cvv_input.text
                        is_valid, message = game.validate_card(card_num, exp_date, cvv)
                        if is_valid:
                            game.balance += amount
                            game.error_message = f"Transaction of ${amount} completed successfully!"
                            game.card_input.text = ""
                            game.exp_date_input.text = ""
                            game.cvv_input.text = ""
                        else:
                            game.error_message = message
                        save_game_state()
                    elif button.text == "Back":
                        game.state = "main_menu"
                        game.card_input.text = ""
                        game.exp_date_input.text = ""
                        game.cvv_input.text = ""
                        game.error_message = ""

        if game.state == "wallpaper":
            for i, button in enumerate(game.wallpaper_buttons[:-1]):
                if button.is_clicked(event):
                    wallpaper_options = [("Default", "default"), ("Wood", "wood"), ("Marble", "marble")]
                    button_text, wp = wallpaper_options[i]
                    if wp in OWNED_WALLPAPERS:
                        CURRENT_WALLPAPER = wp
                        game.error_message = ""
                        save_game_state()
                    elif game.balance >= WALLPAPER_PRICES[wp]:
                        game.balance -= WALLPAPER_PRICES[wp]
                        OWNED_WALLPAPERS.append(wp)
                        CURRENT_WALLPAPER = wp
                        game.error_message = ""
                        save_game_state()
                    else:
                        game.error_message = "Insufficient balance!"
            if game.wallpaper_buttons[3].is_clicked(event):
                game.state = "main_menu"

        if game.state == "start":
            if game.start_button.is_clicked(event):
                game.state = "betting"
            elif game.exit_button.is_clicked(event):
                save_game_state()
                pygame.quit()
                return

        if game.state in ["betting", "playing", "result"]:
            if game.main_menu_button.is_clicked(event):
                game.reset(new_state="main_menu")
                continue

            for button in game.chip_buttons:
                if button.is_clicked(event):
                    bet_amount = int(button.text.split()[1])
                    if game.balance >= bet_amount:
                        game.bet += bet_amount
                        game.balance -= bet_amount
                        save_game_state()
                        if game.state == "betting":
                            game.state = "playing"
                            game.deal_initial_cards()
                            game.buttons = [
                                Button(WIDTH - 200, HEIGHT - 200, 80, 50, "Hit", (0, 128, 0), (0, 200, 0)),
                                Button(WIDTH - 200, HEIGHT - 130, 80, 50, "Stand", (0, 128, 0), (0, 200, 0))
                            ]

        if game.state == "playing":
            for button in game.buttons:
                if button.is_clicked(event):
                    if button.text == "Hit":
                        game.player_hand.append(game.deck.pop())
                    elif button.text == "Stand":
                        game.dealer_play()
                        game.state = "result"
                        game.determine_winner()
                        game.buttons = [
                            Button(WIDTH - 200, HEIGHT - 200, 90, 50, "Play Again", (0, 128, 0), (0, 200, 0))
                        ]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.player_hand.append(game.deck.pop())
                elif event.key == pygame.K_RETURN:
                    game.dealer_play()
                    game.state = "result"
                    game.determine_winner()
                    game.buttons = [
                        Button(WIDTH - 200, HEIGHT - 200, 100, 50, "Play Again", (0, 128, 0), (0, 200, 0))
                    ]

        if game.state == "result":
            for button in game.buttons:
                if button.is_clicked(event):
                    if button.text == "Play Again":
                        if game.balance <= 0:
                            game.state = "game_over"
                            game.buttons = [
                                Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 80, "Reset Game", (0, 128, 0),
                                       (0, 200, 0)),
                                Button(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 80, "Exit", (128, 0, 0), (200, 0, 0))
                            ]
                        else:
                            game.reset(new_state="betting")

        if game.state == "game_over":
            for button in game.buttons:
                if button.is_clicked(event):
                    if button.text == "Reset Game":
                        game.reset_game()
                    elif button.text == "Exit":
                        save_game_state()
                        pygame.quit()
                        return

    game.draw()
    pygame.display.flip()

async def main():
    setup()
    while True:
        await update_loop()
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
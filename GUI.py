import pygame
import sys
from state import GameState, board, REBIRTH, HAPPY, WATER, TRIPLE, DOUBLE, HORUS
from actions import number_of_steps, available_moves, apply_move_lists, handle_rebirth
from ai_wrapper import get_best_move_expectiminimax

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
FPS = 60

# Dynamic board sizing
def calculate_board_dimensions():
    max_board_width = WINDOW_WIDTH - 400
    max_board_height = WINDOW_HEIGHT - 300
    
    cell_size = min(max_board_width // 10, max_board_height // 3) - 8
    cell_margin = 6
    
    board_width = 10 * (cell_size + cell_margin)
    board_height = 3 * (cell_size + cell_margin)
    
    board_x = (WINDOW_WIDTH - board_width) // 2
    board_y = (WINDOW_HEIGHT - board_height) // 2 + 20
    
    return board_x, board_y, cell_size, cell_margin

BOARD_START_X, BOARD_START_Y, CELL_SIZE, CELL_MARGIN = calculate_board_dimensions()

# Enhanced Color Palette
COLORS = {
    'bg_dark': (25, 20, 15),
    'bg_gradient_top': (45, 35, 25),
    'bg_gradient_bottom': (25, 20, 15),
    'sand': (237, 201, 175),
    'sand_dark': (207, 171, 145),
    'wood_dark': (78, 52, 26),
    'wood_light': (139, 90, 43),
    'gold': (255, 215, 0),
    'gold_dark': (184, 134, 11),
    'player1': (231, 76, 60),  # Vibrant red
    'player1_glow': (255, 118, 102),
    'player2': (52, 152, 219),  # Vibrant blue
    'player2_glow': (94, 194, 255),
    'highlight': (46, 204, 113),  # Emerald green
    'highlight_glow': (88, 246, 155),
    'water': (41, 128, 185),
    'water_glow': (93, 173, 226),
    'rebirth': (230, 126, 34),
    'happy': (241, 196, 15),
    'special': (155, 89, 182),
    'text_light': (255, 248, 240),
    'text_dark': (44, 31, 18),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'overlay': (0, 0, 0, 180),
}

# Fonts
try:
    FONT_TITLE = pygame.font.SysFont('papyrus', 72, bold=True)
    FONT_LARGE = pygame.font.SysFont('papyrus', 36, bold=True)
    FONT_MEDIUM = pygame.font.SysFont('papyrus', 28)
    FONT_SMALL = pygame.font.SysFont('papyrus', 20)
    FONT_TINY = pygame.font.SysFont('papyrus', 16)
except:
    FONT_TITLE = pygame.font.Font(None, 72)
    FONT_LARGE = pygame.font.Font(None, 36)
    FONT_MEDIUM = pygame.font.Font(None, 28)
    FONT_SMALL = pygame.font.Font(None, 20)
    FONT_TINY = pygame.font.Font(None, 16)


class AnimatedButton:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_rect = self.rect.copy()
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color or COLORS['white']
        self.hovered = False
        self.animation_progress = 0
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.animation_progress = min(1.0, self.animation_progress + 0.1)
        else:
            self.animation_progress = max(0.0, self.animation_progress - 0.1)
    
    def draw(self, surface, font):
        # Animated scaling
        scale = 1 + (self.animation_progress * 0.05)
        width = int(self.original_rect.width * scale)
        height = int(self.original_rect.height * scale)
        x = self.original_rect.centerx - width // 2
        y = self.original_rect.centery - height // 2
        
        draw_rect = pygame.Rect(x, y, width, height)
        
        # Color interpolation
        current_color = self.interpolate_color(self.color, self.hover_color, self.animation_progress)
        
        # Shadow
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, COLORS['black'], shadow_rect, border_radius=15)
        
        # Button background with gradient effect
        pygame.draw.rect(surface, current_color, draw_rect, border_radius=15)
        
        # Highlight on top
        highlight_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, draw_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 40), highlight_surf.get_rect(), border_radius=15)
        surface.blit(highlight_surf, highlight_rect)
        
        # Border
        pygame.draw.rect(surface, COLORS['gold'], draw_rect, 3, border_radius=15)
        
        # Text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False
    
    @staticmethod
    def interpolate_color(color1, color2, t):
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))


class InputBox:
    def __init__(self, x, y, width, height, default_text='3'):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = COLORS['wood_light']
        self.color_active = COLORS['gold']
        self.color = self.color_inactive
        self.text = default_text
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 2:
                self.text += event.unicode
        return False
    
    def draw(self, surface):
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, COLORS['black'], shadow_rect, border_radius=10)
        
        # Background
        pygame.draw.rect(surface, COLORS['wood_dark'], self.rect, border_radius=10)
        
        # Border
        pygame.draw.rect(surface, self.color, self.rect, 3, border_radius=10)
        
        # Text
        text_surface = FONT_LARGE.render(self.text, True, COLORS['text_light'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Cursor when active
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right + 5
            cursor_y = text_rect.centery
            pygame.draw.line(surface, COLORS['text_light'], 
                           (cursor_x, cursor_y - 15), (cursor_x, cursor_y + 15), 2)
    
    def get_value(self):
        try:
            return max(1, min(10, int(self.text))) if self.text else 3
        except:
            return 3


class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(15):
            angle = pygame.math.Vector2(1, 0).rotate(360 * _ / 15)
            speed = 2 + _ * 0.2
            self.particles.append({
                'pos': [x, y],
                'vel': [angle.x * speed, angle.y * speed],
                'life': 30,
                'color': color
            })
    
    def update(self):
        for p in self.particles:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * (p['life'] / 30))
            color = (*p['color'], alpha)
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (3, 3), 3)
            surface.blit(surf, (int(p['pos'][0]), int(p['pos'][1])))
    
    def is_finished(self):
        return len(self.particles) == 0


class SenetGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🏺 SENET - Ancient Egyptian Board Game 🏺")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = None
        self.human_player = None
        self.computer_player = None
        self.ai_depth = 3
        self.current_roll = None
        self.available_moves_list = []
        self.selected_rock = None
        self.game_over = False
        self.message = "Welcome to Senet!"
        self.thinking = False
        
        # UI state
        self.show_start_screen = True
        self.show_depth_selection = False
        
        # Animations
        self.particles = []
        self.pulse_time = 0
        
        # Input box for difficulty
        input_x = WINDOW_WIDTH // 2 - 100
        input_y = 350
        self.depth_input = InputBox(input_x, input_y, 200, 70)
        
        # Buttons
        self.buttons = []
        
    def create_gradient_background(self, surface):
        """Create a beautiful gradient background"""
        for y in range(WINDOW_HEIGHT):
            progress = y / WINDOW_HEIGHT
            color = tuple(
                int(COLORS['bg_gradient_top'][i] + (COLORS['bg_gradient_bottom'][i] - COLORS['bg_gradient_top'][i]) * progress)
                for i in range(3)
            )
            pygame.draw.line(surface, color, (0, y), (WINDOW_WIDTH, y))
    
    def draw_decorative_border(self, surface):
        """Draw decorative Egyptian-style border"""
        # Outer border
        pygame.draw.rect(surface, COLORS['gold'], (10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), 4, border_radius=20)
        
        # Inner border
        pygame.draw.rect(surface, COLORS['gold_dark'], (15, 15, WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30), 2, border_radius=18)
        
        # Corner decorations
        corner_size = 30
        corners = [
            (20, 20), (WINDOW_WIDTH - 20 - corner_size, 20),
            (20, WINDOW_HEIGHT - 20 - corner_size), 
            (WINDOW_WIDTH - 20 - corner_size, WINDOW_HEIGHT - 20 - corner_size)
        ]
        for x, y in corners:
            pygame.draw.rect(surface, COLORS['gold'], (x, y, corner_size, corner_size), 3)
            pygame.draw.line(surface, COLORS['gold'], (x, y), (x + corner_size, y + corner_size), 2)
            pygame.draw.line(surface, COLORS['gold'], (x + corner_size, y), (x, y + corner_size), 2)
    
    def get_cell_rect(self, index):
        """Get the rectangle for a board cell"""
        if 0 <= index < 10:
            row = 0
            col = index
        elif 10 <= index < 20:
            row = 1
            col = 19 - index
        else:
            row = 2
            col = index - 20
            
        x = BOARD_START_X + col * (CELL_SIZE + CELL_MARGIN)
        y = BOARD_START_Y + row * (CELL_SIZE + CELL_MARGIN)
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    def draw_cell_with_effects(self, surface, rect, cell_type, index):
        """Draw a cell with shadows and highlights"""
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=8)
        surface.blit(shadow_surf, shadow_rect)
        
        # Determine colors
        if cell_type == WATER:
            base_color = COLORS['water']
            glow_color = COLORS['water_glow']
        elif cell_type == REBIRTH:
            base_color = COLORS['rebirth']
            glow_color = COLORS['gold']
        elif cell_type == HAPPY:
            base_color = COLORS['happy']
            glow_color = COLORS['gold_dark']
        elif cell_type in (TRIPLE, DOUBLE, HORUS):
            base_color = COLORS['special']
            glow_color = COLORS['gold']
        elif index % 2 == 0:
            base_color = COLORS['wood_light']
            glow_color = COLORS['sand']
        else:
            base_color = COLORS['wood_dark']
            glow_color = COLORS['sand_dark']
        
        # Main cell
        pygame.draw.rect(surface, base_color, rect, border_radius=8)
        
        # Highlight on top third
        highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 30), highlight_surf.get_rect(), border_radius=8)
        surface.blit(highlight_surf, highlight_rect)
        
        # Border
        pygame.draw.rect(surface, COLORS['gold_dark'], rect, 2, border_radius=8)
        
        # Cell number in corner
        num_text = FONT_TINY.render(str(index), True, COLORS['text_dark'])
        surface.blit(num_text, (rect.x + 4, rect.y + 2))
    
    def draw_board(self):
        """Draw the game board with enhanced visuals"""
        for i in range(30):
            rect = self.get_cell_rect(i)
            self.draw_cell_with_effects(self.screen, rect, board[i], i)
            
            # Draw symbols
            symbol = None
            symbol_color = COLORS['text_dark']
            
            if board[i] == WATER:
                symbol = "~W~"
                symbol_color = COLORS['white']
            elif board[i] == REBIRTH:
                symbol = "R→"
                symbol_color = COLORS['white']
            elif board[i] == HAPPY:
                symbol = "HAP"
                symbol_color = COLORS['wood_dark']
            elif board[i] == TRIPLE:
                symbol = "III"
                symbol_color = COLORS['white']
            elif board[i] == DOUBLE:
                symbol = "II"
                symbol_color = COLORS['white']
            elif board[i] == HORUS:
                symbol = "HR"
                symbol_color = COLORS['white']
                
            if symbol:
                symbol_text = FONT_MEDIUM.render(symbol, True, symbol_color)
                symbol_rect = symbol_text.get_rect(center=rect.center)
                self.screen.blit(symbol_text, symbol_rect)
    
    def draw_piece(self, surface, center, color, glow_color, is_selected=False):
        """Draw a game piece with glow effect"""
        # Animated pulse for selected piece
        if is_selected:
            self.pulse_time += 0.1
            pulse = abs(pygame.math.Vector2(1, 0).rotate(self.pulse_time * 50).x)
            glow_radius = int(35 + pulse * 8)
        else:
            glow_radius = 35
        
        # Glow effect
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for i in range(3):
            alpha = 40 - i * 10
            radius = glow_radius - i * 5
            pygame.draw.circle(glow_surf, (*glow_color, alpha), (glow_radius, glow_radius), radius)
        surface.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))
        
        # Shadow
        shadow_center = (center[0] + 2, center[1] + 3)
        pygame.draw.circle(surface, (0, 0, 0, 100), shadow_center, 28)
        
        # Main piece with gradient
        pygame.draw.circle(surface, color, center, 26)
        
        # Highlight
        highlight_center = (center[0] - 6, center[1] - 6)
        pygame.draw.circle(surface, (255, 255, 255, 150), highlight_center, 8)
        
        # Border
        pygame.draw.circle(surface, COLORS['gold'], center, 26, 3)
        
        # Selection indicator
        if is_selected:
            for i in range(3):
                pygame.draw.circle(surface, COLORS['highlight_glow'], center, 32 + i * 4, 2)
    
    def draw_pieces(self):
        """Draw all game pieces"""
        if not self.state:
            return
        
        # Create temporary surface for pieces to handle overlapping
        piece_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw Player 1 pieces
        for pos in self.state.player_1_rocks_pos:
            rect = self.get_cell_rect(pos)
            center = rect.center
            is_selected = (self.selected_rock == pos)
            self.draw_piece(piece_surface, center, COLORS['player1'], 
                          COLORS['player1_glow'], is_selected)
        
        # Draw Player 2 pieces
        for pos in self.state.player_2_rocks_pos:
            rect = self.get_cell_rect(pos)
            center = rect.center
            is_selected = (self.selected_rock == pos)
            self.draw_piece(piece_surface, center, COLORS['player2'], 
                          COLORS['player2_glow'], is_selected)
        
        self.screen.blit(piece_surface, (0, 0))
    
    def draw_available_moves(self):
        """Highlight available move destinations with animation"""
        if not self.selected_rock or not self.available_moves_list:
            return
        
        pulse = abs(pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.3).x)
        
        for old_pos, new_pos in self.available_moves_list:
            if old_pos == self.selected_rock and new_pos < 30:
                rect = self.get_cell_rect(new_pos)
                
                # Animated glow
                glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
                alpha = int(100 + pulse * 80)
                pygame.draw.rect(glow_surf, (*COLORS['highlight'], alpha), 
                               glow_surf.get_rect(), border_radius=10)
                self.screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
                
                # Pulsing border
                thickness = int(3 + pulse * 3)
                pygame.draw.rect(self.screen, COLORS['highlight_glow'], rect, thickness, border_radius=8)
    
    def draw_dice_panel(self):
        """Draw dice panel with modern design"""
        if self.current_roll is None and not (self.state and self.state.current_player == self.human_player):
            return
        
        panel_x = WINDOW_WIDTH - 210
        panel_y = 10
        panel_width = 200
        panel_height = 280
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*COLORS['wood_dark'], 200), panel_surf.get_rect(), border_radius=20)
        self.screen.blit(panel_surf, panel_rect)
        
        # Border
        pygame.draw.rect(self.screen, COLORS['gold'], panel_rect, 3, border_radius=20)
        
        # Title
        title_text = FONT_MEDIUM.render("DICE", True, COLORS['gold'])
        title_rect = title_text.get_rect(centerx=panel_rect.centerx, y=panel_y + 20)
        self.screen.blit(title_text, title_rect)
        
        if self.current_roll is not None:
            # Roll value
            roll_text = FONT_TITLE.render(str(self.current_roll), True, COLORS['text_light'])
            roll_rect = roll_text.get_rect(centerx=panel_rect.centerx, y=panel_y + 70)
            self.screen.blit(roll_text, roll_rect)
            
            # Stick visualization
            stick_y = panel_y + 160
            for i in range(4):
                stick_x = panel_rect.centerx - 60 + i * 40
                
                if self.current_roll == 5:
                    stick_color = COLORS['sand']
                elif i < self.current_roll:
                    stick_color = COLORS['wood_dark']
                else:
                    stick_color = COLORS['sand']
                
                # Stick shadow
                pygame.draw.rect(self.screen, COLORS['black'], 
                               (stick_x + 2, stick_y + 42, 25, 8), border_radius=2)
                
                # Stick
                pygame.draw.rect(self.screen, stick_color, 
                               (stick_x, stick_y + 40, 25, 8), border_radius=2)
                pygame.draw.rect(self.screen, COLORS['gold_dark'], 
                               (stick_x, stick_y + 40, 25, 8), 1, border_radius=2)
        
        # Roll button (only for human player)
        if self.state and self.state.current_player == self.human_player and self.current_roll is None:
            button_rect = pygame.Rect(panel_rect.centerx - 75, panel_y + 180, 150, 60)
            
            # Check if hovered
            mouse_pos = pygame.mouse.get_pos()
            hovered = button_rect.collidepoint(mouse_pos)
            
            # Button color
            button_color = COLORS['gold'] if hovered else COLORS['gold_dark']
            
            # Shadow
            shadow_rect = button_rect.copy()
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, COLORS['black'], shadow_rect, border_radius=12)
            
            # Button
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=12)
            pygame.draw.rect(self.screen, COLORS['text_light'], button_rect, 3, border_radius=12)
            
            # Text
            button_text = FONT_MEDIUM.render("ROLL", True, COLORS['wood_dark'])
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
    
    def draw_status_panel(self):
        """Draw status panel with player info"""
        panel_x = 10
        panel_y = 10
        panel_width = 200
        panel_height = 280
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*COLORS['wood_dark'], 200), panel_surf.get_rect(), border_radius=20)
        self.screen.blit(panel_surf, panel_rect)
        
        # Border
        pygame.draw.rect(self.screen, COLORS['gold'], panel_rect, 3, border_radius=20)
        
        if self.state and not self.game_over:
            # Current player indicator
            y_offset = panel_y + 30
            
            # Player 1
            p1_color = COLORS['player1'] if self.state.current_player == 1 else COLORS['wood_light']
            pygame.draw.circle(self.screen, p1_color, (panel_x + 40, y_offset), 20)
            pygame.draw.circle(self.screen, COLORS['gold'], (panel_x + 40, y_offset), 20, 2)
            
            p1_text = FONT_SMALL.render(f"Player 1", True, COLORS['text_light'])
            self.screen.blit(p1_text, (panel_x + 70, y_offset - 12))
            
            count1 = len(self.state.player_1_rocks_pos)
            count1_text = FONT_MEDIUM.render(f"× {count1}", True, COLORS['player1'])
            self.screen.blit(count1_text, (panel_x + 70, y_offset + 10))
            
            # Player 2
            y_offset += 80
            p2_color = COLORS['player2'] if self.state.current_player == 2 else COLORS['wood_light']
            pygame.draw.circle(self.screen, p2_color, (panel_x + 40, y_offset), 20)
            pygame.draw.circle(self.screen, COLORS['gold'], (panel_x + 40, y_offset), 20, 2)
            
            p2_text = FONT_SMALL.render(f"Player 2", True, COLORS['text_light'])
            self.screen.blit(p2_text, (panel_x + 70, y_offset - 12))
            
            count2 = len(self.state.player_2_rocks_pos)
            count2_text = FONT_MEDIUM.render(f"× {count2}", True, COLORS['player2'])
            self.screen.blit(count2_text, (panel_x + 70, y_offset + 10))
            
            # Status
            y_offset += 80
            status = "YOU" if self.state.current_player == self.human_player else "AI"
            status_text = FONT_LARGE.render(status, True, COLORS['gold'])
            status_rect = status_text.get_rect(centerx=panel_rect.centerx, y=y_offset)
            self.screen.blit(status_text, status_rect)
    
    def draw_title_and_message(self):
        """Draw title and message"""
        # Title
        title = FONT_TITLE.render("SENET", True, COLORS['gold'])
        title_shadow = FONT_TITLE.render("SENET", True, COLORS['gold_dark'])
        
        title_rect = title.get_rect(centerx=WINDOW_WIDTH // 2, y=40)
        title_shadow_rect = title_shadow.get_rect(centerx=WINDOW_WIDTH // 2 + 3, y=43)
        
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = FONT_SMALL.render("Ancient Egyptian Board Game", True, COLORS['sand'])
        subtitle_rect = subtitle.get_rect(centerx=WINDOW_WIDTH // 2, y=95)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Message bar at bottom
        msg_bg_rect = pygame.Rect(0, WINDOW_HEIGHT - 100, WINDOW_WIDTH, 100)
        msg_surf = pygame.Surface((WINDOW_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(msg_surf, (*COLORS['black'], 150), msg_surf.get_rect())
        self.screen.blit(msg_surf, msg_bg_rect)
        
        msg_text = FONT_MEDIUM.render(self.message, True, COLORS['text_light'])
        msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(msg_text, msg_rect)
    
    def draw_start_screen(self):
        """Enhanced start screen"""
        self.create_gradient_background(self.screen)
        self.draw_decorative_border(self.screen)
        
        # Animated title
        title = FONT_TITLE.render("🏺 SENET 🏺", True, COLORS['gold'])
        title_shadow = FONT_TITLE.render("🏺 SENET 🏺", True, COLORS['black'])
        
        pulse = abs(pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.1).y) * 10
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150 + pulse))
        title_shadow_rect = title_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 4, 154 + pulse))
        
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = FONT_MEDIUM.render("The Ancient Game of Pharaohs", True, COLORS['sand'])
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 230))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Player selection buttons
        mouse_pos = pygame.mouse.get_pos()
        
        button_y = 350
        button_width = 280
        button_height = 80
        
        # Player 1 button
        p1_button = AnimatedButton(
            WINDOW_WIDTH // 2 - button_width - 30, button_y,
            button_width, button_height,
            "Play as RED", COLORS['player1'], COLORS['player1_glow']
        )
        p1_button.update(mouse_pos)
        p1_button.draw(self.screen, FONT_LARGE)
        
        # Player 2 button
        p2_button = AnimatedButton(
            WINDOW_WIDTH // 2 + 30, button_y,
            button_width, button_height,
            "Play as BLUE", COLORS['player2'], COLORS['player2_glow']
        )
        p2_button.update(mouse_pos)
        p2_button.draw(self.screen, FONT_LARGE)
        
        # Store buttons for click detection
        self.buttons = [p1_button, p2_button]
        
        # Instructions
        instructions = [
            "Select your piece to see available moves",
            "Click highlighted squares to move",
            "Bear off all pieces to win!",
        ]
        
        y = 520
        for instruction in instructions:
            text = FONT_SMALL.render(instruction, True, COLORS['sand'])
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 35
    
    def draw_depth_selection(self):
        """Enhanced difficulty selection screen"""
        self.create_gradient_background(self.screen)
        self.draw_decorative_border(self.screen)
        
        # Title
        title = FONT_LARGE.render("Select AI Difficulty", True, COLORS['gold'])
        title_shadow = FONT_LARGE.render("Select AI Difficulty", True, COLORS['black'])
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 180))
        title_shadow_rect = title_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 2, 182))
        
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Instruction
        instruction = FONT_MEDIUM.render("Enter search depth (1-10):", True, COLORS['text_light'])
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 280))
        self.screen.blit(instruction, instruction_rect)
        
        # Input box
        self.depth_input.draw(self.screen)
        
        # Difficulty guide
        guide_y = 460
        guide_texts = [
            ("1-2: Easy", COLORS['player2']),
            ("3-4: Medium", COLORS['happy']),
            ("5+: Hard (may be slow)", COLORS['player1']),
        ]
        
        for text, color in guide_texts:
            guide = FONT_SMALL.render(text, True, color)
            guide_rect = guide.get_rect(center=(WINDOW_WIDTH // 2, guide_y))
            self.screen.blit(guide, guide_rect)
            guide_y += 35
        
        # Start button
        mouse_pos = pygame.mouse.get_pos()
        start_button = AnimatedButton(
            WINDOW_WIDTH // 2 - 125, 600,
            250, 70,
            "START GAME", COLORS['gold'], COLORS['gold_dark'], COLORS['wood_dark']
        )
        start_button.update(mouse_pos)
        start_button.draw(self.screen, FONT_LARGE)
        
        self.buttons = [start_button]
    
    def handle_start_screen_click(self, pos):
        """Handle clicks on start screen"""
        if len(self.buttons) >= 2:
            if self.buttons[0].rect.collidepoint(pos):
                self.human_player = 1
                self.computer_player = 2
                self.show_start_screen = False
                self.show_depth_selection = True
            elif self.buttons[1].rect.collidepoint(pos):
                self.human_player = 2
                self.computer_player = 1
                self.show_start_screen = False
                self.show_depth_selection = True
    
    def handle_depth_selection_click(self, pos):
        """Handle clicks on depth selection screen"""
        if len(self.buttons) >= 1 and self.buttons[0].rect.collidepoint(pos):
            self.ai_depth = self.depth_input.get_value()
            self.show_depth_selection = False
            self.start_game()
    
    def start_game(self):
        """Initialize the game"""
        self.state = GameState(
            player_1_rocks_pos=(1, 3, 5, 7, 9, 11, 13),
            player_2_rocks_pos=(0, 2, 4, 6, 8, 10, 12),
            current_player=self.human_player,
        )
        self.current_roll = None
        self.message = "Click 'ROLL' to begin your turn!"
        self.game_over = False
        
        if self.state.current_player == self.computer_player:
            self.message = "Computer is thinking..."
            self.thinking = True
    
    def roll_dice(self):
        """Roll the dice"""
        self.current_roll = number_of_steps()
        self.available_moves_list = available_moves(self.state, self.current_roll)
        self.selected_rock = None
        
        if not self.available_moves_list:
            self.message = f"Rolled {self.current_roll} - No moves available!"
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        else:
            self.message = f"Rolled {self.current_roll} - Select your piece"
    
    def handle_board_click(self, pos):
        """Handle clicks on the game board"""
        if self.game_over or self.thinking:
            return
        
        if self.state.current_player != self.human_player:
            return
        
        # Check roll button
        if self.current_roll is None:
            panel_x = WINDOW_WIDTH - 210
            panel_y = 10
            # Calculate the center of the panel to position the button correctly
            panel_width = 200
            button_rect = pygame.Rect(panel_x + (panel_width//2) - 75, panel_y + 180, 150, 60)
            if button_rect.collidepoint(pos):
                self.roll_dice()
                return
        
        # Check piece selection
        for rock_pos in (self.state.player_1_rocks_pos if self.state.current_player == 1 
                        else self.state.player_2_rocks_pos):
            rect = self.get_cell_rect(rock_pos)
            if rect.collidepoint(pos):
                self.selected_rock = rock_pos
                self.message = f"Selected piece at position {rock_pos}"
                return
        
        # Check move execution
        if self.selected_rock is not None:
            for old_pos, new_pos in self.available_moves_list:
                if old_pos == self.selected_rock:
                    if new_pos < 30:
                        rect = self.get_cell_rect(new_pos)
                        if rect.collidepoint(pos):
                            self.make_move((old_pos, new_pos))
                            return
                    elif new_pos >= 30:
                        # Bear off - click anywhere in bearing off zone
                        if pos[0] > WINDOW_WIDTH - 300:
                            self.make_move((old_pos, new_pos))
                            return
    
    def make_move(self, move):
        """Execute a move with particle effects"""
        # Create particle effect at destination
        old_pos, new_pos = move
        if new_pos < 30:
            rect = self.get_cell_rect(new_pos)
            color = COLORS['player1'] if self.state.current_player == 1 else COLORS['player2']
            self.particles.append(ParticleEffect(rect.centerx, rect.centery, color))
        
        player_1_rocks_pos, player_1_rocks, player_2_rocks_pos, player_2_rocks, rock_idx = \
            apply_move_lists(self.state, move)
        
        if self.state.current_player == 1:
            player_1_rocks_pos, player_1_rocks = handle_rebirth(
                player_1_rocks_pos, player_1_rocks, player_2_rocks, rock_idx
            )
        else:
            player_2_rocks_pos, player_2_rocks = handle_rebirth(
                player_2_rocks_pos, player_2_rocks, player_1_rocks, rock_idx
            )
        
        self.state = GameState(
            player_1_rocks_pos=tuple(player_1_rocks_pos),
            player_2_rocks_pos=tuple(player_2_rocks_pos),
            current_player=2 if self.state.current_player == 1 else 1,
        )
        
        self.current_roll = None
        self.selected_rock = None
        self.available_moves_list = []
        
        if self.state.is_terminal():
            winner = self.state.winner()
            if winner == self.human_player:
                self.message = "🎉 VICTORY! You have won the game! 🎉"
            else:
                self.message = "💻 Computer wins! Well played!"
            self.game_over = True
        else:
            if self.state.current_player == self.computer_player:
                # Roll the dice immediately when computer's turn starts
                self.current_roll = number_of_steps()
                self.message = f"Computer rolled {self.current_roll}"
                self.thinking = True
                # Start thinking after a short delay to allow user to see the roll
                pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # Increased delay to 1 second
    
    def computer_move(self):
        """Execute computer's move - dice already rolled when turn started"""
        # The dice was already rolled when the turn started, so we just need to process the move
        moves = available_moves(self.state, self.current_roll)

        if not moves:
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        else:
            best_move, nodes, score = get_best_move_expectiminimax(
                self.state, self.current_roll, depth=self.ai_depth, reporting=False
            )

            if best_move:
                self.selected_rock = best_move[0]
                pygame.time.set_timer(pygame.USEREVENT + 3, 800)
                self.pending_computer_move = best_move
            else:
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
    
    def execute_computer_move(self):
        """Execute the computer's pending move"""
        if hasattr(self, 'pending_computer_move'):
            self.make_move(self.pending_computer_move)
            delattr(self, 'pending_computer_move')
            self.thinking = False
            if not self.game_over:
                self.message = "Your turn - Click 'ROLL' to roll dice"
    
    def skip_turn(self):
        """Skip the current turn"""
        self.state = GameState(
            player_1_rocks_pos=self.state.player_1_rocks_pos,
            player_2_rocks_pos=self.state.player_2_rocks_pos,
            current_player=2 if self.state.current_player == 1 else 1,
        )
        self.current_roll = None
        self.selected_rock = None
        self.available_moves_list = []
        
        if self.state.current_player == self.computer_player:
            # Roll the dice immediately when computer's turn starts
            self.current_roll = number_of_steps()
            self.message = f"Computer rolled {self.current_roll}"
            self.thinking = True
            # Start thinking after a short delay to allow user to see the roll
            pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # Increased delay to 1 second
        else:
            self.thinking = False
            self.message = "Your turn - Click 'ROLL' to roll dice"
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_start_screen:
                        self.handle_start_screen_click(event.pos)
                    elif self.show_depth_selection:
                        self.depth_input.handle_event(event)
                        self.handle_depth_selection_click(event.pos)
                    else:
                        self.handle_board_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if self.show_depth_selection:
                        if self.depth_input.handle_event(event):
                            self.ai_depth = self.depth_input.get_value()
                            self.show_depth_selection = False
                            self.start_game()
                
                elif event.type == pygame.USEREVENT + 1:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.skip_turn()
                
                elif event.type == pygame.USEREVENT + 2:
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                    self.computer_move()
                
                elif event.type == pygame.USEREVENT + 3:
                    pygame.time.set_timer(pygame.USEREVENT + 3, 0)
                    self.execute_computer_move()
            
            # Update particles
            for particle in self.particles[:]:
                particle.update()
                if particle.is_finished():
                    self.particles.remove(particle)
            
            # Draw
            if self.show_start_screen:
                self.draw_start_screen()
            elif self.show_depth_selection:
                self.draw_depth_selection()
            else:
                self.create_gradient_background(self.screen)
                self.draw_decorative_border(self.screen)
                self.draw_board()
                self.draw_available_moves()
                self.draw_pieces()
                
                # Draw particles on top
                for particle in self.particles:
                    particle.draw(self.screen)
                
                self.draw_status_panel()
                self.draw_dice_panel()
                self.draw_title_and_message()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SenetGUI()
    game.run()
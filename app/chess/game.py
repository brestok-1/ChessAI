import os

import pygame
from pygame.locals import *

from app.chess.chess import Chess
from app.chess.piece import Queen, Rook, Bishop, Knight
from app.chess.utils import Utils
from app.core.config import settings


class Game:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode([700, 760])  # Увеличена ширина
        pygame.display.set_caption("Chess")
        pygame.display.set_icon(pygame.image.load(settings.BASE_DIR / 'res' / 'chess_icon.png'))
        self.clock, self.menu_showed, self.running = pygame.time.Clock(), False, True

    def start_game(self):
        self.setup_board()
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            if not self.menu_showed:
                self.menu()
            else:
                if self.chess.turn == 'black':
                    self.chess.make_ai_move()
                self.display_game()
            pygame.display.flip()
            pygame.event.pump()
            clock.tick(30)
        pygame.quit()

    def setup_board(self):
        self.board_offset_x, self.board_offset_y = 30, 80
        self.board_img = pygame.image.load(settings.BASE_DIR / 'res' / 'board.png').convert()
        square_len = self.board_img.get_rect().width // 8
        self.board_locations = [[
            [self.board_offset_x + (x * square_len), self.board_offset_y + (y * square_len)]
            for y in range(8)] for x in range(8)]
        self.chess = Chess(self.screen, os.path.join(settings.BASE_DIR / 'res' / 'pieces.png'), self.board_locations, square_len)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.chess.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.menu_showed:
                        self.chess.play_turn(event)
                    else:
                        pass

    def menu(self):
        self.screen.fill((255, 255, 255))
        self.draw_text("Chess", 50, (0, 0, 0), self.screen.get_width() // 2, 150)
        self.draw_button("Play", 270, 300, 100, 50, self.start_game_handler)

    def display_game(self):
        if self.chess.winner:
            self.declare_winner(self.chess.winner)
        elif self.chess.pawn_promotion:
            self.pawn_promotion()
            self.chess.pawn_promotion = None
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.board_img, (self.board_offset_x, self.board_offset_y))
            self.chess.draw_turn_indicator()
            self.chess.draw_pieces()
            self.draw_board_markers()

    def declare_winner(self, winner):
        self.screen.fill((255, 255, 255))
        self.draw_text(f"{winner} wins!", 50, (0, 0, 0), self.screen.get_width() // 2, 150)
        self.draw_button("Play Again", 250, 300, 140, 50, self.reset_game_handler)

    def reset_game_handler(self):
        self.menu_showed = False
        self.chess.reset()

    def draw_button(self, label, x, y, w, h, callback):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        self.draw_text(label, 20, (255, 255, 255), x + w // 2, y + h // 2)
        if Utils().left_click_event() and rect.collidepoint(*Utils().get_mouse_event()):
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 3)
            callback()

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont("comicsansms", size)
        label = font.render(text, True, color)
        self.screen.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))

    def start_game_handler(self):
        self.menu_showed = True

    def pawn_promotion(self):
        self.screen.fill((200, 200, 200))
        self.draw_text("Promote your pawn!", 30, (0, 0, 0), self.screen.get_width() // 2, 150)

        choices = ["queen", "rook", "bishop", "knight"]
        buttons = [
            (pygame.Rect(100 + idx * 120, 300, 100, 50), choice)
            for idx, choice in enumerate(choices)
        ]

        for rect, choice in buttons:
            pygame.draw.rect(self.screen, (0, 0, 0), rect)
            self.draw_text(choice.capitalize(), 20, (255, 255, 255), rect.centerx, rect.centery)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for rect, choice in buttons:
                        if rect.collidepoint(mouse_pos):
                            self.replace_pawn_with_piece(choice)
                            return


    def replace_pawn_with_piece(self, piece_type):
        pawn = self.chess.pawn_promotion
        x, y = pawn.position
        color = pawn.color
        self.chess.board[x][y] = {
            "queen": Queen,
            "rook": Rook,
            "bishop": Bishop,
            "knight": Knight
        }[piece_type](color, [x, y])
        self.chess.pawn_promotion = None
        self.display_game()


    def draw_board_markers(self):
        square_size = self.board_img.get_rect().width // 8
        font = pygame.font.SysFont("comicsansms", 20)
        letters = "ABCDEFGH"
        numbers = "87654321"
        for col in range(8):
            text = font.render(letters[col], True, (255, 255, 255))
            x = self.board_offset_x + col * square_size + square_size // 2 - text.get_width() // 2
            y_top = self.board_offset_y - text.get_height() - 5
            self.screen.blit(text, (x, y_top))
            y_bottom = self.board_offset_y + 8 * square_size + 5
            self.screen.blit(text, (x, y_bottom))

        for row in range(8):
            text = font.render(numbers[row], True, (255, 255, 255))
            y = self.board_offset_y + row * square_size + square_size // 2 - text.get_height() // 2
            x_left = self.board_offset_x - text.get_width() - 5
            self.screen.blit(text, (x_left, y))
            x_right = self.board_offset_x + 8 * square_size + 5
            self.screen.blit(text, (x_right, y))

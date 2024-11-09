import os
import pygame
from pygame.locals import *
from chess import Chess
from utils import Utils


class Game:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode([640, 750])
        pygame.display.set_caption("Chess")
        pygame.display.set_icon(pygame.image.load(os.path.join("res", "chess_icon.png")))
        self.clock, self.menu_showed, self.running = pygame.time.Clock(), False, True

    def start_game(self):
        self.setup_board()
        while self.running:
            self.handle_events()
            if not self.menu_showed:
                self.menu()
            else:
                self.display_game()
            pygame.display.flip()
            pygame.event.pump()
        pygame.quit()

    def setup_board(self):
        self.board_offset_x, self.board_offset_y = 0, 50
        self.board_img = pygame.image.load(os.path.join("res", "board.png")).convert()
        square_len = self.board_img.get_rect().width // 8
        self.board_locations = [[
            [self.board_offset_x + (x * square_len), self.board_offset_y + (y * square_len)]
            for y in range(8)] for x in range(8)]
        self.chess = Chess(self.screen, os.path.join("res", "pieces.png"), self.board_locations, square_len)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[K_ESCAPE]:
                self.running = False
            elif pygame.key.get_pressed()[K_SPACE]:
                self.chess.reset()

    def menu(self):
        self.screen.fill((255, 255, 255))
        self.draw_text("Chess", 50, (0, 0, 0), self.screen.get_width() // 2, 150)
        self.draw_button("Play", 270, 300, 100, 50, self.start_game_handler)

    def display_game(self):
        if self.chess.winner:
            self.declare_winner(self.chess.winner)
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.board_img, (self.board_offset_x, self.board_offset_y))
            self.chess.play_turn()
            self.chess.draw_pieces()
            self.check_pawn_promotion()

    def declare_winner(self, winner):
        self.screen.fill((255, 255, 255))
        self.draw_text(f"{winner} wins!", 50, (0, 0, 0), self.screen.get_width() // 2, 150)
        self.draw_button("Play Again", 250, 300, 140, 50, self.reset_game_handler)

    def reset_game_handler(self):
        self.menu_showed = False
        self.chess.reset()
        self.chess.winner = ""

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

    def check_pawn_promotion(self):
        for file, ranks in self.chess.piece_location.items():
            for rank, piece_info in ranks.items():
                piece_name, _, (x, y) = piece_info
                if piece_name == "white_pawn" and y == 0:
                    self.pawn_promotion(file, rank, "white")
                elif piece_name == "black_pawn" and y == 7:
                    self.pawn_promotion(file, rank, "black")

    def pawn_promotion(self, file, rank, color):
        self.screen.fill((200, 200, 200))
        self.draw_text("Promote your pawn!", 30, (0, 0, 0), self.screen.get_width() // 2, 150)
        choices = ["queen", "rook", "bishop", "knight"]
        x_offset = 100
        for idx, choice in enumerate(choices):
            self.draw_button(
                choice.capitalize(), x_offset + idx * 120, 300, 100, 50,
                lambda ch=choice: self.promote_pawn(file, rank, f"{color}_{ch}")
            )

    def promote_pawn(self, file, rank, new_piece):
        self.chess.piece_location[file][rank][0] = new_piece
        self.display_game()

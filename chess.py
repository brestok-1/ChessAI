import pygame

from piece import Knight, Rook, King, Bishop, Queen, Pawn
from spritesheets import PieceSprites
from utils import Utils


class Chess:
    def __init__(self, screen, pieces_src, square_coords, square_length):
        self.screen = screen
        self.square_coords = square_coords
        self.square_length = square_length
        self.turn = 'white'
        self.utils = Utils()
        self.piece_sprites = PieceSprites(pieces_src, cols=6, rows=2)
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None
        self.moves = []
        self.winner = None
        self.reset()

    def reset(self):
        self.turn = 'white'
        self.selected_piece = None
        self.moves = []
        self.winner = None
        self.initialize_board()
        self.piece_location = {chr(i): {a: ["", False, [x, 8 - a]] for a in range(1, 9)} for x, i in
                               enumerate(range(97, 105))}

    def initialize_board(self):
        # Place white pieces
        for x in range(8):
            self.board[x][6] = Pawn('white', [x, 6])
        self.board[0][7] = Rook('white', [0, 7])
        self.board[1][7] = Knight('white', [1, 7])
        self.board[2][7] = Bishop('white', [2, 7])
        self.board[3][7] = Queen('white', [3, 7])
        self.board[4][7] = King('white', [4, 7])
        self.board[5][7] = Bishop('white', [5, 7])
        self.board[6][7] = Knight('white', [6, 7])
        self.board[7][7] = Rook('white', [7, 7])

        # Place black pieces
        for x in range(8):
            self.board[x][1] = Pawn('black', [x, 1])
        self.board[0][0] = Rook('black', [0, 0])
        self.board[1][0] = Knight('black', [1, 0])
        self.board[2][0] = Bishop('black', [2, 0])
        self.board[3][0] = Queen('black', [3, 0])
        self.board[4][0] = King('black', [4, 0])
        self.board[5][0] = Bishop('black', [5, 0])
        self.board[6][0] = Knight('black', [6, 0])
        self.board[7][0] = Rook('black', [7, 0])

    def play_turn(self):
        self.draw_turn_indicator()
        if self.utils.left_click_event():
            x, y = self.get_board_coords(self.utils.get_mouse_event())
            if x is not None and y is not None:
                self.handle_click(x, y)

    def handle_click(self, x, y):
        piece = self.get_piece_at(x, y)
        if piece and piece.color == self.turn:
            self.selected_piece = piece
            self.moves = piece.possible_moves(self)
        elif self.selected_piece and [x, y] in self.moves:
            self.move_piece(self.selected_piece, x, y)
            self.end_turn()
        else:
            self.selected_piece = None
            self.moves = []

    def move_piece(self, piece, x, y):
        self.board[piece.position[0]][piece.position[1]] = None
        captured_piece = self.get_piece_at(x, y)
        if captured_piece:
            if isinstance(captured_piece, King):
                self.winner = piece.color
        piece.move([x, y])
        self.board[x][y] = piece

    def end_turn(self):
        self.turn = 'black' if self.turn == 'white' else 'white'
        self.selected_piece = None
        self.moves = []
        if self.is_king_in_checkmate(self.turn):
            self.winner = 'white' if self.turn == 'black' else 'black'

    def draw_pieces(self):
        if self.selected_piece:
            for move in self.moves:
                coords = self.square_coords[move[0]][move[1]]
                pygame.draw.rect(self.screen, (0, 255, 0),
                                 (coords[0], coords[1], self.square_length, self.square_length), 3)

        for x in range(8):
            for y in range(8):
                piece = self.get_piece_at(x, y)
                if piece:
                    coords = self.square_coords[x][y]
                    self.piece_sprites.draw(self.screen, piece, coords)

    def draw_turn_indicator(self):
        font = pygame.font.SysFont("comicsansms", 20)
        turn_text = font.render(f"Turn: {self.turn.capitalize()}", True, (255, 255, 255))
        self.screen.blit(turn_text, ((self.screen.get_width() - turn_text.get_width()) // 2, 10))

    def get_piece_at(self, x, y):
        if 0 <= x < 8 and 0 <= y < 8:
            return self.board[x][y]
        return None

    def is_empty(self, x, y):
        return self.get_piece_at(x, y) is None

    def is_enemy_piece(self, color, x, y):
        piece = self.get_piece_at(x, y)
        return piece and piece.color != color

    def filter_valid_moves(self, piece, moves):
        valid_moves = []
        for x, y in moves:
            if 0 <= x < 8 and 0 <= y < 8:
                target_piece = self.get_piece_at(x, y)
                if not target_piece or target_piece.color != piece.color:
                    valid_moves.append([x, y])
        return valid_moves

    def get_straight_moves(self, piece):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.get_moves_in_directions(piece, directions)

    def get_diagonal_moves(self, piece):
        directions = [[-1, -1], [1, 1], [-1, 1], [1, -1]]
        return self.get_moves_in_directions(piece, directions)

    def get_moves_in_directions(self, piece, directions):
        moves = []
        x, y = piece.position
        for dx, dy in directions:
            nx, ny = x, y
            while True:
                nx += dx
                ny += dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target_piece = self.get_piece_at(nx, ny)
                    if not target_piece:
                        moves.append([nx, ny])
                    elif target_piece.color != piece.color:
                        moves.append([nx, ny])
                        break
                    else:
                        break
                else:
                    break
        return moves

    def is_king_in_check(self, color):
        king = self.find_king(color)
        return self.is_position_attacked(king.position, color)

    def is_king_in_checkmate(self, color):
        if not self.is_king_in_check(color):
            return False
        king = self.find_king(color)
        moves = king.possible_moves(self)
        for move in moves:
            if not self.is_position_attacked(move, color):
                return False
        return True

    def is_position_attacked(self, position, color):
        opponent_color = 'black' if color == 'white' else 'white'
        for x in range(8):
            for y in range(8):
                piece = self.get_piece_at(x, y)
                if piece and piece.color == opponent_color:
                    if position in piece.possible_moves(self, is_attacking=True):
                        return True
        return False

    def find_king(self, color):
        for x in range(8):
            for y in range(8):
                piece = self.get_piece_at(x, y)
                if isinstance(piece, King) and piece.color == color:
                    return piece
        return None

    def can_castle(self, color, side):
        king = self.find_king(color)
        if king.has_moved:
            return False

        if side == 'king':
            rook = self.get_piece_at(7, king.position[1])
        else:
            rook = self.get_piece_at(0, king.position[1])

        if not isinstance(rook, Rook) or rook.color != color or rook.has_moved:
            return False

        # Проверяем, что клетки между королем и ладьей пусты
        start = min(king.position[0], rook.position[0]) + 1
        end = max(king.position[0], rook.position[0])
        for x in range(start, end):
            if not self.is_empty(x, king.position[1]):
                return False
            # Дополнительно можно проверить, что эти клетки не находятся под атакой

        return True

    def get_board_coords(self, mouse_pos):
        for x in range(8):
            for y in range(8):
                rect = pygame.Rect(self.square_coords[x][y][0], self.square_coords[x][y][1],
                                   self.square_length, self.square_length)
                if rect.collidepoint(mouse_pos):
                    return x, y
        return None, None

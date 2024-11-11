import pygame

from piece import Knight, Rook, King, Bishop, Queen, Pawn, ChessPiece
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
        self.board: list = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None
        self.moves = []
        self.winner = None
        self.reset()
        self.pawn_promotion = None

    def reset(self):
        self.turn = 'white'
        self.selected_piece = None
        self.moves = []
        self.winner = None
        self.board: list = [[None for _ in range(8)] for _ in range(8)]
        self.initialize_board()

    def initialize_board(self):
        for x in range(8):
            self.board[x][6] = Pawn('white', [x, 6])
            self.board[x][1] = Pawn('black', [x, 1])

        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for x, piece_class in enumerate(back_row):
            self.board[x][7] = piece_class('white', [x, 7])
            self.board[x][0] = piece_class('black', [x, 0])

    def play_turn(self):
        self.draw_turn_indicator()
        if self.utils.left_click_event():
            x, y = self.get_board_coords(self.utils.get_mouse_event())
            if x is not None and y is not None:
                self.handle_click(x, y)

    def handle_click(self, x: int, y: int):
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

    def move_piece(self, piece: ChessPiece, x: int, y: int):
        self.board[piece.position[0]][piece.position[1]] = None
        captured_piece = self.get_piece_at(x, y)
        if captured_piece:
            if isinstance(captured_piece, King):
                self.winner = piece.color

        if isinstance(piece, Pawn):
            if (piece.color == 'white' and y == 0) or (piece.color == 'black' and y == 7):
                self.pawn_promotion = piece

        if isinstance(piece, King):
            if abs(piece.position[0] - x) == 2:
                self.perform_castle(piece, x)
        piece.move([x, y])
        self.board[x][y] = piece

    def end_turn(self):
        self.turn = 'black' if self.turn == 'white' else 'white'
        self.selected_piece = None
        self.moves = []
        if winner:=self.is_king_in_checkmate(self.turn):
            self.winner = winner

    def draw_pieces(self):
        colors = {
            "black": (0, 194, 39, 170),
            "white": (28, 21, 212, 170)
        }
        surfaces = {
            "black": pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA),
            "white": pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        }
        for key in surfaces:
            surfaces[key].fill(colors[key])
        if self.selected_piece:
            for move in self.moves:
                coords = self.square_coords[move[0]][move[1]]
                color_key = self.selected_piece.color
                self.screen.blit(surfaces[color_key], (coords[0], coords[1]))
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

    def get_piece_at(self, x: int, y: int) -> ChessPiece | None:
        if 0 <= x < 8 and 0 <= y < 8:
            return self.board[x][y]
        return None

    def is_empty(self, x: int, y: int):
        return self.get_piece_at(x, y) is None

    def is_enemy_piece(self, color: str, x: int, y: int):
        piece = self.get_piece_at(x, y)
        return piece and piece.color != color

    def filter_valid_moves(self, piece: ChessPiece, moves: list):
        valid_moves = []
        for x, y in moves:
            if 0 <= x < 8 and 0 <= y < 8:
                target_piece = self.get_piece_at(x, y)
                if not target_piece or target_piece.color != piece.color:
                    valid_moves.append([x, y])
        return valid_moves

    def get_straight_moves(self, piece: ChessPiece):
        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        return self.get_moves_in_directions(piece, directions)

    def get_diagonal_moves(self, piece: ChessPiece):
        directions = [[-1, -1], [1, 1], [-1, 1], [1, -1]]
        return self.get_moves_in_directions(piece, directions)

    def get_moves_in_directions(self, piece: ChessPiece, directions: list[list[int]]) -> list[list]:
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

    def is_king_in_checkmate(self, color: str) -> str | None:
        white_king, black_king = self.find_king('white'), self.find_king('black')
        if not white_king:
            return 'black'
        if not black_king:
            return 'white'
        if self.is_position_attacked(white_king.position, white_king.color) and color == 'black':
            return 'black'
        if self.is_position_attacked(black_king.position, black_king.color) and color == 'white':
            return 'white'
        return None

    def is_position_attacked(self, position: list[int, int], color: str):
        opponent_color = 'black' if color == 'white' else 'white'
        for x in range(8):
            for y in range(8):
                piece = self.get_piece_at(x, y)
                if piece and piece.color == opponent_color:
                    if position in piece.possible_moves(self, is_attacking=True):
                        return True
        return False

    def find_king(self, color: str) -> King | None:
        for x in range(8):
            for y in range(8):
                piece = self.get_piece_at(x, y)
                if isinstance(piece, King) and piece.color == color:
                    return piece
        return None

    def can_castle(self, color: str, side: str) -> bool:
        king = self.find_king(color)
        if king.has_moved:
            return False

        if side == 'king':
            rook = self.get_piece_at(7, king.position[1])
        else:
            rook = self.get_piece_at(0, king.position[1])

        if not isinstance(rook, Rook) or rook.color != color or rook.has_moved:
            return False

        start = min(king.position[0], rook.position[0]) + 1
        end = max(king.position[0], rook.position[0])
        for x in range(start, end):
            if not self.is_empty(x, king.position[1]):
                return False
        return True

    def perform_castle(self, piece: ChessPiece, x: int):
        if x == 6:  # King-side castling
            rook = self.get_piece_at(7, piece.position[1])
            self.board[7][piece.position[1]] = None
            self.board[5][piece.position[1]] = rook
            rook.move([5, piece.position[1]])
        elif x == 2:  # Queen-side castling
            rook = self.get_piece_at(0, piece.position[1])
            self.board[0][piece.position[1]] = None
            self.board[3][piece.position[1]] = rook
            rook.move([3, piece.position[1]])

    def get_board_coords(self, mouse_pos: list) -> tuple[int | None, int | None]:
        for x in range(8):
            for y in range(8):
                rect = pygame.Rect(self.square_coords[x][y][0], self.square_coords[x][y][1],
                                   self.square_length, self.square_length)
                if rect.collidepoint(mouse_pos):
                    return x, y
        return None, None

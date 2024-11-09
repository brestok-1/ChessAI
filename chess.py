import pygame

from piece import Piece
from utils import Utils


class Chess:
    def __init__(self, screen, pieces_src, square_coords, square_length):
        self.screen = screen
        self.chess_pieces = Piece(pieces_src, cols=6, rows=2)
        self.board_locations = square_coords
        self.square_length = square_length
        self.turn = {"black": 0, "white": 0}
        self.moves = []
        self.utils = Utils()
        self.pieces = {
            "white_pawn": 5, "white_knight": 3, "white_bishop": 2,
            "white_rook": 4, "white_king": 0, "white_queen": 1,
            "black_pawn": 11, "black_knight": 9, "black_bishop": 8,
            "black_rook": 10, "black_king": 6, "black_queen": 7
        }
        self.captured = []
        self.winner = ""
        self.reset()

    def reset(self):
        self.moves = []
        self.turn["white"], self.turn["black"] = 1, 0
        self.king_moved = {"white": False, "black": False}
        self.rook_moved = {"white_king_side": False, "white_queen_side": False,
                           "black_king_side": False, "black_queen_side": False}
        self.piece_location = {chr(i): {a: ["", False, [x, 8 - a]] for a in range(1, 9)} for x, i in
                               enumerate(range(97, 105))}
        self._initialize_board()

    def _initialize_board(self):
        for file, rank in self.piece_location.items():
            for row in range(1, 9):
                if row == 1:
                    rank[row][0] = {"a": "white_rook", "h": "white_rook", "b": "white_knight", "g": "white_knight",
                                    "c": "white_bishop", "f": "white_bishop", "d": "white_queen",
                                    "e": "white_king"}.get(file, "")
                elif row == 2:
                    rank[row][0] = "white_pawn"
                elif row == 7:
                    rank[row][0] = "black_pawn"
                elif row == 8:
                    rank[row][0] = {"a": "black_rook", "h": "black_rook", "b": "black_knight", "g": "black_knight",
                                    "c": "black_bishop", "f": "black_bishop", "d": "black_queen",
                                    "e": "black_king"}.get(file, "")

    def play_turn(self):
        white_color = (255, 255, 255)
        small_font = pygame.font.SysFont("comicsansms", 20)
        turn_text = small_font.render(f"Turn: {'Black' if self.turn['black'] else 'White'}", True, white_color)
        self.screen.blit(turn_text, ((self.screen.get_width() - turn_text.get_width()) // 2, 10))
        self.move_piece("black" if self.turn["black"] else "white")

    def draw_pieces(self):
        colors = {
            "black": (0, 194, 39, 170),
            "white": (28, 21, 212, 170)
        }

        surfaces = {
            "black": pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA),
            "white": pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        }
        for color, surface in surfaces.items():
            surface.fill(colors[color])

        for val in self.piece_location.values():
            for value in val.values():
                piece_name, is_selected, (piece_x, piece_y) = value
                if is_selected and piece_name.startswith(("black", "white")):
                    color = "black" if piece_name.startswith("black") else "white"
                    self.screen.blit(surfaces[color], self.board_locations[piece_x][piece_y])
                    for move in self.moves:
                        if all(0 <= coord < 8 for coord in move):
                            self.screen.blit(surfaces[color], self.board_locations[move[0]][move[1]])

        for val in self.piece_location.values():
            for value in val.values():
                piece_name, _, (piece_x, piece_y) = value
                if piece_name:
                    self.chess_pieces.draw(self.screen, piece_name, self.board_locations[piece_x][piece_y])

    def possible_moves(self, piece_name, piece_coord, check_castling=True):
        positions = []
        if not piece_name:
            return positions

        x_coord, y_coord = piece_coord

        piece_color = piece_name.split('_')[0]

        if piece_name.endswith("bishop"):
            positions = self.diagonal_moves(positions, piece_name, piece_coord)

        elif piece_name.endswith("pawn"):
            positions = self._pawn_moves(piece_name, x_coord, y_coord)

        elif piece_name.endswith("rook"):
            positions = self.linear_moves(positions, piece_name, piece_coord)

        elif piece_name.endswith("knight"):
            knight_moves = [
                (x_coord - 2, y_coord - 1), (x_coord - 2, y_coord + 1),
                (x_coord + 2, y_coord - 1), (x_coord + 2, y_coord + 1),
                (x_coord - 1, y_coord - 2), (x_coord - 1, y_coord + 2),
                (x_coord + 1, y_coord - 2), (x_coord + 1, y_coord + 2)
            ]
            positions.extend([[x, y] for x, y in knight_moves if 0 <= x < 8 and 0 <= y < 8])

        elif piece_name.endswith("king"):
            king_moves = [
                (x_coord, y_coord - 1), (x_coord, y_coord + 1),
                (x_coord - 1, y_coord), (x_coord + 1, y_coord),
                (x_coord - 1, y_coord - 1), (x_coord - 1, y_coord + 1),
                (x_coord + 1, y_coord - 1), (x_coord + 1, y_coord + 1)
            ]
            positions.extend([[x, y] for x, y in king_moves if 0 <= x < 8 and 0 <= y < 8])

            # Castling moves
            if check_castling and not self.king_moved[piece_color] and not self.is_king_in_check(piece_color):
                # King side castling
                if not self.rook_moved[f"{piece_color}_king_side"]:
                    if self.is_path_clear_for_castling(x_coord, y_coord, 1, piece_color):
                        positions.append([x_coord + 2, y_coord])

                # Queen side castling
                if not self.rook_moved[f"{piece_color}_queen_side"]:
                    if self.is_path_clear_for_castling(x_coord, y_coord, -1, piece_color):
                        positions.append([x_coord - 2, y_coord])

        elif piece_name.endswith("queen"):
            positions = self.diagonal_moves(positions, piece_name, piece_coord)
            positions = self.linear_moves(positions, piece_name, piece_coord)

        return self._filter_positions(piece_name, positions)

    def _pawn_moves(self, piece_name, x_coord, y_coord):
        positions = []
        column_char = chr(97 + x_coord)
        row_no = 8 - y_coord
        direction = 1 if piece_name == "black_pawn" else -1
        start_row = 1 if piece_name == "black_pawn" else 6

        if 0 <= y_coord + direction < 8:
            row_no -= direction
            front_piece = self.piece_location[column_char][row_no][0]
            if not front_piece:
                positions.append([x_coord, y_coord + direction])
                if y_coord == start_row:
                    row_no -= direction
                    front_piece = self.piece_location[column_char][row_no][0]
                    if not front_piece:
                        positions.append([x_coord, y_coord + 2 * direction])

        for dx in [-1, 1]:
            nx, ny = x_coord + dx, y_coord + direction
            if 0 <= nx < 8 and 0 <= ny < 8:
                column_char = chr(97 + nx)
                row_no = 8 - ny
                to_capture = self.piece_location[column_char][row_no]
                if to_capture[0].startswith("white" if piece_name == "black_pawn" else "black"):
                    positions.append([nx, ny])

        return positions

    def _filter_positions(self, piece_name, positions):
        to_remove = []
        for x, y in positions:
            column_char = chr(97 + x)
            row_no = 8 - y
            des_piece_name = self.piece_location[column_char][row_no][0]
            if des_piece_name.startswith(piece_name[:5]):
                to_remove.append([x, y])
        return [pos for pos in positions if pos not in to_remove]

    def move_piece(self, turn):
        square = self.get_selected_square()
        if not square:
            return

        piece_name, column_char, row_no = square
        piece_color = piece_name[:5]
        x, y = self.piece_location[column_char][row_no][2]

        if piece_name and piece_color == turn:
            self.moves = self.possible_moves(piece_name, [x, y])
            for k, v in self.piece_location.items():
                for key in v:
                    v[key][1] = False
            self.piece_location[column_char][row_no][1] = True

        for move in self.moves:
            if move == [x, y]:
                if not self.piece_location[column_char][row_no][0] or piece_color == turn:
                    self.validate_move([x, y])
                else:
                    self.capture_piece([column_char, row_no], [x, y])

    def get_selected_square(self):
        if self.utils.left_click_event():
            mouse_event = self.utils.get_mouse_event()
            for i, row in enumerate(self.board_locations):
                for j, loc in enumerate(row):
                    rect = pygame.Rect(loc[0], loc[1], self.square_length, self.square_length)
                    if rect.collidepoint(mouse_event):
                        selected = [rect.x, rect.y]
                        for k, board_row in enumerate(self.board_locations):
                            try:
                                l = board_row.index(selected)
                                for val in self.piece_location.values():
                                    for piece in val.values():
                                        if not piece[1]:
                                            piece[1] = False
                                column_char, row_no = chr(97 + k), 8 - l
                                piece_name = self.piece_location[column_char][row_no][0]
                                return [piece_name, column_char, row_no]
                            except ValueError:
                                pass
        return None

    def validate_move(self, destination):
        des_col = chr(97 + destination[0])
        des_row = 8 - destination[1]

        for col, rows in self.piece_location.items():
            for row, board_piece in rows.items():
                if board_piece[1]:
                    board_piece[1] = False
                    piece_name = board_piece[0]
                    piece_color = piece_name.split('_')[0]
                    self.piece_location[des_col][des_row][0] = piece_name
                    self.piece_location[col][row][0] = ""

                    # Handle castling
                    if piece_name.endswith("king"):
                        self.king_moved[piece_color] = True
                        if abs(destination[0] - (ord(col) - 97)) == 2:
                            # This is castling
                            if destination[0] - (ord(col) - 97) == 2:
                                # King side castling
                                rook_start_col = 'h'
                                rook_end_col = chr(97 + destination[0] - 1)
                                self.rook_moved[f"{piece_color}_king_side"] = True
                            else:
                                # Queen side castling
                                rook_start_col = 'a'
                                rook_end_col = chr(97 + destination[0] + 1)
                                self.rook_moved[f"{piece_color}_queen_side"] = True
                            rook_row = des_row
                            rook_piece = self.piece_location[rook_start_col][rook_row][0]
                            self.piece_location[rook_start_col][rook_row][0] = ""
                            self.piece_location[rook_end_col][rook_row][0] = rook_piece
                    elif piece_name.endswith("rook"):
                        # Mark the rook as moved
                        if col == 'a':
                            self.rook_moved[f"{piece_color}_queen_side"] = True
                        elif col == 'h':
                            self.rook_moved[f"{piece_color}_king_side"] = True

                    self.turn["black"], self.turn["white"] = int(not self.turn["black"]), int(not self.turn["white"])
                    src_location = f"{col}{row}"
                    des_location = f"{des_col}{des_row}"
                    print(f"{piece_name} moved from {src_location} to {des_location}")

                    # Check for check after move
                    opponent_color = 'white' if piece_color == 'black' else 'black'
                    if self.is_king_in_check(opponent_color):
                        if self.is_king_in_checkmate(opponent_color):
                            print(f"{opponent_color.capitalize()} is in checkmate. {piece_color.capitalize()} wins!")
                            self.winner = piece_color.capitalize()
                        else:
                            print(f"{opponent_color.capitalize()} is in check!")
                    return

    def diagonal_moves(self, positions, piece_name, piece_coord):
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dx, dy in directions:
            x, y = piece_coord
            while True:
                x += dx
                y += dy
                if not (0 <= x <= 7 and 0 <= y <= 7):
                    break
                positions.append([x, y])
                column_char = chr(97 + x)
                row_no = 8 - y
                p = self.piece_location[column_char][row_no]
                if p[0]:
                    break
        return positions

    def linear_moves(self, positions, piece_name, piece_coord):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            x, y = piece_coord
            while 0 <= x + dx < 8 and 0 <= y + dy < 8:
                x += dx
                y += dy
                positions.append([x, y])
                column_char = chr(97 + x)
                row_no = 8 - y
                p = self.piece_location[column_char][row_no]
                if p[0]:
                    break
        return positions

    def is_path_clear_for_castling(self, king_x, king_y, direction, piece_color):
        # direction = 1 for king side (right), -1 for queen side (left)
        if direction == 1:
            x_range = range(king_x + 1, 7)
        else:
            x_range = range(1, king_x)

        # Check if squares between king and rook are empty
        for x in x_range:
            if self.is_square_occupied(x, king_y):
                return False

        # Check if squares the king passes over are not under attack
        if direction == 1:
            squares_to_check = [[king_x + 1, king_y], [king_x + 2, king_y]]
        else:
            squares_to_check = [[king_x - 1, king_y], [king_x - 2, king_y]]

        for square in squares_to_check:
            if self.is_position_attacked(square, piece_color):
                return False

        return True

    def is_square_occupied(self, x, y):
        col_char = chr(97 + x)
        row_no = 8 - y
        piece_name = self.piece_location[col_char][row_no][0]
        return bool(piece_name)

    def capture_piece(self, chess_board_coord, piece_coord):
        column_char, row_no = chess_board_coord
        p = self.piece_location[column_char][row_no]

        if p[0] == "white_king" and self.is_king_in_check('white'):
            self.winner = "Black"
            print("Black wins")
        elif p[0] == "black_king" and self.is_king_in_check('black'):
            self.winner = "White"
            print("White wins")

        self.captured.append(p)
        self.validate_move(piece_coord)

    def is_king_in_check(self, color):
        king_position = self.find_king(color)
        return self.is_position_attacked(king_position, color)

    def is_king_in_checkmate(self, king_color):
        if not self.is_king_in_check(king_color):
            return False
        king_position = self.find_king(king_color)
        possible_moves = self.possible_moves(f"{king_color}_king", king_position)

        for move in possible_moves:
            if not self.is_position_attacked(move, king_color):
                return False

        return True

    def find_king(self, king_color):
        king_name = f"{king_color}_king"
        for col, rows in self.piece_location.items():
            for row, piece in rows.items():
                if piece[0] == king_name:
                    return [ord(col) - 97, 8 - row]

    def is_position_attacked(self, position, king_color):
        opponent_color = "black" if king_color == "white" else "white"
        for col, rows in self.piece_location.items():
            for row, piece in rows.items():
                if piece[0].startswith(opponent_color):
                    piece_moves = self.possible_moves(piece[0], [ord(col) - 97, 8 - row], check_castling=False)
                    if position in piece_moves:
                        return True
        return False

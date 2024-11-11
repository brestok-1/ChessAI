class ChessPiece:
    def __init__(self, color, position):
        self.color = color  # 'white' or 'black'
        self.position = position  # [x, y]
        self.has_moved = False

    def possible_moves(self, board, is_attacking=False):
        raise NotImplementedError("This method should be overridden in subclasses")

    def move(self, destination):
        self.position = destination
        self.has_moved = True

    def __str__(self):
        return self.__class__.__name__

class King(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        x, y = self.position
        moves = [
            [x, y - 1], [x, y + 1],
            [x - 1, y], [x + 1, y],
            [x - 1, y - 1], [x - 1, y + 1],
            [x + 1, y - 1], [x + 1, y + 1]
        ]

        if not is_attacking:
            if not self.has_moved and not board.is_position_attacked(self.position, self.color):
                if board.can_castle(self.color, 'king'):
                    moves.append([x + 2, y])
                if board.can_castle(self.color, 'queen'):
                    moves.append([x - 2, y])

        return board.filter_valid_moves(self, moves)


class Queen(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        return board.get_straight_moves(self) + board.get_diagonal_moves(self)


class Rook(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        return board.get_straight_moves(self)


class Bishop(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        return board.get_diagonal_moves(self)


class Knight(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        x, y = self.position
        moves = [
            [x - 2, y - 1], [x - 2, y + 1],
            [x + 2, y - 1], [x + 2, y + 1],
            [x - 1, y - 2], [x - 1, y + 2],
            [x + 1, y - 2], [x + 1, y + 2]
        ]
        return board.filter_valid_moves(self, moves)


class Pawn(ChessPiece):
    def possible_moves(self, board, is_attacking=False):
        x, y = self.position
        moves = []
        direction = 1 if self.color == 'black' else -1
        start_row = 1 if self.color == 'black' else 6

        if board.is_empty(x, y + direction):
            moves.append([x, y + direction])
            if y == start_row and board.is_empty(x, y + 2 * direction):
                moves.append([x, y + 2 * direction])

        for dx in [-1, 1]:
            nx, ny = x + dx, y + direction
            if board.is_enemy_piece(self.color, nx, ny):
                moves.append([nx, ny])

        return board.filter_valid_moves(self, moves)

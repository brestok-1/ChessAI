import numpy as np
from chess import Board

from app.chess.piece import ChessPiece

def board_to_matrix(chess):
    matrix = np.zeros((13, 8, 8))
    for x in range(8):
        for y in range(8):
            piece: ChessPiece = chess.board[x][y]
            if piece is not None:
                piece_color = 0 if piece.color == 'white' else 6
                piece_type = piece.piece_type
                row = 7 - y
                matrix[piece_type + piece_color, row, x] = 1

    legal_moves = chess.get_legal_moves()
    for (_, _), (to_x, to_y) in legal_moves:
        row_to = 7 - to_y
        matrix[12, row_to, to_x] = 1
    return matrix


def board_to_matrix_original(board: Board) -> np.ndarray:
    # 8x8 is a size of the chess board.
    # 12 = number of unique pieces.
    # 13th board for legal moves (WHERE we can move)
    matrix = np.zeros((13, 8, 8))
    piece_map = board.piece_map()

    # Populate first 12 8x8 boards (where pieces are)
    for square, piece in piece_map.items():
        row, col = divmod(square, 8)
        piece_type = piece.piece_type - 1
        piece_color = 0 if piece.color else 6
        matrix[piece_type + piece_color, row, col] = 1

    # Populate the legal moves board (13th 8x8 board)
    legal_moves = board.legal_moves
    for move in legal_moves:
        to_square = move.to_square
        row_to, col_to = divmod(to_square, 8)
        matrix[12, row_to, col_to] = 1

    return matrix

if __name__ == "__main__":
    board_ = Board()
    t = board_to_matrix(board_)
    print(t)
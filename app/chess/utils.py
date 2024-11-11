import pygame

class Utils:
    @staticmethod
    def get_mouse_event():
        return pygame.mouse.get_pos()

    @staticmethod
    def left_click_event():
        mouse_btn = pygame.mouse.get_pressed()
        left_click = False
        if mouse_btn[0]:
            left_click = True
        return left_click

    @staticmethod
    def convert_moves_to_uci(legal_moves: list[list[list[int, int], tuple[int, int]]]) -> list[str]:
        def coords_to_uci_square(pos: tuple[int, int]) -> str:
            x, y = pos
            file = chr(ord('a') + x)
            rank = str(8 - y)
            return file + rank

        uci_moves = []
        for from_pos, to_pos in legal_moves:
            from_square = coords_to_uci_square(from_pos)
            to_square = coords_to_uci_square(to_pos)
            uci_move = from_square + to_square
            uci_moves.append(uci_move)
        return uci_moves

    @staticmethod
    def uci_move_to_coords(uci_move: str) -> list[list[int]]:
        from_square = uci_move[:2]
        to_square = uci_move[2:4]

        from_x = ord(from_square[0]) - ord('a')
        from_y = 8 - int(from_square[1])

        to_x = ord(to_square[0]) - ord('a')
        to_y = 8 - int(to_square[1])

        move_coords = [[from_x, from_y], [to_x, to_y]]
        return move_coords

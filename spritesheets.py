import pygame


class PieceSprites(pygame.sprite.Sprite):
    def __init__(self, filename, cols, rows):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.cols = cols
        self.rows = rows
        self.cell_count = cols * rows
        self.rect = self.spritesheet.get_rect()
        w = self.cell_width = self.rect.width // self.cols
        h = self.cell_height = self.rect.height // self.rows
        self.cells = [(i % cols * w, i // cols * h, w, h) for i in range(self.cell_count)]
        self.pieces = {
            'white_king': 0,
            'white_queen': 1,
            'white_bishop': 2,
            'white_knight': 3,
            'white_rook': 4,
            'white_pawn': 5,
            'black_king': 6,
            'black_queen': 7,
            'black_bishop': 8,
            'black_knight': 9,
            'black_rook': 10,
            'black_pawn': 11,
        }

    def draw(self, surface, piece, coords):
        piece_name = f"{piece.color}_{piece.__class__.__name__.lower()}"
        index = self.pieces[piece_name]
        surface.blit(self.spritesheet, coords, self.cells[index])

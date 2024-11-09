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
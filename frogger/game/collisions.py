"""
collisions: frog-vs-vehicle collision detection.
"""

from game.renderer import CELL_SIZE


def check_collision(frog, vehicles):
    """
    Returns True if the frog is currently hit by any vehicle, based on
    whether their on-screen rectangles actually overlap.
    """
    frog_rect = frog.get_rect(CELL_SIZE)
    return any(frog_rect.colliderect(v.get_rect(CELL_SIZE)) for v in vehicles)

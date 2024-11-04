"""
My first application
"""

import importlib.metadata
import os
import sys
from pathlib import Path

import pygame


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)


def main():
    # Linux desktop environments use an app's .desktop file to integrate the app
    # in to their application menus. The .desktop file of this app will include
    # the StartupWMClass key, set to app's formal name. This helps associate the
    # app's windows to its menu item.
    #
    # For association to work, any windows of the app must have WMCLASS property
    # set to match the value set in app's desktop file. For PyGame, this is set
    # using the SDL_VIDEO_X11_WMCLASS environment variable.

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    metadata = importlib.metadata.metadata(app_module)

    os.environ["SDL_VIDEO_X11_WMCLASS"] = metadata["Formal-Name"]

    pygame.init()
    pygame.display.set_caption(metadata["Formal-Name"])
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        screen.fill(WHITE)
        pygame.display.flip()

    pygame.quit()

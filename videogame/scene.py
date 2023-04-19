# Michael Shafae
# CPSC 386-01
# 2050-01-01
# mshafae@csu.fullerton.edu
# @mshafae
#
# Lab 00-00
#
# Partners:
#
# This my first program and it prints out Hello World!
#

"""Scene objects for making games with PyGame."""

import os
import pygame
import rgbcolors
from animation import Explosion


# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        # This should be commented out or removed since it generates a lot of noise.
        # print(str(event))
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Bye bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""

    def update_scene(self):
        """Update the scene state."""

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.5)
            except pygame.error as pygame_error:
                print("\n".join(pygame_error.args))
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class PressAnyKeyToExitScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class Circle:
    """Class representing a circle with a bounding rect."""

    def __init__(self, center_x, center_y, radius, color, name="None"):
        self._center_x = center_x
        self._center_y = center_y
        self._radius = radius
        self._color = color
        self._name = name
        self._is_exploding = False

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def center(self):
        """Return the circle's center."""
        return pygame.Vector2(self._center_x, self._center_y)

    @property
    def rect(self):
        """Return bounding rect."""
        left = self._center_x - self._radius
        top = self._center_y - self._radius
        width = 2 * self._radius
        return pygame.Rect(left, top, width, width)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return 2 * self._radius

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return 2 * self._radius

    @property
    def is_exploding(self):
        return self._is_exploding

    @is_exploding.setter
    def is_exploding(self, val):
        self._is_exploding = val

    def draw(self, screen):
        """Draw the circle to screen."""
        pygame.draw.circle(screen, self._color, self.center, self.radius)

    def __repr__(self):
        """Circle stringify."""
        return f'Circle({self._center_x}, {self._center_y}, {self._radius}, {self._color}, "{self._name}")'


class SpriteScene(PressAnyKeyToExitScene):
    def __init__(self, screen):
        self._main_dir = os.path.split(os.path.abspath(__file__))[0]
        self._data_dir = os.path.join(self._main_dir, "data")
        soundtrack = os.path.join(
            self._data_dir, "8bp051-06-random-happy_ending_after_all.mp3"
        )
        super().__init__(screen, rgbcolors.black, soundtrack)
        self._explosion_sound = pygame.mixer.Sound(
            os.path.join(self._data_dir, "Pillsbury.aif")
        )
        self._circles = None
        self.make_circles()
        self._render_updates = pygame.sprite.RenderUpdates()
        Explosion.containers = self._render_updates

    def make_circles(self):
        circle_width = 100
        circle_radius = circle_width // 2
        gutter_width = circle_width // 8
        (width, height) = self._screen.get_size()
        x_step = gutter_width + circle_width
        y_step = gutter_width + circle_width
        circles_per_row = (width // x_step) - 1
        num_rows = (height // y_step) - 1
        print(
            f"There will be {num_rows} rows and {circles_per_row} circles in each row."
        )
        self._circles = [
            Circle(
                x_step + (j * x_step),
                y_step + (i * y_step),
                circle_radius,
                rgbcolors.random_color(),
                f"{i+1}, {j+1}",
            )
            for i in range(num_rows)
            for j in range(circles_per_row)
        ]

    # def start_scene(self):
    #     super().start_scene()

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for circle in self._circles:
                if circle.rect.collidepoint(event.pos):
                    Explosion(circle)
                    circle.is_exploding = True
                    self._explosion_sound.play()

    def render_updates(self):
        super().render_updates()
        self._render_updates.clear(self._screen, self._background)
        self._render_updates.update()
        dirty = self._render_updates.draw(self._screen)

    def draw(self):
        super().draw()
        for circle in self._circles:
            if not circle.is_exploding:
                circle.draw(self._screen)

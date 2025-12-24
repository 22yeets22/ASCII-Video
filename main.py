import cv2
import pygame
import numpy as np
from tkinter import Tk
from tkinter.messagebox import showinfo

# ASCII characters from dark to light
CHAR_SET = """ `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"""
CELL_SIZE = 5

# Precompute brightness to ASCII lookup
gamma = 1
BRIGHTNESS_LOOKUP = [CHAR_SET[int((i / 255) ** gamma * (len(CHAR_SET) - 1))] for i in range(256)]


def show_loading_message():
    """Display a loading message using Tkinter."""
    root = Tk()
    root.withdraw()
    showinfo(
        "Currently Loading...", "This may take a while, as it needs to access your camera.\nClick OK to start loading."
    )
    root.destroy()


def initialize_pygame_window(width, height, cell_size):
    """Initialize the pygame window."""
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("ASCII Video (Output)")
    font = pygame.font.SysFont("Courier New", cell_size + 2, bold=True)
    return window, font


def boost_color(frame):
    """
    Boosts the brightness/vividness of the color while preserving the hue.
    This compensates for the black background of the ASCII window.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Make colors more colorful (Saturation * 1.3)
    s = cv2.multiply(s, 1.3)

    # Make colors brighter (Value + 60)
    # This prevents dark pixels from becoming invisible 'invisible ink'
    v = cv2.add(v, 60)

    hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def process_frame(frame, font, window, cols, rows):
    """Convert a frame to ASCII and render it in the pygame window with color."""
    # Resize frame to number of cells
    small_frame = cv2.resize(frame, (cols, rows), interpolation=cv2.INTER_LINEAR)
    greyscale = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    small_frame = boost_color(small_frame)

    window.fill((0, 0, 0))  # Clear previous frame

    for y in range(rows):
        for x in range(cols):
            brightness = greyscale[y, x]
            ascii_char = BRIGHTNESS_LOOKUP[brightness]

            color_bgr = small_frame[y, x]
            color = tuple(int(c) for c in (color_bgr[2], color_bgr[1], color_bgr[0]))

            text_surface = font.render(ascii_char, True, color)
            window.blit(text_surface, (x * CELL_SIZE, y * CELL_SIZE))


def main():
    show_loading_message()

    video = cv2.VideoCapture(0)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cols = width // CELL_SIZE
    rows = height // CELL_SIZE

    window, font = initialize_pygame_window(width, height, CELL_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ret, frame = video.read()
        if not ret:
            print("Failed to capture video frame.")
            break

        process_frame(frame, font, window, cols, rows)

        cv2.imshow("ASCII Video (Input)", frame)
        pygame.display.update()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            running = False

    video.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()

import cv2
import pygame
from tkinter import Tk
from tkinter.messagebox import showinfo


def transform(value, min1, max1, min2, max2):
    """Map a value from one range to another."""
    return (value - min1) * ((max2 - min2) / (max1 - min1)) + min2


def show_loading_message():
    """Display a loading message using Tkinter."""
    root = Tk()
    root.withdraw()
    showinfo("Currently Loading...", "This may take a while, as it needs to access your camera.\nClick OK to start loading.")
    root.destroy()


def initialize_pygame_window(width, height, cell_size):
    """Initialize the pygame window."""
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("ASCII Video (Output)")
    return window, pygame.font.SysFont("Courier New", cell_size + 2)


def process_frame(frame, char_set, size, font, window, width, height):
    """Convert a frame to ASCII and render it in the pygame window with color."""
    greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rows = height // size
    cols = width // size

    for y in range(rows):
        for x in range(cols):
            try:
                # Get brightness and corresponding ASCII character
                brightness = greyscale[y * size, x * size]
                ascii_char = char_set[int(transform(brightness, 255, 0, 0, len(char_set) - 1))]

                # Extract average color from the region in the original frame
                region = frame[y * size:(y + 1) * size, x * size:(x + 1) * size]
                avg_color = region.mean(axis=0).mean(axis=0)  # Average color in BGR format

                # Convert BGR to RGB for pygame
                color = (int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))

                # Render the ASCII character with the region's color
                text_surface = font.render(ascii_char, True, color)
                window.blit(text_surface, (x * size, y * size))
            except IndexError:
                continue  # Skip any out-of-bounds issues


def main():
    """Main program to capture video and render ASCII."""
    CHAR_SET = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~i!lI;:,\"^`. "
    CELL_SIZE = 9

    # Display loading message
    show_loading_message()

    # Initialize video capture and get dimensions
    video = cv2.VideoCapture(0)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize pygame window
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

        window.fill((0, 0, 0))
        process_frame(frame, CHAR_SET, CELL_SIZE, font, window, width, height)

        # Show the original video frame in a separate window
        cv2.imshow('ASCII Video (Input)', frame)
        pygame.display.update()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

    # Cleanup resources
    video.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()

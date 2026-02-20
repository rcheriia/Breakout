import arcade
from menu_screen import StartScreen

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Breakout Arcade"


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Создаём начальный экран
    start_screen = StartScreen(window)
    window.show_view(start_screen)

    arcade.run()


if __name__ == "__main__":
    main()
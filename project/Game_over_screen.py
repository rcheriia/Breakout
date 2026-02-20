import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class GameOverScreen(arcade.View):

    def __init__(self, window, score):
        super().__init__()
        self.window = window
        self.score = score

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        arcade.draw_text("GAME OVER",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2 + 50,
                         arcade.color.RED,
                         50,
                         anchor_x="center")

        arcade.draw_text(f"Ваш счёт: {self.score}",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2,
                         arcade.color.WHITE,
                         20,
                         anchor_x="center")

        arcade.draw_text("Нажмите ENTER, чтобы вернуться в меню",
                         SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2 - 40,
                         arcade.color.YELLOW,
                         20,
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            from menu_screen import StartScreen
            menu = StartScreen(self.window)
            self.window.show_view(menu)
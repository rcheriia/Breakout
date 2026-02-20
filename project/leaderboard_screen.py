import arcade
from leaderboard_db import get_top_scores

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class LeaderboardScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.scores = get_top_scores(10)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Таблица рекордов", 400, 550, arcade.color.YELLOW, 40, anchor_x="center")

        if not self.scores:
            arcade.draw_text("Нет рекордов", 400, 400, arcade.color.WHITE, 25, anchor_x="center")
        else:
            for i, (name, score) in enumerate(self.scores):
                arcade.draw_text(f"{i+1}. {name} — {score}", 400, 500 - i*40, arcade.color.WHITE, 25, anchor_x="center")

        arcade.draw_text("Нажмите ESC для выхода в меню", 400, 50, arcade.color.GRAY, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from menu_screen import StartScreen
            start_screen = StartScreen(self.window)
            self.window.show_view(start_screen)
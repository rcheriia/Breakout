import arcade
import arcade.gui
from game_screen import Game
from leaderboard_screen import LeaderboardScreen

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class StartScreen(arcade.View):

    def __init__(self, window):
        super().__init__(window)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        play_button = arcade.gui.UIFlatButton(text="Играть", width=200)
        leaderboard_button = arcade.gui.UIFlatButton(text="Таблица рекордов", width=200)

        self.v_box.add(play_button)
        self.v_box.add(leaderboard_button)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")

        self.manager.add(anchor)

        @play_button.event("on_click")
        def on_click_play(event):
            game_view = Game()
            self.window.show_view(game_view)

        @leaderboard_button.event("on_click")
        def on_click_leaderboard(event):
            leaderboard_view = LeaderboardScreen()
            self.window.show_view(leaderboard_view)

    def on_draw(self):
        self.clear()
        arcade.draw_text("BREAKOUT", 400, 500,
                         arcade.color.WHITE, 50,
                         anchor_x="center")
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()
import random
import math
import arcade
from leaderboard_db import add_score
from Game_over_screen import GameOverScreen

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Breakout Arcade"

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 20
BALL_RADIUS = 10

BRICK_WIDTH = 60
BRICK_HEIGHT = 25
BRICK_PADDING = 5

BASE_BALL_SPEED = 4

LEVELS = [
    {"rows": 4, "cols": 10, "max_hp": 1},
    {"rows": 5, "cols": 11, "max_hp": 2},
    {"rows": 6, "cols": 12, "max_hp": 3},
]

wall_hit_sound = arcade.load_sound("sounds/wall_hit.mp3")
block_hit_sound = arcade.load_sound("sounds/block_hit.mp3")

# ---------------- БЛОК ----------------
class Brick(arcade.SpriteSolidColor):
    def __init__(self, width, height, hp):
        super().__init__(width, height, arcade.color.WHITE)
        self.hp = hp
        self.update_color()

        # Анимация разрушения
        self.is_destroying = False
        self.shrink_speed = 4  # пикселей за кадр
        self.scored = False  # начислено ли очко

    def hit(self):
        self.hp -= 1
        self.update_color()
        if self.hp <= 0:
            self.start_destruction()
            return True  # уничтожен (запуск анимации)
        return False

    def update_color(self):
        if self.hp >= 3:
            self.color = arcade.color.RED
        elif self.hp == 2:
            self.color = arcade.color.ORANGE
        else:
            self.color = arcade.color.YELLOW

    def start_destruction(self):
        self.is_destroying = True

    def update(self, delta_time: float = 1/60):
        if self.is_destroying:
            # Сжимаем блок по центру
            self.width -= self.shrink_speed
            self.height -= self.shrink_speed
            self.center_x += self.shrink_speed / 2
            self.center_y += self.shrink_speed / 2

            if self.width <= 0 or self.height <= 0:
                self.remove_from_sprite_lists()


# ---------------- БОНУС ----------------
class Bonus(arcade.SpriteCircle):
    def __init__(self, x, y):
        super().__init__(8, arcade.color.GREEN)
        self.center_x = x
        self.center_y = y
        self.speed = 200  # пикселей в секунду
        self.bonus_type = random.choice(["expand", "slow", "score", "multiball"])

    def update(self, delta_time: float = 1/60):
        # падение строго вниз
        self.center_y -= self.speed * delta_time


class Ball(arcade.SpriteCircle):
    def __init__(self, radius, speed):
        super().__init__(radius, arcade.color.WHITE)
        angle = random.uniform(-0.5, 0.5)
        self.change_x = speed * math.sin(angle)
        self.change_y = speed * math.cos(angle)

    def move_and_collide(self, bricks, paddle, delta_time):
        steps = int(max(abs(self.change_x), abs(self.change_y))) + 1
        dx = self.change_x / steps
        dy = self.change_y / steps

        for _ in range(steps):
            self.center_x += dx
            self.center_y += dy

            # ЛЕВАЯ СТЕНА
            if self.left <= 0 and self.change_x < 0:
                self.left = 0
                self.change_x *= -1
                arcade.play_sound(wall_hit_sound)
                break

            # ПРАВАЯ СТЕНА
            if self.right >= SCREEN_WIDTH and self.change_x > 0:
                self.right = SCREEN_WIDTH
                self.change_x *= -1
                arcade.play_sound(wall_hit_sound)
                break

            # ВЕРХ
            if self.top >= SCREEN_HEIGHT and self.change_y > 0:
                self.top = SCREEN_HEIGHT
                self.change_y *= -1
                arcade.play_sound(wall_hit_sound)
                break

            # Столкновение с платформой
            if arcade.check_for_collision(self, paddle) and self.change_y < 0:
                self.bottom = paddle.top + 1
                self.change_y *= -1
                hit_pos = (self.center_x - paddle.center_x) / (PADDLE_WIDTH / 2)
                self.change_x = hit_pos * 6

            # Столкновение с блоками
            hit_list = arcade.check_for_collision_with_list(self, bricks)
            for brick in hit_list:
                arcade.play_sound(block_hit_sound)
                destroyed = brick.hit()
                overlap_x = self.center_x - brick.center_x
                overlap_y = self.center_y - brick.center_y

                if abs(overlap_y) > abs(overlap_x):
                    if overlap_y > 0:
                        self.bottom = brick.top + 1
                    else:
                        self.top = brick.bottom - 1
                    self.change_y *= -1
                else:
                    if overlap_x > 0:
                        self.left = brick.right + 1
                    else:
                        self.right = brick.left - 1
                    self.change_x *= -1
                return brick

        return False


# ---------------- ИГРА ----------------
class Game(arcade.View):

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.level = 0
        self.score = 0
        self.paddle_speed = 0
        self.game_completed = False
        self.lives = 3
        self.speed = BASE_BALL_SPEED + self.level * 1.5

        self.setup()

    def setup(self):
        self.bricks = arcade.SpriteList()
        self.paddle_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()
        self.speed = BASE_BALL_SPEED + self.level * 1.5
        ball = Ball(BALL_RADIUS, self.speed)
        ball.center_x = SCREEN_WIDTH // 2
        ball.center_y = 80
        self.ball_list.append(ball)
        self.bonus_list = arcade.SpriteList()

        # 🎲 Рандомная генерация блоков
        level_data = LEVELS[self.level]
        for row in range(level_data["rows"]):
            for col in range(level_data["cols"]):
                if random.random() > 0.15:  # 15% пропусков
                    hp = random.randint(1, level_data["max_hp"])
                    brick = Brick(BRICK_WIDTH, BRICK_HEIGHT, hp)
                    brick.center_x = 60 + col * (BRICK_WIDTH + BRICK_PADDING)
                    brick.center_y = SCREEN_HEIGHT - 60 - row * (BRICK_HEIGHT + BRICK_PADDING)
                    self.bricks.append(brick)

        # Платформа
        self.paddle = arcade.SpriteSolidColor(PADDLE_WIDTH, PADDLE_HEIGHT, arcade.color.BLUE)
        self.paddle.center_x = SCREEN_WIDTH // 2
        self.paddle.center_y = 40
        self.paddle_list.append(self.paddle)

        # 🚀 Ускорение мяча на каждом уровне
        self.speed = BASE_BALL_SPEED + self.level * 1.5
        self.ball = Ball(BALL_RADIUS, self.speed)
        self.ball.center_x = SCREEN_WIDTH // 2
        self.ball.center_y = 80
        self.ball_list.append(self.ball)

    # ---------------- РИСОВАНИЕ ----------------
    def on_draw(self, delta_time = 1/60):
        self.clear()
        self.bricks.draw()
        self.paddle_list.draw()
        self.ball_list.draw()
        self.bonus_list.draw()

        arcade.draw_text(f"Уровень: {self.level + 1}", 10, 10, arcade.color.WHITE, 14)
        arcade.draw_text(f"Счёт: {self.score}", 10, 30, arcade.color.WHITE, 14)

        # 🏅 Медаль
        if self.game_completed:
            arcade.draw_circle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 60, arcade.color.GOLD)
            arcade.draw_text("ПОБЕДА!", SCREEN_WIDTH // 2 - 70,
                             SCREEN_HEIGHT // 2 - 10,
                             arcade.color.BLACK, 24)

        # ❤️ Жизни
        for i in range(self.lives):
            x = SCREEN_WIDTH - 30 - i * 30
            y = SCREEN_HEIGHT - 30

            arcade.draw_circle_filled(x - 6, y, 8, arcade.color.RED)
            arcade.draw_circle_filled(x + 6, y, 8, arcade.color.RED)
            arcade.draw_triangle_filled(
                x - 14, y,
                x + 14, y,
                x, y - 16,
                arcade.color.RED
            )

    # ---------------- УПРАВЛЕНИЕ ----------------
    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.paddle_speed = -8
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.paddle_speed = 8

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A,
                   arcade.key.RIGHT, arcade.key.D):
            self.paddle_speed = 0

    # ---------------- ЛОГИКА ----------------
    def on_update(self, delta_time):
        if self.game_completed:
            return

        # ---------------- Движение мячей ----------------
        for ball in self.ball_list:
            hit_brick = ball.move_and_collide(self.bricks, self.paddle, delta_time)
            # Если столкновение с блоком и блок разрушен
            if hit_brick and hit_brick.is_destroying and not hit_brick.scored:
                self.score += 10  # начисляем очки один раз
                hit_brick.scored = True
                arcade.play_sound(block_hit_sound)

                # 🎁 Шанс выпадения бонуса
                if random.random() < 0.5:
                    bonus = Bonus(hit_brick.center_x, hit_brick.center_y)
                    self.bonus_list.append(bonus)

        # ---------------- Движение бонусов ----------------
        self.bonus_list.update()

        # ---------------- Движение платформы ----------------
        self.paddle.center_x += self.paddle_speed
        self.paddle.left = max(self.paddle.left, 0)
        self.paddle.right = min(self.paddle.right, SCREEN_WIDTH)

        # ---------------- Проверка падения мячей ----------------
        for ball in self.ball_list:
            if ball.bottom <= 0:
                ball.remove_from_sprite_lists()

        if len(self.ball_list) == 0:
            self.lives -= 1
            if self.lives <= 0:
                add_score("Игрок", self.score)
                self.window.show_view(GameOverScreen(self.window, self.score))
                return
            else:
                # Создаем новый мяч над платформой
                speed = BASE_BALL_SPEED + self.level * 1.5
                safe_y = self.paddle.top + BALL_RADIUS + 1
                new_ball = Ball(BALL_RADIUS, speed)
                new_ball.center_x = self.paddle.center_x
                new_ball.center_y = safe_y
                angle = random.uniform(-0.5, 0.5)
                new_ball.change_x = speed * math.sin(angle)
                new_ball.change_y = speed * math.cos(angle)
                self.ball_list.append(new_ball)

        # ---------------- Подбор бонусов ----------------
        for bonus in arcade.check_for_collision_with_list(self.paddle, self.bonus_list):
            if bonus.bonus_type == "expand":
                self.paddle.width = min(self.paddle.width + 40, 220)
            elif bonus.bonus_type == "slow":
                for ball in self.ball_list:
                    ball.change_x *= 0.8
                    ball.change_y *= 0.8
            elif bonus.bonus_type == "score":
                self.score += 100
            bonus.remove_from_sprite_lists()

        # ---------------- Удаление упавших бонусов ----------------
        for bonus in self.bonus_list:
            if bonus.top < 0:
                bonus.remove_from_sprite_lists()

        # ---------------- Анимация разрушения блоков ----------------
        self.bricks.update(delta_time)

        # ---------------- Следующий уровень ----------------
        if len(self.bricks) == 0:
            self.level += 1
            if self.level >= len(LEVELS):
                self.game_completed = True
            else:
                self.setup()


if __name__ == "__main__":
    game = Game()
    arcade.run()
import arcade
import os
import random

# set values for window
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

# create the character (rectangle man)
#CHAR_WIDTH = 25
#CHAR_HEIGHT = 45

# set the speed that rectangle man can walk
CHAR_SPEED = 3

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.textures = []
        texture = arcade.load_texture('./resources/character.png')
        self.textures.append(texture)
        self.set_texture(0)

        self.char_width = self.texture.image.width
        self.char_height = self.texture.image.height

        self.health = 0


    def update(self):

        # verify that player can't walk off screen
        self.center_x += self.change_x
        if self.center_x < self.char_width/2:
            self.center_x = self.char_width/2
        if self.center_x > WINDOW_WIDTH - (self.char_width/2):
            self.center_x = WINDOW_WIDTH - (self.char_width/2)

        self.center_y += self.change_y
        if self.center_y < self.char_height/2:
            self.center_y = self.char_height/2
        if self.center_y > WINDOW_HEIGHT - (self.char_height/2):
            self.center_y = WINDOW_HEIGHT - (self.char_height/2)


class BadGuy(arcade.Sprite):

    def __init__(self):

        super().__init__()
        self.textures = []
        texture = arcade.load_texture('./resources/monster.png')
        self.textures.append(texture)
        self.set_texture(0)

        # randomly intitialize the direction of travel
        self.x_direc = random.choice([-1,1])
        self.y_direc = random.choice([-1,1])

        # set bad guy speed
        self.speed = 1


    def update(self):

        # random 1/20 chance of changing direction each move
        self.x_direc *= random.choice([-1,]+[1]*19)
        self.y_direc *= random.choice([-1,]+[1]*19)

        x_move = self.speed*self.x_direc + random.randint(-1,1)
        y_move = self.speed*self.y_direc + random.randint(-1,1)

        # bad guys loop around the screen
        self.center_x += x_move
        if self.center_x <= 0:
            self.center_x = WINDOW_WIDTH
        elif self.center_x >= WINDOW_WIDTH:
            self.center_x = 0

        self.center_y += y_move
        if self.center_y <= 0:
            self.center_y = WINDOW_HEIGHT
        elif self.center_y >= WINDOW_HEIGHT:
            self.center_y = 0



class Fruit(arcade.Sprite):

    def __init__(self):

        super().__init__()
        self.textures = []
        texture = arcade.load_texture('./resources/watermelon.png')
        self.textures.append(texture)
        self.set_texture(0)



class GameView(arcade.View):

    def __init__(self):

        super().__init__()

        self.all_sprites_list = None
        self.player = None

        self.background = None

        self.game_time = 0
        self.score = 0
        self.game_over = False
        self.game_running = True

        arcade.set_background_color(arcade.color.BLACK)


    def setup(self):

        self.all_player_list = arcade.SpriteList()
        self.all_enemy_list = arcade.SpriteList()
        self.all_fruit_list = arcade.SpriteList()

        # setup character and initial position
        self.player = Player()
        self.player.center_x = WINDOW_WIDTH//2
        self.player.center_y = WINDOW_HEIGHT//2
        self.all_player_list.append(self.player)

        # add some bad guys, but not too close to player's initial start position
        for i in range(2):
            bad_guy = BadGuy()
            bad_guy.center_x = random.choice([random.randrange(0, WINDOW_WIDTH/4), random.randrange(WINDOW_WIDTH*3/4, WINDOW_WIDTH)])
            bad_guy.center_y = random.choice([random.randrange(0, WINDOW_HEIGHT/4), random.randrange(WINDOW_HEIGHT*3/4, WINDOW_HEIGHT)])
            self.all_enemy_list.append(bad_guy)

        # add some fruit
        for i in range(2):
            fruit = Fruit()
            fruit.center_x = random.randrange(WINDOW_WIDTH)
            fruit.center_y = random.randrange(WINDOW_HEIGHT)
            self.all_fruit_list.append(fruit)

        # sets up the game and initialzied variables
        self.background = arcade.load_texture('./resources/grass.jpg')


    def on_update(self, dt):

        self.all_player_list.update()
        self.all_enemy_list.update()

        self.game_time += dt

        # enemy added every every 30 seconds
        if int(self.game_time / 30) + 2 > len(self.all_enemy_list):
            bad_guy = BadGuy()
            bad_guy.center_x = random.choice([x for x in range(WINDOW_WIDTH) if abs(x-self.player.center_x)>WINDOW_WIDTH/2])
            bad_guy.center_y = random.choice([y for y in range(WINDOW_HEIGHT) if abs(y-self.player.center_y)>WINDOW_HEIGHT/2])
            bad_guy.speed = random.randrange(1, 3)
            self.all_enemy_list.append(bad_guy)

        # check if player gets hit
        hit_list = arcade.check_for_collision_with_list(self.player, self.all_enemy_list)
        if hit_list:
            self.player.health -= 1

        # check if player got fruit
        hit_fruit = arcade.check_for_collision_with_list(self.player, self.all_fruit_list)
        for f in hit_fruit:
            f.remove_from_sprite_lists()
            self.player.health += 5
            self.score += 1
            fruit = Fruit()
            fruit.center_x = random.randrange(WINDOW_WIDTH)
            fruit.center_y = random.randrange(WINDOW_HEIGHT)
            self.all_fruit_list.append(fruit)

        # if health < 0, game over:
        if self.player.health < 0:
            view = GameOverView(self.score, self.game_time)
            self.window.show_view(view)



    def on_draw(self):

        #if self.game_running:
        # render the screen
        arcade.start_render()

        # draw the background and character
        arcade.draw_lrwh_rectangle_textured(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, self.background)
        self.all_player_list.draw()
        self.all_enemy_list.draw()
        self.all_fruit_list.draw()

        arcade.draw_text(f'{self.player.health}', WINDOW_WIDTH/2, WINDOW_HEIGHT-30, arcade.color.RED, 24)
        arcade.draw_text(f'Score: {self.score}', 10, 20, arcade.color.WHITE,16)
        arcade.draw_text(f'Time: {int(self.game_time/60)}:{int(self.game_time % 60)}', 10, 5, arcade.color.WHITE,16)


    def on_key_press(self, key, modifiers):
        # define what happens for each arrow key
        if key == arcade.key.UP:
            self.player.change_y = CHAR_SPEED
        elif key == arcade.key.DOWN:
            self.player.change_y = -1*CHAR_SPEED
        elif key == arcade.key.LEFT:
            self.player.change_x = -1*CHAR_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = CHAR_SPEED

    def on_key_release(self, key, modifier):
        # reset change when key is released
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0



class StartView(arcade.View):

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture('./resources/grass.jpg')
        self.fruit = arcade.load_texture('./resources/watermelon.png')
        self.monster = arcade.load_texture('./resources/monster.png')


    def on_draw(self):
        arcade.start_render()
        self.texture.draw_sized(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, WINDOW_WIDTH, WINDOW_HEIGHT)

        arcade.draw_text('Collect these: ', WINDOW_WIDTH/5, WINDOW_HEIGHT*3/5-50, arcade.color.WHITE, 18)
        self.fruit.draw_scaled(WINDOW_WIDTH/5 + 150, WINDOW_HEIGHT*3/5-50, 1)

        arcade.draw_text('Avoid these: ', WINDOW_WIDTH/5, WINDOW_HEIGHT*3/5, arcade.color.WHITE, 18)
        self.monster.draw_scaled(WINDOW_WIDTH/5+150, WINDOW_HEIGHT*3/5, 1)
        arcade.draw_text('Press Enter to Begin', WINDOW_WIDTH/6, WINDOW_HEIGHT/4, arcade.color.WHITE, 24)


    def on_key_press(self, key, modifiers):
        # define what happens for each arrow key
        if key==arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)




class GameOverView(arcade.View):

    def __init__(self, score, game_time):
        super().__init__()
        self.score = score
        self.game_time = game_time
        self.texture = arcade.load_texture('./resources/grass.jpg')

    def on_draw(self):
        arcade.draw_text('GAME OVER', 0, WINDOW_HEIGHT*2//3, arcade.color.WHITE, 24)
        arcade.draw_text(f'Score = {self.score}', 0, WINDOW_HEIGHT*2//3+50, arcade.color.WHITE, 24)
        arcade.draw_text('Press Enter to Start Again', 0, WINDOW_HEIGHT//2, arcade.color.WHITE, 24)

    def on_key_press(self, key, modifiers):
        if key==arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)



if __name__=='__main__':
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Game')
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()
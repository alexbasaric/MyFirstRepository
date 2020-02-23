'''
Singleplayer Pong by Luka Jovanovic
'''

import pygame
import random
import math
import pickle
from enum import Enum

pygame.font.init()

WIN_WIDTH = 900
WIN_HEIGHT = 600

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Pong!")

MAIN_FONT = pygame.font.Font('BebasNeue-Regular.ttf', 30)
FINAL_FONT = pygame.font.Font('BebasNeue-Regular.ttf', 43)
STAT_FONT = pygame.font.Font('BebasNeue-Regular.ttf', 50)
SCORE_FONT = pygame.font.Font('BebasNeue-Regular.ttf', 160)

COLOR_BLACK = (255, 255, 255)
COLOR_WHITE = (200, 200, 200)
COLOR_GREY = (128, 128, 128)
COLOR_OTHER = (32, 32, 32)
COLOR_64 = (64, 64, 64)

score1 = 0
score2 = 0
PLAY_UNTIL = 5


# The enum Side will be used to determine which side is the paddle (board), left or right
class Side(Enum):
    LEFT = 1
    RIGHT = 2

# Board represents the paddle or bat, on each side of the playing field
class Board:
    WIDTH = 10
    LENGTH = 140

    # Initialize a paddle on given side of the table
    def __init__(self, side):
        if Side.LEFT == side:
            self.x = 30
        else:
            self.x = WIN_WIDTH - 30

        self.y = WIN_HEIGHT/2 - self.LENGTH/2

        self.vel = 0.5  # 0.5
        self.side = side

    # move paddle up or down
    def move(self, direction):
        if direction == 'up' and self.y >= 0:
            self.y -= self.vel
        elif direction == 'down' and self.y <= WIN_HEIGHT - self.LENGTH:
            self.y += self.vel

    # Draws the paddle
    def draw(self, win):
        pygame.draw.rect(win, COLOR_BLACK, (self.x, self.y, self.WIDTH, self.LENGTH))

    # checks coordinates of the ball and the paddle and calculates if there was a hit
    # returns True if there was a hit
    def hit_the_ball(self, ball, ):
        if self.side == Side.LEFT:
            if self.x + self.WIDTH >= int(ball.x):
                for i in range(int(self.y), int(self.y + self.LENGTH)):
                    if int(ball.y) == i:
                        return True
        else:
            if self.x <= int(ball.x) + Board.WIDTH:
                for i in range(int(self.y), int(self.y + Board.LENGTH)):
                    if int(ball.y) == i:
                        return True

        return False


# Class Ball represnets the ping pong ball
class Ball:

    # Initializes the ball, with initial velocity and random angle of movement and direction
    def __init__(self):
        self.x = WIN_WIDTH/2
        self.y = WIN_HEIGHT/2
        self.vel = 0.35  # 0.35
        self.tilt = random.randrange(45, 135)
        self.direction = random.randint(1, 2)
        self.choices = [-45, 45]

    # Draw the ball on the screen
    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), (self.x, self.y, 10, 10))

    # Bounce the ball of the sides of the playing field
    def bounce(self):
        self.tilt = (180 - self.tilt) % 360
        self.vel *= 1.02  # 1.02

    # bounces the ball of the paddle(board)
    def vertical_bounce(self):
        self.tilt = (360 - self.tilt) % 360
        self.vel *= 1.02  # 1.02

    # initial move of the ball, after the previous point was scored
    def first_move(self):
        self.tilt = random.randrange(45,135)
        self.direction = random.randint(1, 2)
        if self.direction == 1:
            tilt_radians = math.radians(self.tilt)
            self.x += self.vel * math.sin(tilt_radians)
            self.y -= self.vel * math.cos(tilt_radians)
        if self.direction == 2:
            self.tilt = self.tilt + 180
            tilt_radians = math.radians(self.tilt)
            self.x += self.vel * math.sin(tilt_radians)
            self.y -= self.vel * math.cos(tilt_radians)

    # Moves the ball in each cycle
    def move(self, just_once, computer, player):
        if just_once:
            self.first_move()

        global score1
        global score2
        tilt_radians = math.radians(self.tilt)
        self.x += self.vel * math.sin(tilt_radians)
        self.y -= self.vel * math.cos(tilt_radians)
        if self.y <= 0 or self.y >= WIN_HEIGHT:
            self.bounce()

        ret = False
        if self.x <= 0:
            self.reset()
            score2 += 1
            ret = True

        if self.x >= WIN_WIDTH:
            self.reset()
            score1 += 1
            ret = True

        if player.hit_the_ball(self) or computer.hit_the_ball(self):
            self.vertical_bounce()

        return ret

    def reset(self):
        self.tilt = random.randrange(45, 135)
        self.direction = random.randint(1, 2)
        self.x = WIN_WIDTH / 2
        self.y = WIN_HEIGHT / 2
        self.vel = 0.35 # 0.35


# StartBox represents the box that shows instructions of how to start the game, i.e. click with the mouse
class StartBox:
    def __init__(self, width, height, game_over):
        self.x = WIN_WIDTH/2 - width/2
        self.y = WIN_HEIGHT/2 - height/2
        self.w = width
        self.h = height
        if game_over:
            self.line1 = "Game Over"
            self.line2 = "Click here for another game"
        else:
            self.line1 = "Click here"
            self.line2 = "to start game"

    # loops until user clicks inside the box, or closes the window
    def wait_for_click(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("User wants to quit")

        offset = 50
        pygame.draw.rect(WIN, COLOR_BLACK, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(WIN, COLOR_WHITE,  (self.x + offset, self.y + offset, self.w - 2*offset, self.h-2*offset))

        text = STAT_FONT.render(self.line1, 1, COLOR_OTHER)
        WIN.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 280 - text.get_height() / 2))
        text = STAT_FONT.render(self.line2, 1, COLOR_OTHER)
        WIN.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 320 - text.get_height() / 2))

        mousepos = pygame.mouse.get_pos()
        pygame.display.flip()

        if self.x < mousepos[0] < self.x + self.w and self.y < mousepos[1] < self.y + self.h:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONUP:
                    return True

# Draws title of the game
def draw_title(win):
    win.fill(COLOR_OTHER)
    text = MAIN_FONT.render('PONG', 1, COLOR_GREY)
    win.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 8))

# Draws score on the screen
def draw_score(win, player1_score, player2_score):
    text = SCORE_FONT.render(str(player1_score), 1, COLOR_GREY)
    win.blit(text, (WIN_WIDTH / 4 - text.get_width() / 2, 300 - text.get_height() / 2))
    text = SCORE_FONT.render(str(player2_score), 1, COLOR_GREY)
    win.blit(text, ((WIN_WIDTH / 4) * 3 - text.get_width() / 2, 300 - text.get_height() / 2))
    pygame.draw.rect(win, COLOR_64, (WIN_WIDTH/2, 45, 2, WIN_WIDTH))


# Draws screen after each cycle
def draw_game(win, player1_board, ball, player2_board, player1_score, player2_score):
    draw_title(win)
    draw_score(win, player1_score, player2_score)
    player1_board.draw(win)
    player2_board.draw(win)
    ball.draw(win)
    pygame.display.flip()


# calculates the computer move using NEAT python AI framework
def make_computer_move(nets, computer, ball):
    output = nets[0].activate((computer.y - 5, computer.y - ball.y, computer.x - ball.x))

    if output[
        0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump (should the bird jump? yes or no)
        computer.move('up')
    elif output[0] <= -0.5:
        computer.move('down')

# Calculates player move based on key pressed
def make_player_mover(player):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] or keys[pygame.K_KP8] or keys[pygame.K_UP]:
        player.move('up')
    if keys[pygame.K_s] or keys[pygame.K_KP2] or keys[pygame.K_DOWN]:
        player.move('down')


# Main loop
def main():

    global WIN
    global score1
    global score2
    nets = []
    with open('TheAI.pickle', 'rb') as pickle_file:
        x = pickle.load(pickle_file)
    nets.append(x)

    computer = Board(Side.RIGHT)
    player = Board(Side.LEFT)
    ball = Ball()
    just_once = True

    begin = False
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        make_computer_move(nets, computer, ball)
        make_player_mover(player)
        just_once = ball.move(just_once, computer, player)

        draw_game(WIN, player, ball, computer, score1, score2)

        game_over = score1 == PLAY_UNTIL or score2 == PLAY_UNTIL

        if not begin or game_over:
            begin = False
            try:
                while not begin:
                    start_box = StartBox(350, 250, game_over)
                    begin = start_box.wait_for_click()
                    run = True
                    score1 = 0
                    score2 = 0
            except Exception as err:
                run = False


main()

pygame.quit()
quit()


'''
Singleplayer Pong by Luka Jovanovic
'''

import pygame
import random
import math
import pickle
pygame.font.init()

WIN_WIDTH = 1200
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

class Board:
    WIDTH = 10
    LENGTH = 140
    def __init__(self, x, y):
        self.y = y
        self.x = x
        self.vel = 0.5  # 0.5

    def move(self, direction):
        if direction == 'up' and self.y >= 0:
            self.y -= self.vel
        elif direction == 'down' and self.y <= 460:
            self.y += self.vel

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), (self.x, self.y, self.WIDTH, self.LENGTH))

class Ball:
    def __init__(self):
        self.x = WIN_WIDTH/2
        self.y = WIN_HEIGHT/2
        self.vel = 0.35  # 0.35
        self.tilt = random.randrange(45, 135)
        self.direction = random.randint(1, 2)
        self.choices = [-45, 45]

    def draw(self, win):
        try:
            pygame.draw.rect(win, (255, 255, 255), (self.x, self.y, 10, 10))
        except: pass

    def bounce(self):
        self.tilt = (180 - self.tilt) % 360
        self.vel *= 1.02  # 1.02

    def vertical_bounce(self):
        self.tilt = (360 - self.tilt) % 360
        self.vel *= 1.02  # 1.02

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

    def move(self):
        tilt_radians = math.radians(self.tilt)
        self.x += self.vel * math.sin(tilt_radians)
        self.y -= self.vel * math.cos(tilt_radians)

    def reset(self):
        self.tilt = random.randrange(45, 135)
        self.direction = random.randint(1, 2)
        self.x = WIN_WIDTH / 2
        self.y = WIN_HEIGHT / 2
        self.vel = 0.35 # 0.35


class StartBox:
    def __init__(self, width, height, line1, line2):
        self.x = WIN_WIDTH/2 - width/2
        self.y = WIN_HEIGHT/2 - height/2
        self.w = width
        self.h = height
        self.line1 = line1
        self.line2 = line2

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
                if event.type == pygame.MOUSEBUTTONUP:
                    return True


def draw_title(win):
    win.fill(COLOR_OTHER)
    text = MAIN_FONT.render('PONG', 1, COLOR_GREY)
    win.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 8))


def draw_score(win, player1_score, player2_score):
    text = SCORE_FONT.render(str(player1_score), 1, COLOR_GREY)
    win.blit(text, (WIN_WIDTH / 4 - text.get_width() / 2, 300 - text.get_height() / 2))
    text = SCORE_FONT.render(str(player2_score), 1, COLOR_GREY)
    win.blit(text, ((WIN_WIDTH / 4) * 3 - text.get_width() / 2, 300 - text.get_height() / 2))
    pygame.draw.rect(win, COLOR_64, (WIN_WIDTH/2, 45, 2, WIN_WIDTH))


def draw_game(win, player1_board, ball, player2_board, player1_score, player2_score):
    draw_title(win)
    draw_score(win, player1_score, player2_score)
    player1_board.draw(win)
    player2_board.draw(win)
    ball.draw(win)


def main():

    global WIN
    nets = []
    with open('TheAI.pickle', 'rb') as pickle_file:
        x = pickle.load(pickle_file)
    nets.append(x)

    computer = Board(WIN_WIDTH - 30, 230)
    player = Board(20, 230)

    score2 = 0
    score1 = 0
    ball = Ball()
    justonce = True

    play_until = 3
    begin = False
    run = True

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        while not begin:
            start_box = StartBox(250, 350, 'CLICK', 'TO BEGIN')
            draw_game(WIN, player, ball, computer, score1, score2)
            begin = start_box.wait_for_click()



        output = nets[0].activate((computer.y - 5, computer.y - ball.y, computer.x - ball.x))

        if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump (should the bird jump? yes or no)
            computer.move('up')
        elif output[0] <= -0.5:
            computer.move('down')

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_KP8] or keys[pygame.K_UP]:
            player.move('up')
        if keys[pygame.K_s] or keys[pygame.K_KP2] or keys[pygame.K_DOWN]:
            player.move('down')

        if justonce:
            ball.first_move()
            justonce = False

        ball.move()
        if ball.y <= 0 or ball.y >= WIN_HEIGHT:
            ball.bounce()

        if ball.x <= 0:
            score2 += 1
            justonce = True
            ball.reset()

        if ball.x >= WIN_WIDTH:
            score1 += 1
            justonce = True
            ball.reset()

        try:
            if ball.vel <= 0.9:
                if player.x + 10 == int(ball.x):
                    for i in range(int(player.y), int(player.y + 141)):
                        if int(ball.y) == i:
                            ball.vertical_bounce()

                if computer.x == int(ball.x) + 10:
                    for i in range(int(computer.y), int(computer.y + 141)):
                        if int(ball.y) == i:
                            ball.vertical_bounce()
            else:
                if player.x + 10 >= int(ball.x):
                    for i in range(int(player.y), int(player.y + 141)):
                        if int(ball.y) == i:
                            ball.vertical_bounce()

                if computer.x <= int(ball.x) + 10:
                    for i in range(int(computer.y), int(computer.y + 141)):
                        if int(ball.y) == i:
                            ball.vertical_bounce()

            draw_game(WIN, player, ball, computer, score1, score2)
            pygame.display.flip()
        except:
            pass

        if score1 == play_until or score2 == play_until:
            begin = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            try:
                while not begin:
                    start_box = StartBox(350,250,'GAME OVER', 'Another?')
                    draw_game(WIN, player, ball, computer, score1, score2)
                    begin = start_box.wait_for_click()
                    run = True
                    score1 = 0
                    score2 = 0
            except Exception as err:
                run = False

main()

pygame.quit()
quit()


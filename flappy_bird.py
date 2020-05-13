#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library
import os
import random
import time

# 3rd party libraries
import pygame
import neat

# Local modules

# Global variables
WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730

pygame.font.init()  # init font
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

# Images used in the game
# Todo add .convert_alpha()
bg_img = pygame.image.load(os.path.join("imgs", "bg.png"))
bg_img = pygame.transform.scale(bg_img, (600, 900))

base_img = pygame.image.load(os.path.join("imgs", "base.png"))
base_img = pygame.transform.scale2x(base_img)

pipe_img = pygame.image.load(os.path.join("imgs", "pipe.png"))
pipe_img = pygame.transform.scale2x(pipe_img)

bird_imgs = []
for i in range(1, 4):
    path = os.path.join("imgs", "bird" + str(i) + ".png")
    bird_img = pygame.image.load(path)
    bird_img = pygame.transform.scale2x(bird_img)
    bird_imgs.append(bird_img)


class Bird():
    IMGS = bird_imgs
    MAX_ROTATION = 25  # How much the bird tilts
    ROT_VEL = 20  # How much the bird can rotate every frame
    ANIMATION_TIME = 5  # How long we show the flapping animation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # start flat
        self.tick_count = 0  # to figure out the physics
        self.vel = 0
        self.height = self.y
        self.img_count = 0  # to know the image we show
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5   # the velocity is negative  to go upward
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1  # How many time we move since the last hump

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        # jump higher
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:   # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2  # No frame skipped

        # tilt the bird
        blit_rotate_center(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False  # if the bird has already passed the pipe

        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  # move the pipe to the left

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if b_point or t_point:  # if they're not none
            return True
        else:
            return False


class Base():
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Move floor so it looks like its scrolling
        :return: None
        """
        # We use two images to fake movement
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # If the first image is off-screen,
        # we put it behind the second one
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blit_rotate_center(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_window(win, bird, pipes, base, score):
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    # score
    score_color = (255, 255, 255)
    score_label = STAT_FONT.render("Score: " + str(score), 1, score_color)
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    base.draw(win)
    bird.draw(win)
    pygame.display.update()


def main():
    base = Base(730)
    pipes = [Pipe(700)]
    bird = Bird(230, 350)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird, win):
                pass

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        # if we hit the ground
        if bird.y + bird.img.get_height() >= FLOOR:
            pass

        base.move()
        draw_window(win, bird, pipes, base, score)
    pygame.quit()
    quit()


main()

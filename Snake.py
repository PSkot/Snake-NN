import pygame
import random
pygame.init()

#Basic game info
name = "Snake"
screenWidth = 500
screenHeight = 500
score_margin = 60
border_size = 10
snakePos = [260, 260]
snakeSize = [20, 20]
candyRadius = 7
score = 0
font = pygame.font.SysFont('comicsans', 30, bold = True, italic = True)

win = pygame.display.set_mode((screenWidth, screenHeight + score_margin))
pygame.display.set_caption(name)
clock = pygame.time.Clock()

class snakePiece(object):
    def __init__(self, x, y, width, height, old_x, old_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.old_x = old_x
        self.old_y = old_y

    def draw(self, win):
        pygame.draw.rect(win, (255,255,255), (self.x, self.y, self.width, self.height))

    def hit(self):
        self.x = snakePos[0]
        self.y = snakePos[1]
        i = 0
        while i < 300:
            pygame.time.delay(10)
            i += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    i = 301
                    pygame.quit()


class candy_piece(object):
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, win):
        pygame.draw.circle(win, (255,255,255), (self.x, self.y), self.radius)

def redrawGameWindow():
    win.fill((0,0,0))
    pygame.draw.rect(win, (100, 0, 0), (0, 0 + score_margin, screenWidth, screenHeight))
    candy.draw(win)
    for i in range(len(snake)):
        snake[i].draw(win)
    text = font.render(str(score), 1, (255, 255, 255))
    win.blit(text, (450, 10))
    pygame.display.update()


#Main loop
run = True
snake = []
snake.append(snakePiece(snakePos[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
snake.append(snakePiece(snakePos[0]-snakeSize[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
snake.append(snakePiece(snakePos[0]-snakeSize[0]*2, snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
rand2 = random.randint(0, screenHeight//snakeSize[0]-1)*snakeSize[1]+snakeSize[1]//2 + score_margin

for i in range(len(snake)):
    while rand1*snakeSize[0] == snake[i].x+snakeSize[0]//2 and rand1*snakeSize[1] == snake[i].y+snakeSize[0]//2:
        rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
        rand2 = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0]+snakeSize[1]//2 + score_margin

candy = candy_piece(rand1, rand2, candyRadius)

horizontal = 1
vertical = 0
MovementLoop = 0
loseGame = False

while run:
    clock.tick(45)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    for i in range(len(snake)):
        snake[i].old_x = snake[i].x
        snake[i].old_y = snake[i].y

    MovementLoop += 1

    if MovementLoop > 1:
        MovementLoop = 0

    if MovementLoop == 0:

        if candy.x == snake[0].x + snakeSize[0]//2 and candy.y == snake[0].y + snakeSize[1]//2:
            snake.append(snakePiece(snake[len(snake)-1].x, snake[len(snake)-1].y, snakeSize[0], snakeSize[1], 0, 0))
            candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
            candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[1]+snakeSize[1]//2 + score_margin
            score += 1

        if len(snake) > 1:
            for i in range(1, len(snake)):
                snake[i].x = snake[i-1].old_x
                snake[i].y = snake[i-1].old_y

            while candy.x == snake[0].x+snakeSize[0]//2 and candy.y == snake[0].y+snakeSize[0]//2:
                candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
                candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0]+snakeSize[1]//2 + score_margin

        if (horizontal == 1 and snake[0].x + snake[0].width != screenWidth) or (horizontal == -1 and snake[0].x != 0):
            snake[0].x += snake[0].width * horizontal
        elif (vertical == 1 and snake[0].y + snake[0].height != screenHeight + score_margin) or (vertical == -1 and snake[0].y != score_margin):
            snake[0].y += snake[0].height * vertical

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT] and not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and horizontal == 0:
        horizontal = 1
        vertical = 0

    if keys[pygame.K_LEFT] and not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and horizontal == 0:
        horizontal = -1
        vertical = 0

    if keys[pygame.K_UP] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and vertical == 0:
        horizontal = 0
        vertical = -1

    if keys[pygame.K_DOWN] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and vertical == 0:
        horizontal = 0
        vertical = 1

    if len(snake) > 1:
        for i in range(len(snake)):
            for j in range(len(snake)):
                if i == j:
                    pass
                elif snake[i].x == snake[j].x and snake[i].y == snake[j].y:
                    snake[0].hit()
                    score = 0

                    snake = []
                    snake.append(snakePiece(snakePos[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
                    snake.append(snakePiece(snakePos[0]-snakeSize[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
                    snake.append(snakePiece(snakePos[0]-snakeSize[0]*2, snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
                    rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
                    rand2 = random.randint(0, screenHeight//snakeSize[0]-1)*snakeSize[1]+snakeSize[1]//2 + score_margin

                    while rand1*snakeSize[0] == snakePos[0]+snakeSize[0]//2 and rand1*snakeSize[1] == snakePos[1]+snakeSize[0]//2:
                        rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0]+snakeSize[0]//2
                        rand2 = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0]+snakeSize[1]//2 + score_margin

                    candy = candy_piece(rand1, rand2, candyRadius)

                    horizontal = 1
                    vertical = 0

                    loseGame = True

                    break

            else:
                continue

            break



    if loseGame == False:
        redrawGameWindow()

    loseGame = False

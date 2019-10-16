import pygame
import random
import neat
import os
import numpy as np
pygame.init()

#Basic game info
name = "Snake"
screenWidth = 800
screenHeight = 800
score_margin = 0
border_size = 10
snakePos = [400, 400]
snakeSize = [20, 20]
candyRadius = 7
font = pygame.font.SysFont('comicsans', 30, bold = True, italic = True)
#Array to store wall coordinates
wall_coords = []

for i in range(screenWidth//snakeSize[0]+1):
        wall_coords.append([i*snakeSize[0], score_margin])
        wall_coords.append([screenWidth, i*snakeSize[1]])
        wall_coords.append([0, snakeSize[1]*i])
        wall_coords.append([i*snakeSize[0], score_margin + screenHeight])

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
        while i < 1:
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


def draw_sight(win, vecs):
    for j in range(len(vecs)):
        for i in range(len(vecs[j])):
            if [vecs[j][i][0], vecs[j][i][1]] in wall_coords:
                pygame.draw.circle(win, (255, 255, 0), (vecs[j][i][0], vecs[j][i][1]), 5)
            else:
                pygame.draw.circle(win, (0, 255, 255), (vecs[j][i][0], vecs[j][i][1]), 1)

def calc_dist_wall(dist_vec, snake_x, snake_y, dist = 0):
    for i in range(len(dist_vec)):
        if [dist_vec[i][0], dist_vec[i][1]] in wall_coords:
            dist = ((dist_vec[i][0] - snake_x)**2 + (dist_vec[i][1] - snake_y)**2)**0.5

    return np.where(dist is None, 0, dist)

def calc_dist_candy(dist_vec, snake_x, snake_y, candy_x, candy_y, dist = 0, dir = 'other'):
        for i in range(len(dist_vec)):
            if [dist_vec[i][0], dist_vec[i][1]] == [candy_x, candy_y]:
                if dir == 'other':
                    dist = ((dist_vec[i][0] - snake_x)**2 + (dist_vec[i][1] - snake_y)**2)**0.5
                elif dir == 'left':
                    dist = snake_x - candy_x
                elif dir == 'right':
                    dist = candy_x - snake_x
                elif dir == 'up':
                    dist = snake_y - candy_y
                elif dir == 'down':
                    dist = candy_y - snake_y
                else:
                    print("Error in direction, please debug")
                    pygame.quit()

        return np.where(dist is None, 0, dist)

def calc_dist_tail(dist_vec, snake_body_coords, snake_x, snake_y, dist = 0, all_dists = []):
    all_dists.clear()
    for i in range(len(snake_body_coords)):
        if snake_body_coords[i] in dist_vec:
            all_dists.append(((snake_body_coords[i][0] - snake_x)**2 + (snake_body_coords[i][1] - snake_y)**2)**0.5)
        else:
            all_dists.append(1000)

    if all_dists == []:
        dist = 0
    else:
        dist = min(all_dists)
    return np.where(dist is 1000, 0, dist)

def s_dist(x, y, dir, mult, vector):
    if dir == 'up':
        vector.append([x, (y - snakeSize[0]*mult)])
    elif dir == 'down':
        vector.append([x, (y + snakeSize[0]*mult)])
    elif dir == 'left':
        vector.append([x - snakeSize[0]*mult, y])
    elif dir == 'right':
        vector.append([x + snakeSize[0]*mult, y])
    elif dir == 'upleft':
        vector.append([x-snakeSize[0]*mult, y-snakeSize[0]*mult])
    elif dir == 'upright':
        vector.append([x+snakeSize[0]*mult, y-snakeSize[0]*mult])
    elif dir == 'downleft':
        vector.append([x-snakeSize[0]*mult, y+snakeSize[0]*mult])
    elif dir == 'downright':
        vector.append([x+snakeSize[0]*mult, y+snakeSize[0]*mult])

def redrawGameWindow(win, snake, candy, score, vecs, moves):
    win.fill((0,0,0))
    pygame.draw.rect(win, (100, 0, 0), (0, 0 + score_margin, screenWidth, screenHeight))
    candy.draw(win)
    for i in range(len(snake)):
        snake[i].draw(win)
    draw_sight(win, vecs)
    moves_left = font.render(str(moves), 1, (255, 255, 255))
    text = font.render(str(score), 1, (255, 255, 255))
    win.blit(text, (screenWidth - 50, 10))
    win.blit(moves_left, (50, 10))
    pygame.display.update()



#Main loop
def main(genomes, config):

    #NET
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        snake = []
        appends = []
        candy_dist = [0,0,0,0,0,0,0,0]
        tail_dist = [0,0,0,0,0,0,0,0]
        g.fitness = 0

        #set positions and initiate snake
        snake.append(snakePiece(snakePos[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        # rand = random.randint(0,3)
        # if rand == 0:
        #     horizontal = 1
        #     vertical = 0
        #     snake.append(snakePiece(snakePos[0]-snakeSize[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        #     snake.append(snakePiece(snakePos[0]-snakeSize[0]*2, snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        # elif rand == 1:
        #     horizontal = -1
        #     vertical = 0
        #     snake.append(snakePiece(snakePos[0]+snakeSize[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        #     snake.append(snakePiece(snakePos[0]+snakeSize[0]*2, snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        # elif rand == 2:
        #     horizontal = 0
        #     vertical = 1
        #     snake.append(snakePiece(snakePos[0], snakePos[1]-snakeSize[0], snakeSize[0], snakeSize[1], 0, 0))
        #     snake.append(snakePiece(snakePos[0], snakePos[1]-snakeSize[0]*2, snakeSize[0], snakeSize[1], 0, 0))
        # else:
        #     horizontal = 0
        #     vertical = -1
        #     snake.append(snakePiece(snakePos[0], snakePos[1]+snakeSize[0], snakeSize[0], snakeSize[1], 0, 0))
        #     snake.append(snakePiece(snakePos[0], snakePos[1]+snakeSize[0]*2, snakeSize[0], snakeSize[1], 0, 0))


        horizontal = 1
        vertical = 0
        snake.append(snakePiece(snakePos[0]-snakeSize[0], snakePos[1], snakeSize[0], snakeSize[1], 0, 0))
        snake.append(snakePiece(snakePos[0]-snakeSize[0]*2, snakePos[1], snakeSize[0], snakeSize[1], 0, 0))

        #Initiate snake
        score = 0
        win = pygame.display.set_mode((screenWidth, screenHeight + score_margin))
        pygame.display.set_caption(name)
        clock = pygame.time.Clock()

        #Create candy
        rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] +snakeSize[0]//2
        rand2 = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin + snakeSize[1]//2

        for i in range(len(snake)):
            while rand1*snakeSize[0] == snake[i].x+snakeSize[0]//2 and rand1*snakeSize[1] == snake[i].y + snakeSize[0]//2:
                rand1 = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] + snakeSize[0]//2
                rand2 = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin + snakeSize[1]//2

        candy = candy_piece(rand1, rand2, candyRadius)

        #Initiate positions and game loop
        run = True
        snake_x = []
        snake_y = []
        inputs = []
        snake_coords = []
        movement = 200

        #Main loop
        while run:

            ### INPUT CALCULATIONS ###

            #Array to store snake coordinates
            snake_coords = []
            if len(snake) > 3:
                for i in range(3, len(snake)):
                    snake_coords.append([snake[i].x, snake[i].y])

            #Declare master distance vector
            vecs = []

            #Declare vision vectors
            up_vec = []
            down_vec = []
            left_vec = []
            right_vec = []
            upleft_vec = []
            upright_vec = []
            downleft_vec = []
            downright_vec = []

            for i in range(50):
                s_dist(snake[0].x, snake[0].y, 'left', i, left_vec)
                s_dist(snake[0].x, snake[0].y, 'right', i, right_vec)
                s_dist(snake[0].x, snake[0].y, 'down', i, down_vec)
                s_dist(snake[0].x, snake[0].y, 'up', i, up_vec)
                s_dist(snake[0].x, snake[0].y, 'upleft', i, upleft_vec)
                s_dist(snake[0].x, snake[0].y, 'upright', i, upright_vec)
                s_dist(snake[0].x, snake[0].y, 'downleft', i, downleft_vec)
                s_dist(snake[0].x, snake[0].y, 'downright', i, downright_vec)

            vecs.append(left_vec)
            vecs.append(right_vec)
            vecs.append(up_vec)
            vecs.append(down_vec)
            vecs.append(upleft_vec)
            vecs.append(upright_vec)
            vecs.append(downleft_vec)
            vecs.append(downright_vec)

            #Distances to wall
            left_dist_wall = snake[0].x
            right_dist_wall = screenWidth - snake[0].x
            down_dist_wall = screenHeight + score_margin - snake[0].y
            up_dist_wall = snake[0].y - score_margin
            upleft_dist_wall = calc_dist_wall(upleft_vec, snake[0].x, snake[0].y)
            upright_dist_wall = calc_dist_wall(upright_vec, snake[0].x, snake[0].y)
            downleft_dist_wall = calc_dist_wall(downleft_vec, snake[0].x, snake[0].y)
            downright_dist_wall = calc_dist_wall(downright_vec, snake[0].x, snake[0].y)

            #print(snake_coords[:][2:3])

            tail_dist[0] = calc_dist_tail(left_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[1] = calc_dist_tail(right_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[2] = calc_dist_tail(down_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[3] = calc_dist_tail(up_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[4] = calc_dist_tail(upleft_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[5] = calc_dist_tail(upright_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[6] = calc_dist_tail(downleft_vec, snake_coords, snake[0].x, snake[0].y)
            tail_dist[7] = calc_dist_tail(downright_vec, snake_coords, snake[0].x, snake[0].y)

            #Distances to candy
            candy_dist[0] = calc_dist_candy(left_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'left') #left
            candy_dist[1] = calc_dist_candy(right_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'right') #right
            candy_dist[2] = calc_dist_candy(up_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'up') #up
            candy_dist[3] = calc_dist_candy(down_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'down') #down
            candy_dist[4] = calc_dist_candy(upleft_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'other') #upleft
            candy_dist[5] = calc_dist_candy(upright_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'other') #upright
            candy_dist[6] = calc_dist_candy(downleft_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'other') #downleft
            candy_dist[7] = calc_dist_candy(downright_vec, snake[0].x, snake[0].y, candy.x - snakeSize[0]//2, candy.y - snakeSize[1]//2, dir = 'other') #downright

            #GAME STARTS
            #clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

            for i in range(len(snake)):
                snake[i].old_x = snake[i].x
                snake[i].old_y = snake[i].y

            output = net.activate([left_dist_wall, right_dist_wall, down_dist_wall, up_dist_wall, upleft_dist_wall,
            upright_dist_wall,downleft_dist_wall,downright_dist_wall,
            candy_dist[0],candy_dist[1],candy_dist[2],candy_dist[3],candy_dist[4],candy_dist[5],candy_dist[6],candy_dist[7],
            tail_dist[0],tail_dist[1],tail_dist[2],tail_dist[3],tail_dist[4],tail_dist[5],tail_dist[6],tail_dist[7]])
            index_max = np.argmax(output)

            if index_max == 0 and horizontal == 0:
                horizontal = 1
                vertical = 0
            elif index_max == 1 and vertical == 0:
                vertical = -1
                horizontal = 0
            elif index_max == 2 and horizontal == 0:
                horizontal = -1
                vertical = 0
            elif index_max == 3 and vertical == 0:
                vertical = 1
                horizontal = 0

            #MANUAL CONTROLS
            # keys = pygame.key.get_pressed()
            #
            # if keys[pygame.K_RIGHT] and not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and horizontal == 0:
            #     horizontal = 1
            #     vertical = 0
            #
            # if keys[pygame.K_LEFT] and not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and horizontal == 0:
            #     horizontal = -1
            #     vertical = 0
            #
            # if keys[pygame.K_UP] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and vertical == 0:
            #     horizontal = 0
            #     vertical = -1
            #
            # if keys[pygame.K_DOWN] and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and vertical == 0:
            #     horizontal = 0
            #     vertical = 1


            for i in range(len(appends)):
                if appends[i] > 0:
                    appends[i] -= 1
                else:
                    snake.append(snakePiece(snake[len(snake)-1].x, snake[len(snake)-1].y, snakeSize[0], snakeSize[1], 0, 0))
                    appends.pop()

            if len(snake) > 1:
                for i in range(1, len(snake)):
                    if i == 1:
                        if (horizontal == 1 and snake[0].x + snake[0].width != screenWidth) or (horizontal == -1 and snake[0].x != 0):
                            snake[0].x += snake[0].width * horizontal
                        elif (vertical == 1 and snake[0].y + snake[0].height != screenHeight + score_margin) or (vertical == -1 and snake[0].y != score_margin):
                            snake[0].y += snake[0].height * vertical

                    snake[i].x = snake[i-1].old_x
                    snake[i].y = snake[i-1].old_y

                    while candy.x == snake[i].x+snakeSize[0]//2 and candy.y == snake[i].y+snakeSize[0]//2:
                        candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] + snakeSize[0]//2
                        candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin +snakeSize[1]//2

            if ((snake[0].old_x + snake[0].width//2 - candy.x)**2 + (snake[0].old_y + snake[0].height//2 - candy.y)**2)**0.5 < ((snake[0].x + snake[0].width//2 - candy.x)**2 + (snake[0].y + snake[0].height//2 - candy.y)**2)**0.5:
                g.fitness -= 1
            if ((snake[0].old_x - candy.x)**2 + (snake[0].old_y - candy.y)**2)**0.5 > ((snake[0].x - candy.x)**2 + (snake[0].y - candy.y)**2)**0.5:
                g.fitness += 0.5
            else:
                pass

            if candy_dist[0] == 20 and horizontal == -1:
                score += 1
                movement += 100
                g.fitness += 50
                candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] +snakeSize[0]//2
                candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin +snakeSize[1]//2
                appends.insert(0, len(snake)-1)

            elif candy_dist[1] == 20 and horizontal == 1:
                score += 1
                movement += 100
                g.fitness += 50
                candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] +snakeSize[0]//2
                candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin +snakeSize[1]//2
                appends.insert(0, len(snake)-1)

            elif candy_dist[2] == 20 and vertical == -1:
                score += 1
                movement += 100
                g.fitness += 50
                candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] +snakeSize[0]//2
                candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin +snakeSize[1]//2
                appends.insert(0, len(snake)-1)

            elif candy_dist[3] == 20 and vertical == 1:
                score += 1
                movement += 100
                g.fitness += 50
                candy.x = random.randint(0, screenWidth//snakeSize[0]-1)*snakeSize[0] +snakeSize[0]//2
                candy.y = random.randint(0, screenHeight//snakeSize[1]-1)*snakeSize[0] + score_margin +snakeSize[1]//2
                appends.insert(0, len(snake)-1)

            else:
                pass

            movement -= 1
            if movement == 0:
                print("Out of moves")
                run = False

            if len(snake) > 1:
                for i in range(len(snake)):
                    for j in range(len(snake)):
                        if i == j:
                            pass
                        elif snake[i].x == snake[j].x and snake[i].y == snake[j].y:
                            g.fitness -= 50
                            run = False
                            break

                    else:
                        continue

                    break

            if run == True:
                redrawGameWindow(win, snake, candy, score, vecs, movement)
                g.fitness += 0.5
                # if g.fitness != 0:
                #     print(g.fitness)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 10000)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

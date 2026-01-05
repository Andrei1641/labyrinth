import pygame
from collections import deque
from pygame import KEYDOWN
import  random

WIDTH, HEIGHT = 500, 500
WALLS_WIDTH = 5
FPS = 30

BG_COLOR = (0, 0, 0)
PLAYER_SIZE = 5
PLAYER_COLOR = (255, 255, 0)
WALLS_COLOR = (220, 0, 0)
START_COLOR = (0, 255, 0)
FINISH_COLOR = (0, 0, 255)
SIZE = 50

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((SIZE - PLAYER_SIZE * 2, SIZE - PLAYER_SIZE * 2))
        self.rect = pygame.Rect(pos[0], pos[1], SIZE, SIZE)
        x,y = self.rect.topleft
        self.coordinates = (x // SIZE, y // SIZE)

        margin = PLAYER_SIZE
        width_height = SIZE - PLAYER_SIZE * 2
        rect_params = (margin, margin, width_height, width_height)

        pygame.draw.rect(self.image, PLAYER_COLOR, rect_params)

    def update(self):
        x,y = self.rect.topleft
        self.coordinates = (x // SIZE, y // SIZE)

class Field(pygame.sprite.Sprite):
    def __init__(self, pos, walls):
        super().__init__()
        self.image = pygame.Surface((SIZE, SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.wall = walls       #right and lower wall
    def update(self):
        if self.wall[0] == 1:
            pygame.draw.rect(self.image, WALLS_COLOR, (SIZE - WALLS_WIDTH, 0, WALLS_WIDTH, SIZE))
        else:
            pass
        if self.wall[1] == 1:
            pygame.draw.rect(self.image, WALLS_COLOR, (0, SIZE - WALLS_WIDTH, SIZE, WALLS_WIDTH))
        else:
            pass

def search(groups, flor, current_sell, number_of_sells):
    counter = 0
    for j in groups:
        if (flor - 1) * number_of_sells + current_sell in j:
            return counter
        counter += 1
    return None

def first_stage_change(flor, number_of_sells, groups, field_walls):
    for i in range(number_of_sells - 1):
        rand_change = random.randint(0,1)

        print(rand_change)
        if rand_change:
            field_walls[flor - 1][i] = (1, 0)
        else:
            lst1 = search(groups, flor, i, number_of_sells)
            lst2 = search(groups, flor, i + 1, number_of_sells)
            if lst1 != lst2:
                if lst1 > lst2:
                    lst1, lst2 = lst2, lst1
                if len(groups) >= 1:
                    groups[lst1] = groups[lst1] + groups[lst2]
                    del groups[lst2]
#right border
        field_walls[flor - 1][number_of_sells - 1] = (1, 0)

def if_at_least_one_sell_has_low_wall(groups, flor, number_of_sells, field_walls, current_cell):
    lst = search(groups, flor, current_cell, number_of_sells)
    group_on_flor = []
    c = 0
    for j in groups[lst]:
        if j in range((flor - 1) * number_of_sells, (flor - 1) * number_of_sells + number_of_sells):
            group_on_flor.append(j)

    for i in group_on_flor:
        needed_flor = i // number_of_sells
        needed_sell = i % number_of_sells
        a, b = field_walls[needed_flor][needed_sell]
        if b == 0:
            c += 1
        if c == 2:
            return True
    return False

def second_stage_change(number_of_sells, groups, flor, field_walls):
    for i in range(number_of_sells):
        rand_change = random.randint(0, 1)
        print(rand_change)
        if rand_change:
            low_wall = if_at_least_one_sell_has_low_wall(groups, flor, number_of_sells, field_walls, i)
            if low_wall:
                a,b = field_walls[flor - 1][i]
                field_walls[flor - 1][i] = (a, 1)

def next_flor(number_of_sells, field_walls, flor, groups):
    for i in range(number_of_sells):
        a, b = field_walls[flor - 1][i]
        if b != 1:
            for j in groups:
                if (flor - 1) * number_of_sells + i in j:
                    j.append(number_of_sells * flor + i)
        else:
            groups.append([number_of_sells * flor + i])
    flor += 1
    return flor

def grid_ini(number_of_sells):
#first flor
    groups = [[n] for n in range(number_of_sells)]
    field_walls = [[(0, 0) for _ in range(number_of_sells)] for _ in range(number_of_sells)]

    flor = 1
    first_stage_change(flor, number_of_sells, groups, field_walls)
    second_stage_change(number_of_sells, groups, flor, field_walls)

#body of the labyrinth
    for _ in range(1, number_of_sells - 1):
        flor = next_flor(number_of_sells, field_walls, flor, groups)
        first_stage_change(flor, number_of_sells, groups, field_walls)
        second_stage_change(number_of_sells, groups, flor, field_walls)

#last flor
    for i in range(number_of_sells - 1):
        field_walls[flor][i] = (0,1)
    field_walls[flor][number_of_sells - 1] = (1,1)

    print(groups)
    return field_walls

def field_init(number_of_sells, grid, fields_arr):
    for i in range(number_of_sells):
        for j in range(number_of_sells):
            fields_arr.append(Field((j * SIZE, i * SIZE), grid[i][j]))

def border_check(axis):
    if axis < 1:
        return 1
    return 0

def gathering_of_all_sides_of_the_field(grid, cur_field):
    x,y = cur_field
    if x > len(grid) - 1 or y > len(grid) - 1 or x < 0 or y < 0:
        a, b, c, d = -1, -1, -1, -1
    else:
        a, b = grid[y][x]
        c = border_check(x)
        d = border_check(y)
        if not c:
            c, _ = grid[y][x - 1]
        if not d:
            _, d = grid[y - 1][x]

    return a, b, c, d


def movement(event, player, a, b, c, d):
    if event.key == pygame.K_LEFT and c == 0:
        player.rect.x -= SIZE
    if event.key == pygame.K_RIGHT and a == 0:
        player.rect.x += SIZE
    if event.key == pygame.K_DOWN and b == 0:
        player.rect.y += SIZE
    if event.key == pygame.K_UP and d == 0:
        player.rect.y -= SIZE

def reconstruct_path(parent, end):
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]

def bfs_path_matrix(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    visited = set([start])
    parent = {start: None}
    while queue:
        r, l = queue.popleft()
        directions = []
        a, b, c, d = gathering_of_all_sides_of_the_field(grid, (r, l))
        if a == 0:
            directions.append((1, 0))
        if b == 0:
            directions.append((0, 1))
        if c == 0:
            directions.append((-1, 0))
        if d == 0:
            directions.append((0, -1))

        if (r, l) == end:
            return reconstruct_path(parent, end)
        for dr, dc in directions:
            nr, nc = r + dr, l + dc
            if (0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited):
                visited.add((nr, nc))
                parent[(nr, nc)] = (r, l)
                queue.append((nr, nc))
    return None

def autom_move_player(path_index, path, move_timer, player):
    current_time = pygame.time.get_ticks()
    if path_index < len(path):
        if current_time - move_timer > 500:
            move_timer = current_time
            x, y = path[path_index]
            player.rect.topleft = (x * SIZE, y * SIZE)
            path_index += 1
    return path_index, move_timer

def main():
    grid = [[]]
    fields_arr = []
    number_of_sells = 7
    move_timer = 0
    path_index = 0
    path = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Labyrinth")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    grid = grid_ini(number_of_sells)
    print(grid)

    field_init(number_of_sells, grid, fields_arr)

    all_sprites.add(fields_arr)

    player = Player((0, 0))
    all_sprites.add(player)

    running = True
    while running:

# keyboard input + collision

        a,b,c,d = gathering_of_all_sides_of_the_field(grid, player.coordinates)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                movement(event, player, a, b, c, d)
                if event.key == pygame.K_h:
                    path_index = 0
                    path = bfs_path_matrix(grid, player.coordinates, (6,0))
                    move_timer = pygame.time.get_ticks()
                    print(path)


        path_index, move_timer = autom_move_player(path_index, path, move_timer, player)

# rendering
        all_sprites.update()
        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
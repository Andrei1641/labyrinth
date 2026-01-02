import pygame
from collections import deque

from pygame import KEYDOWN

WIDTH, HEIGHT = 500, 500
BORDER_WIDTH = 5
FPS = 30

BG_COLOR = (0, 0, 0)
PLAYER_COLOR = (255, 255, 0)
FIELD_COLOR = (220, 0, 0)
START_COLOR = (0, 255, 0)
FINISH_COLOR = (0, 0, 255)
SIZE = 50

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((SIZE, SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=pos)
        self.old_pos = (0, 0)
    def update(self):
        pass

class Field(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((SIZE, SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

def feld_ini(fields_arr, untouchable_fs, field_state, y_pos, x_pos):
    if field_state == 1:
        fields_arr.append(Field((SIZE * y_pos + BORDER_WIDTH, SIZE * x_pos + BORDER_WIDTH), FIELD_COLOR))
    elif field_state == "S":
        untouchable_fs.append(Field((SIZE * y_pos + BORDER_WIDTH, SIZE * x_pos + BORDER_WIDTH), START_COLOR))
    elif field_state == "F":
        untouchable_fs.append(Field((SIZE * y_pos + BORDER_WIDTH, SIZE * x_pos + BORDER_WIDTH), FINISH_COLOR))

def fields_ini(grid, fields_arr, untouchable_fs):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            field_state = grid[i][j]
            if field_state:
                feld_ini(fields_arr, untouchable_fs, field_state, j, i)


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
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    while queue:
        r,c = queue.popleft()
        if (r, c) == end:
            return reconstruct_path(parent, end)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (grid[nr][nc] == 0 or grid[nr][nc] == "S" or grid[nr][nc] == "F" )and (nr, nc) not in visited:
                visited.add((nr, nc))
                parent[(nr, nc)] = (r,c)
                queue.append((nr, nc))
    return None

def movement(event, player):
    if event.key == pygame.K_LEFT:
        player.old_pos = player.rect.topleft
        player.rect.x -= SIZE
    if event.key == pygame.K_RIGHT:
        player.old_pos = player.rect.topleft
        player.rect.x += SIZE
    if event.key == pygame.K_DOWN:
        player.old_pos = player.rect.topleft
        player.rect.y += SIZE
    if event.key == pygame.K_UP:
        player.old_pos = player.rect.topleft
        player.rect.y -= SIZE

def shortest_path_calculation(player, grid):
    y, x = player.rect.topleft
    cur_pos = (x // SIZE, y // SIZE)
    path = bfs_path_matrix(grid, cur_pos, (3, 5))
    print(path)
    return path

def autom_move_player(path_index, path, move_timer, player):
    current_time = pygame.time.get_ticks()
    if path_index < len(path):
        if current_time - move_timer > 500:
            move_timer = current_time
            y, x = path[path_index]
            player.rect.topleft = (x * SIZE + BORDER_WIDTH, y * SIZE + BORDER_WIDTH)
            path_index += 1
    return path_index, move_timer

def main():
    grid = [
      ["S", 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1],
        [0, 0, 0, 1, 1, "F"],
        [0, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1]
    ]

    path = []
    fields_arr = []
    untouchable_fs = []
    end = len(grid[0]) * SIZE + BORDER_WIDTH
    move_timer = 0
    path_index = 0

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Labyrinth")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    fields_ini(grid, fields_arr, untouchable_fs)
    all_sprites.add(fields_arr)
    all_sprites.add(untouchable_fs)
    player = Player((BORDER_WIDTH, BORDER_WIDTH))
    all_sprites.add(player)

    running = True
    while running:

#keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                movement(event, player)
                if event.key == pygame.K_h:
                    path_index = 0
                    path = shortest_path_calculation(player, grid)
                    move_timer = pygame.time.get_ticks()

        path_index, move_timer = autom_move_player(path_index, path, move_timer, player)

#collision
        hit = player.rect.collidelist([f.rect for f in fields_arr])
        if hit != -1 or player.rect.x < 0 or player.rect.x >= end or player.rect.y < 0 or player.rect.y >= end :
            player.rect.topleft = player.old_pos

#rendering
        all_sprites.update()
        screen.fill(BG_COLOR)
        all_sprites.draw(screen)
        pygame.draw.rect(screen, FIELD_COLOR, (0, 0, end + BORDER_WIDTH, end + BORDER_WIDTH), BORDER_WIDTH)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()

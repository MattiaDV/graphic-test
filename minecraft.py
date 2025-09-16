from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import numpy as np
import random

app = Ursina()
window.fullscreen = True

# -------------------- CONFIG --------------------
CHUNK_SIZE = 16
RENDER_DISTANCE = 2
BASE_HEIGHT = 20
MAX_HEIGHT = 40  # altezza massima assoluta per non crashare

loaded_chunks = {}
chunk_blocks = {}  # (chunk_x, chunk_z) -> dizionario blocchi

# -------------------- FUNZIONI --------------------
def terrain_noise(x, z):
    """Combinazione di rumori per colline, montagne e avvallamenti"""
    mountains = (np.sin(x * 0.01) + np.cos(z * 0.01)) * 15
    hills = (np.sin(x * 0.05) + np.cos(z * 0.05)) * 5
    detail = (np.sin(x * 0.15) * np.cos(z * 0.15)) * 2
    valleys = -abs(np.sin(x * 0.02) * np.cos(z * 0.02)) * 10
    return int(mountains + hills + detail + valleys)

def get_top_height(world_x, world_z):
    """Altezza uniforme per tutto il mondo senza pianure speciali"""
    height = BASE_HEIGHT + terrain_noise(world_x, world_z)
    return int(height)

def generate_chunk(chunk_x, chunk_z):
    chunk = Entity()
    blocks_in_chunk = {}

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            top_height = get_top_height(world_x, world_z)
            top_height = min(top_height, MAX_HEIGHT)

            # Riempimento fino all'altezza top_height
            for y in range(top_height + 1):
                visible = (y == top_height)
                if visible:
                    Entity(parent=chunk, model='cube', texture='terra.jpg',
                           collider='box', position=(world_x, y, world_z))
                blocks_in_chunk[(world_x, y, world_z)] = True

    chunk_blocks[(chunk_x, chunk_z)] = blocks_in_chunk
    return chunk

def reveal_adjacent_blocks(pos):
    x0, y0, z0 = int(pos.x), int(pos.y), int(pos.z)
    for dx, dz, dy in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
        x = x0 + dx
        y = y0 + dy
        z = z0 + dz
        cx = x // CHUNK_SIZE
        cz = z // CHUNK_SIZE
        if (cx, cz) in chunk_blocks and (x,y,z) not in chunk_blocks[(cx, cz)]:
            top_height = get_top_height(x, z)
            if y <= min(top_height, MAX_HEIGHT):
                Entity(parent=loaded_chunks[(cx, cz)], model='cube', texture='terra.jpg',
                       collider='box', position=(x,y,z))
                chunk_blocks[(cx, cz)][(x,y,z)] = True

def update_chunks(player_position):
    player_chunk_x = int(player_position[0] // CHUNK_SIZE)
    player_chunk_z = int(player_position[2] // CHUNK_SIZE)

    # genera nuovi chunk
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            coord = (player_chunk_x + dx, player_chunk_z + dz)
            if coord not in loaded_chunks:
                loaded_chunks[coord] = generate_chunk(*coord)

    # rimuovi chunk lontani
    to_remove = []
    for coord in list(loaded_chunks.keys()):
        if abs(coord[0] - player_chunk_x) > RENDER_DISTANCE or abs(coord[1] - player_chunk_z) > RENDER_DISTANCE:
            loaded_chunks[coord].disable()
            to_remove.append(coord)
    for coord in to_remove:
        del loaded_chunks[coord]
        del chunk_blocks[coord]

# -------------------- GENERA CHUNK INIZIALI --------------------
# Generiamo uno spazio iniziale 3x3 di chunk per avere blocchi disponibili allo spawn
for cx in range(-1,2):
    for cz in range(-1,2):
        loaded_chunks[(cx, cz)] = generate_chunk(cx, cz)

# scegli spawn tra i blocchi iniziali
all_blocks = []
for blocks in chunk_blocks.values():
    all_blocks.extend([pos for pos,val in blocks.items() if val])
spawn_block = random.choice(all_blocks)
spawn_x, spawn_y, spawn_z = spawn_block[0], spawn_block[1] + 30, spawn_block[2]

player = FirstPersonController()
player.gravity = 1
player.position = (spawn_x, spawn_y, spawn_z)

# -------------------- UPDATE & INPUT --------------------
def update():
    update_chunks(player.position)
    if player.y < -1:
        # respawn se cade
        spawn_block = random.choice(all_blocks)
        player.position = (spawn_block[0], spawn_block[1] + 30, spawn_block[2])
        player.gravity = 1

def input(key):
    if key == "escape":
        application.quit()

    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit and hit_info.entity.position.y > 0:
            destroyed_position = hit_info.entity.position
            destroy(hit_info.entity)
            reveal_adjacent_blocks(destroyed_position)

    if key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit:
            new_block_position = hit_info.entity.position + hit_info.normal
            cx, cz = int(new_block_position.x // CHUNK_SIZE), int(new_block_position.z // CHUNK_SIZE)
            if (cx, cz) in chunk_blocks:
                Entity(model='cube', texture='terra.jpg', collider='box',
                       position=new_block_position)
                chunk_blocks[(cx, cz)][tuple(new_block_position)] = True

# -------------------- SKY & RUN --------------------
Sky()
app.run()

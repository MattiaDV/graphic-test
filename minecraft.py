from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import numpy as np
import random

app = Ursina()
window.fullscreen = True

# -------------------- CONFIG --------------------
CHUNK_SIZE = 16
RENDER_DISTANCE = 1
BASE_HEIGHT = 20
MAX_HEIGHT = 40

loaded_chunks = {}
chunk_blocks = {}  # (chunk_x, chunk_z) -> {(x,y,z): visible_bool}

# -------------------- FUNZIONI --------------------
def terrain_noise(x, z):
    mountains = (np.sin(x*0.01)+np.cos(z*0.01))*15
    hills = (np.sin(x*0.05)+np.cos(z*0.05))*5
    detail = (np.sin(x*0.15)*np.cos(z*0.15))*2
    valleys = -abs(np.sin(x*0.02)*np.cos(z*0.02))*10
    return int(mountains+hills+detail+valleys)

def get_top_height(x, z):
    return int(BASE_HEIGHT + terrain_noise(x, z))

def generate_chunk(chunk_x, chunk_z):
    chunk = Entity()
    blocks_in_chunk = {}

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = chunk_x*CHUNK_SIZE + x
            world_z = chunk_z*CHUNK_SIZE + z
            top_height = min(get_top_height(world_x, world_z), MAX_HEIGHT)

            # blocchi “logici”, invisibili inizialmente
            for y in range(top_height+1):
                blocks_in_chunk[(world_x, y, world_z)] = False

            # crea entità solo per la superficie
            e = Entity(parent=chunk, model='cube', texture='terra.jpg',
                       collider='box', position=(world_x, top_height, world_z))
            blocks_in_chunk[(world_x, top_height, world_z)] = True

    chunk_blocks[(chunk_x, chunk_z)] = blocks_in_chunk
    return chunk

def reveal_block(cx, cz, key):
    """Genera entità solo se non visibile"""
    if not chunk_blocks[(cx, cz)][key]:
        x, y, z = key
        Entity(parent=loaded_chunks[(cx, cz)],
               model='cube', texture='terra.jpg', collider='box',
               position=(x, y, z))
        chunk_blocks[(cx, cz)][key] = True

def reveal_adjacent_blocks(pos):
    """Rivela solo blocchi adiacenti esposti, senza ricreare quelli distrutti."""
    x0, y0, z0 = int(pos.x), int(pos.y), int(pos.z)
    directions = [(0,-1,0), (-1,0,0), (1,0,0), (0,0,-1), (0,0,1), (0,1,0)]
    
    cx, cz = x0 // CHUNK_SIZE, z0 // CHUNK_SIZE
    if (cx, cz) not in chunk_blocks:
        return

    revealed_count = 0
    for dx, dy, dz in directions:
        if revealed_count >= 6:
            break
        nx, ny, nz = x0+dx, y0+dy, z0+dz
        key = (nx, ny, nz)
        # rivela solo se non visibile e non distrutto
        if key in chunk_blocks[(cx, cz)] and chunk_blocks[(cx, cz)][key] is False:
            Entity(parent=loaded_chunks[(cx, cz)], model='cube',
                   texture='terra.jpg', collider='box', position=(nx, ny, nz))
            chunk_blocks[(cx, cz)][key] = True
            revealed_count += 1

def update_chunks(player_pos):
    player_chunk_x = int(player_pos[0]//CHUNK_SIZE)
    player_chunk_z = int(player_pos[2]//CHUNK_SIZE)

    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            coord = (player_chunk_x+dx, player_chunk_z+dz)
            if coord not in loaded_chunks:
                loaded_chunks[coord] = generate_chunk(*coord)

    # rimuovi chunk lontani
    to_remove = []
    for coord in list(loaded_chunks.keys()):
        if abs(coord[0]-player_chunk_x)>RENDER_DISTANCE or abs(coord[1]-player_chunk_z)>RENDER_DISTANCE:
            loaded_chunks[coord].disable()
            to_remove.append(coord)
    for coord in to_remove:
        del loaded_chunks[coord]
        del chunk_blocks[coord]

# -------------------- GENERA CHUNK INIZIALI --------------------
for cx in range(-1,2):
    for cz in range(-1,2):
        loaded_chunks[(cx, cz)] = generate_chunk(cx, cz)

all_blocks = [pos for blocks in chunk_blocks.values() for pos,val in blocks.items() if val]
spawn_block = random.choice(all_blocks)
spawn_x, spawn_y, spawn_z = spawn_block[0], spawn_block[1]+50, spawn_block[2]

player = FirstPersonController()
player.gravity = 1
player.position = (spawn_x, spawn_y, spawn_z)

# -------------------- UPDATE & INPUT --------------------
def update():
    update_chunks(player.position)
    if player.y < -1:
        spawn_block = random.choice(all_blocks)
        player.position = (spawn_block[0], spawn_block[1]+50, spawn_block[2])
        player.gravity = 1

def input(key):
    if key=="escape":
        application.quit()

    if key=='left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit and hit_info.entity.position.y>0:
            destroyed_position = hit_info.entity.position
            destroy(hit_info.entity)
            
            # segna il blocco come distrutto
            cx, cz = int(destroyed_position.x // CHUNK_SIZE), int(destroyed_position.z // CHUNK_SIZE)
            chunk_blocks[(cx, cz)][tuple(destroyed_position)] = None
            
            # rivela blocchi adiacenti esposti
            reveal_adjacent_blocks(destroyed_position)

    if key=='right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit:
            new_pos = hit_info.entity.position + hit_info.normal
            cx, cz = int(new_pos.x//CHUNK_SIZE), int(new_pos.z//CHUNK_SIZE)
            if (cx, cz) in chunk_blocks:
                Entity(model='cube', texture='terra.jpg', collider='box', position=new_pos)
                chunk_blocks[(cx, cz)][tuple(new_pos)] = True

Sky()
app.run()

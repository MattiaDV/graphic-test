from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import numpy as np

app = Ursina()
window.fullscreen = True

# -------------------- CONFIG --------------------
CHUNK_SIZE = 16
RENDER_DISTANCE = 1
BASE_HEIGHT = 20
HEIGHT_VARIATION = 5
MAX_DISTANCE_FOR_TRANSITION = 5  # fino a che distanza dalla pianura inizia il noise completo

loaded_chunks = {}
chunk_blocks = {}  # (x,y,z) -> True=visibile, None=nascosto

# -------------------- FUNZIONI --------------------
def simple_noise(x, z):
    """Rumore leggero per colline"""
    return int(np.sin(x*0.1) + np.cos(z*0.1) * HEIGHT_VARIATION)

def get_top_height(chunk_x, chunk_z, world_x, world_z):
    """Calcola l'altezza top con transizione liscia dalla pianura al noise"""
    dist = max(abs(chunk_x), abs(chunk_z))
    
    # chunk centrali 3x3: pianura leggermente più bassa
    if dist <= 1:
        return BASE_HEIGHT - 1  # <-- qui scende di 1 blocco
    
    # transizione graduale
    elif dist <= MAX_DISTANCE_FOR_TRANSITION:
        t = (dist - 1) / (MAX_DISTANCE_FOR_TRANSITION - 1)
        noise_height = BASE_HEIGHT + simple_noise(world_x, world_z)
        return int(BASE_HEIGHT * (1 - t) + noise_height * t)
    
    # chunk lontani: rumore pieno
    else:
        return BASE_HEIGHT + simple_noise(world_x, world_z)

def generate_chunk(chunk_x, chunk_z):
    chunk = Entity()
    blocks_in_chunk = {}

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            top_height = get_top_height(chunk_x, chunk_z, world_x, world_z)

            # blocchi nascosti
            for y in range(top_height + 1):
                blocks_in_chunk[(world_x, y, world_z)] = None

            # rendi visibili quelli esposti
            for y in range(top_height + 1):
                visible = (y == top_height)
                if not visible:
                    for dx,dz,dy in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,1),(0,0,-1)]:
                        neighbor_top = get_top_height(chunk_x, chunk_z, world_x+dx, world_z+dz)
                        neighbor_y = y+dy
                        if neighbor_y > neighbor_top:
                            visible = True
                            break
                if visible:
                    Entity(parent=chunk, model='cube', texture='terra.jpg', collider='box', position=(world_x, y, world_z))
                    blocks_in_chunk[(world_x, y, world_z)] = True

    chunk_blocks[(chunk_x, chunk_z)] = blocks_in_chunk
    return chunk

def reveal_adjacent_blocks(pos):
    x0, y0, z0 = int(pos.x), int(pos.y), int(pos.z)
    for dx,dz,dy in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
        x = x0 + dx
        y = y0 + dy
        z = z0 + dz
        cx = x // CHUNK_SIZE
        cz = z // CHUNK_SIZE
        if (cx, cz) in chunk_blocks and chunk_blocks[(cx, cz)].get((x,y,z)) is None:
            top_height = get_top_height(cx, cz, x, z)
            if y <= top_height:
                Entity(parent=loaded_chunks[(cx, cz)], model='cube', texture='terra.jpg', collider='box', position=(x,y,z))
                chunk_blocks[(cx, cz)][(x,y,z)] = True

def update_chunks(player_position):
    player_chunk_x = int(player_position[0] // CHUNK_SIZE)
    player_chunk_z = int(player_position[2] // CHUNK_SIZE)

    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            coord = (player_chunk_x + dx, player_chunk_z + dz)
            if coord not in loaded_chunks:
                loaded_chunks[coord] = generate_chunk(*coord)

    to_remove = []
    for coord in loaded_chunks:
        if abs(coord[0] - player_chunk_x) > RENDER_DISTANCE or abs(coord[1] - player_chunk_z) > RENDER_DISTANCE:
            loaded_chunks[coord].disable()
            to_remove.append(coord)
    for coord in to_remove:
        del loaded_chunks[coord]
        del chunk_blocks[coord]

# -------------------- SPAWN PLAYER --------------------
spawn_x, spawn_z = 0, 0
initial_chunk = generate_chunk(0, 0)
loaded_chunks[(0,0)] = initial_chunk

# spawn sopra la pianura centrale
max_y = max([pos[1] for pos,val in chunk_blocks[(0,0)].items() if val])
spawn_y = max_y + 30
player = FirstPersonController()
player.gravity = 1
player.position = (spawn_x, spawn_y, spawn_z)

# -------------------- UPDATE & INPUT --------------------
def update():
    update_chunks(player.position)

def input(key):
    if key == "escape":
        application.quit()

    # distruggi blocco
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit and hit_info.entity.position.y > 0:
            destroyed_position = hit_info.entity.position
            destroy(hit_info.entity)
            reveal_adjacent_blocks(destroyed_position)

    # piazza blocco anche dove spaccato
    if key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[player])
        if hit_info.hit:
            new_block_position = hit_info.entity.position + hit_info.normal
            cx, cz = int(new_block_position.x // CHUNK_SIZE), int(new_block_position.z // CHUNK_SIZE)
            if (cx, cz) in chunk_blocks:
                Entity(model='cube', texture='terra.jpg', collider='box', position=new_block_position)
                chunk_blocks[(cx, cz)][tuple(new_block_position)] = True

# -------------------- SKY & RUN --------------------
Sky()
app.run()
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import numpy as np

app = Ursina()
window.fullscreen = True

# -------------------- CONFIG --------------------
CHUNK_SIZE = 16
RENDER_DISTANCE = 2
BASE_HEIGHT = 20
MAX_DISTANCE_FOR_TRANSITION = 5  # distanza dopo cui il noise è completo

loaded_chunks = {}

# -------------------- TERRAIN NOISE --------------------
def terrain_noise(x, z):
    """Combinazione di montagne, colline e avvallamenti"""
    mountains = (np.sin(x * 0.01) + np.cos(z * 0.01)) * 15
    hills = (np.sin(x * 0.05) + np.cos(z * 0.05)) * 5
    detail = (np.sin(x * 0.15) * np.cos(z * 0.15)) * 2
    valleys = -abs(np.sin(x * 0.02) * np.cos(z * 0.02)) * 10
    return int(mountains + hills + detail + valleys)

def get_top_height(world_x, world_z):
    """Calcola l'altezza del terreno con transizione graduale"""
    dist = int(max(abs(world_x // CHUNK_SIZE), abs(world_z // CHUNK_SIZE)))
    if dist <= 1:
        return BASE_HEIGHT
    elif dist <= MAX_DISTANCE_FOR_TRANSITION:
        t = (dist - 1) / (MAX_DISTANCE_FOR_TRANSITION - 1)
        noise_height = BASE_HEIGHT + terrain_noise(world_x, world_z)
        return int(BASE_HEIGHT * (1 - t) + noise_height * t)
    else:
        return BASE_HEIGHT + terrain_noise(world_x, world_z)

# -------------------- GENERA CHUNK --------------------
def generate_chunk(chunk_x, chunk_z):
    chunk = Entity()
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            top_height = get_top_height(world_x, world_z)

            # Riempimento totale dal basso fino al top
            for y in range(top_height + 1):
                color_block = color.lime if y == top_height else color.rgb(100,70,40)
                Entity(parent=chunk, model='cube', collider='box', color=color_block,
                       position=(world_x, y, world_z))
    loaded_chunks[(chunk_x, chunk_z)] = chunk
    return chunk

# -------------------- GESTIONE CHUNK --------------------
def update_chunks(player_position):
    player_chunk_x = int(player_position[0] // CHUNK_SIZE)
    player_chunk_z = int(player_position[2] // CHUNK_SIZE)

    # Genera nuovi chunk
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            coord = (player_chunk_x + dx, player_chunk_z + dz)
            if coord not in loaded_chunks:
                generate_chunk(*coord)

    # Rimuovi chunk lontani
    to_remove = []
    for coord in list(loaded_chunks.keys()):
        if abs(coord[0] - player_chunk_x) > RENDER_DISTANCE or abs(coord[1] - player_chunk_z) > RENDER_DISTANCE:
            loaded_chunks[coord].disable()
            to_remove.append(coord)
    for coord in to_remove:
        del loaded_chunks[coord]

# -------------------- PLAYER --------------------
initial_chunk = generate_chunk(0, 0)
max_y = max([e.position.y for e in initial_chunk.children])
spawn_y = max_y + 30

player = FirstPersonController()
player.gravity = 1
player.position = (0, spawn_y, 0)

# -------------------- UPDATE --------------------
def update():
    update_chunks(player.position)
    if player.y < -10:  # respawn se cade
        player.position = (0, spawn_y, 0)
        player.gravity = 1

# -------------------- INPUT --------------------
def input(key):
    if key == "escape":
        application.quit()

# -------------------- SKY & RUN --------------------
Sky()
app.run()

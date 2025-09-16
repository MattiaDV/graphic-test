from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Carica la texture
terra_texture = load_texture('terra.jpg')

# Crea una mesh unica per il terreno
terrain = Entity(model=Mesh(vertices=[], uvs=[]), texture=terra_texture)

# Funzione per aggiungere un blocco
def add_block(position):
    terrain.model.vertices.extend([
        # Aggiungi i vertici del blocco
    ])
    terrain.model.generate()

# Funzione per rimuovere un blocco
def remove_block(position):
    # Rimuovi i vertici del blocco
    terrain.model.generate()

# Funzione di aggiornamento
def update():
    # Aggiungi o rimuovi blocchi in base all'input dell'utente
    pass

# Imposta la posizione iniziale del giocatore
player = FirstPersonController()
player.position = (0, 10, 0)

app.run()

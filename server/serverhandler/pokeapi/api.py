import pokebase as pb
from random import randint

MAX_ID = 898

def get_random_pokemon():
    return get_pokemon_by_id(randint(1, MAX_ID))

def get_pokemon_by_id(poke_id):
    pokemon = pb.pokemon(poke_id)
    return {"name": pokemon.name, "sprite_url": pokemon.sprites.front_default, "poke_id": pokemon.id}

if __name__ == "__main__":
    print("API Test")

    print(f"Random: {get_random_pokemon()}")
    print(f"Bulbasaur: {get_pokemon_by_id(1)}")
    print(f"Max id: {get_pokemon_by_id(MAX_ID)}")

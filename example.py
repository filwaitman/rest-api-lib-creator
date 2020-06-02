from rest_api_lib_creator.core import OnException, RestApiLib, ViewsetRestApiLib


class Ability(RestApiLib):
    use_str_in_place_of_repr = True

    def get_pretty_identifier(self):
        return f'{self.ability["name"]} on slot #{self.slot}'


class Pokemon(ViewsetRestApiLib):
    base_api_url = 'https://pokeapi.co/api/v2/pokemon'
    identifier_field = 'name'  # Default to 'id'
    on_exception = OnException.return_response  # Without this an exception will be raised every time a 4XX is returned
    nested_objects = {
        'abilities': Ability,  # So 'abilities' will be converted to a list of <Ability> instances
    }


# --> Get a list of items
pokemons = Pokemon.list()
pokemons
# [<Pokemon: bulbasaur>,
#  <Pokemon: ivysaur>,
#  <Pokemon: venusaur>,
#  <Pokemon: charmander>,
#  <Pokemon: charmeleon>,
#  <Pokemon: charizard>,
#  <Pokemon: squirtle>,
#  <Pokemon: wartortle>,
#  <Pokemon: blastoise>,
#  <Pokemon: caterpie>,
#  <Pokemon: metapod>,
#  <Pokemon: butterfree>,
#  <Pokemon: weedle>,
#  <Pokemon: kakuna>,
#  <Pokemon: beedrill>,
#  <Pokemon: pidgey>,
#  <Pokemon: pidgeotto>,
#  <Pokemon: pidgeot>,
#  <Pokemon: rattata>,
#  <Pokemon: raticate>]
pokemons._meta.request.method
# GET
pokemons._meta.response.status_code
# 200
pokemons._meta.to_curl()
# "curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' -H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' https://pokeapi.co/api/v2/pokemon"
# (requires curlify)

# --> Retrieve a particular item
pokemon = Pokemon.retrieve('pikachu')
pokemon
# <Pokemon: pikachu>
pokemon.height, pokemon.weight
# (4, 60)
pokemon._meta.request.method
# GET
pokemon._meta.response.status_code
# 200
pokemon._meta.to_curl()
# "curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' -H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.23.0' https://pokeapi.co/api/v2/pokemon/pikachu"
# (requires curlify)
pokemon.abilities
# [<Ability: lightning-rod on slot #3>,
#  <Ability: static on slot #1>]

# --> Create an item
bad_response = Pokemon.create(name='pikachu', height=6, weight=70)
bad_response._meta.response.content
# Error as this API is readonly

# --> Update an item
bad_response = Pokemon.update('pikachu', name='NEWNAME')
bad_response._meta.response.content
# Error as this API is readonly

# --> Delete an item
bad_response = Pokemon.delete('pikachu')
bad_response._meta.response.content
# Error as this API is readonly

# --> Create a new item as a python object, mode 1
new_pokemon = Pokemon(name='pikachu', height=6, weight=70)
bad_response = new_pokemon.save()  # Issues the POST
bad_response._meta.response.content
# Error as this API is readonly

# --> Create a new item as a python object, mode 2
new_pokemon = Pokemon()
new_pokemon.name = 'pikachu'
bad_response = new_pokemon.save()  # Issues the POST
bad_response._meta.response.content
# Error as this API is readonly

# --> Update an item as a python object
pokemon = Pokemon.retrieve('pikachu')
pokemon.name = 'NEW NAME'
bad_response = pokemon.save()  # Issues the PATCH
bad_response._meta.response.content
# Error as this API is readonly

# --> Delete an item as a python object
pokemon = Pokemon.retrieve('pikachu')
bad_response = pokemon.destroy()  # Issues the DELETE
bad_response._meta.response.content
# Error as this API is readonly

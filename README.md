[![Travis](https://travis-ci.com/filwaitman/rest-api-lib-creator.svg?branch=master)](https://travis-ci.com/filwaitman/rest-api-lib-creator)
[![Codecov](https://codecov.io/gh/filwaitman/rest-api-lib-creator/branch/master/graph/badge.svg)](https://codecov.io/gh/filwaitman/rest-api-lib-creator)
[![PyPI](https://img.shields.io/pypi/v/rest-api-lib-creator.svg)](https://pypi.python.org/pypi/rest-api-lib-creator/)
[![License](https://img.shields.io/pypi/l/rest-api-lib-creator.svg)](https://pypi.python.org/pypi/rest-api-lib-creator/)
[![Python versions](https://img.shields.io/pypi/pyversions/rest-api-lib-creator.svg)](https://pypi.python.org/pypi/rest-api-lib-creator/)
[![PyPI downloads per month](https://img.shields.io/pypi/dm/rest-api-lib-creator.svg)](https://pypi.python.org/pypi/rest-api-lib-creator/)


# REST API lib creator

REST API lib creator is a boilerplate-free way for creating libs for RESTful APIs (specially the ones created using [Django REST framework](https://github.com/encode/django-rest-framework) - but certainly adaptable for other frameworks).

**NOTES**:
* This is a port for a personal project I made for myself. It may or may not solve your needs (it solves mine).
* This is still alpha. I opened this on GH just so I can see if this is something I should improve (or not).


## Examples:

* The bare minimum for creating your own lib:
```python
from rest_api_lib_creator.core import ViewsetRestApiLib


class User(ViewsetRestApiLib):
    base_api_url = 'http://super.cool/api/users'
```

* With this you can play around with your API:
```python
users = User.list()  # Triggers a requests.get with url=http://super.cool/api/users
isinstance(users[0], User)

user = User.create(first_name='Filipe', last_name='Waitman', email='filwaitman@gmail.com', photo=open('image.png', 'rb'))  # Triggers a requests.post with url=http://super.cool/api/users and data={'first_name': 'Filipe', 'last_name': 'Waitman', 'email': 'filwaitman@gmail.com'} and files={'photo': <file binary content>}

# Similarly to the call above you could create an empty object and save it:
user = User()
user.first_name = 'Filipe'
user.last_name = 'Waitman'
user.email = 'filwaitman@gmail.com'
user.photo = open('image.png', 'rb')
user.save()  # Triggers a requests.post with url=http://super.cool/api/users and data={'first_name': 'Filipe', 'last_name': 'Waitman', 'email': 'filwaitman@gmail.com'} and files={'photo': <file binary content>}

isinstance(user, User)
print(user.id)  # Prints the user id (assuming the API returned this field)
print(user.first_name)  # )rints the user first name (assuming the API returned this field)
user.first_name = 'New name'
user.save()  # Triggers a requests.patch with url=http://super.cool/api/users/<user-id> and data={'first_name': 'New name'}

user.delete()  # Triggers a requests.delete with url=http://super.cool/api/users/<user-id>
```

* If your resource return other nested resources you can parse them as well:
```python
class Pet(ViewsetRestApiLib):
    base_api_url = 'http://super.cool/api/pets'
    nested_objects = {
        'owner': User,
    }


pet = Pet.retrieve('pet-id')
isinstance(pet, Pet)
isinstance(pet.owner, User)
```

* See a more complete (and real world) example [here](https://github.com/filwaitman/rest-api-lib-creator/blob/master/example.py)
* You can see all possible customizations [here](https://github.com/filwaitman/rest-api-lib-creator/blob/master/rest_api_lib_creator/core.py#L22-L50) (someday I'll improve this doc).

## Special thanks:

* [Django REST framework](https://github.com/encode/django-rest-framework) - you're the best, seriously.
* [Stripe-python lib](https://github.com/stripe/stripe-python) - which I used as an inspiration to create this project.


## Development:

### Run linter:
```bash
pip install -r requirements_dev.txt
isort -rc .
tox -e lint
```

### Run tests via `tox`:
```bash
pip install -r requirements_dev.txt
tox
```

### Release a new major/minor/patch version:
```bash
pip install -r requirements_dev.txt
bump2version <PART>  # <PART> can be either 'patch' or 'minor' or 'major'
```

### Upload to PyPI:
```bash
pip install -r requirements_dev.txt
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```

## Contributing:

Please [open issues](https://github.com/filwaitman/rest-api-lib-creator/issues) if you see one, or [create a pull request](https://github.com/filwaitman/rest-api-lib-creator/pulls) when possible.
In case of a pull request, please consider the following:
- Respect the line length (132 characters)
- Write automated tests
- Run `tox` locally so you can see if everything is green (including linter and other python versions)

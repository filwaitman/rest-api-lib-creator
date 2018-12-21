from setuptools import setup

from rest_api_lib_creator import VERSION

BASE_CVS_URL = 'https://github.com/filwaitman/rest-api-lib-creator'


setup(
    name='rest-api-lib-creator',
    packages=['rest_api_lib_creator', ],
    version=VERSION,

    author='Filipe Waitman',
    author_email='filwaitman@gmail.com',

    description='Boilerplate-free way for creating libs for REST APIs',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    url=BASE_CVS_URL,
    download_url='{}/tarball/{}'.format(BASE_CVS_URL, VERSION),

    install_requires=[x.strip() for x in open('requirements.txt').readlines()],

    test_suite='tests',
    tests_require=[x.strip() for x in open('requirements_test.txt').readlines()],

    keywords=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

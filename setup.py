from setuptools import setup, find_packages

setup(
    name='YourGame',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pygame',
        'RPi.GPIO',
        'smbus',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'yourgame=yourgame.main:main',
        ],
    },
)

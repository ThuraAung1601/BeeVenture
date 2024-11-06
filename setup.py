from setuptools import setup, find_packages

setup(
    name='BeeVenture',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pygame',
        'RPi.GPIO',
        'mpu6050-raspberrypi'
    ],
    entry_points={
        'console_scripts': [
            'beeventure=beeventure.app:main',
        ],
    },
)

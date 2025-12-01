from setuptools import setup, find_packages

setup(
    name='cli-tools',
    version='1.0',
    packages=find_packages(),  # Automatically finds the cmds directory and other packages
    install_requires=[
        'requests',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'weather = cmds.weather:main',
            'neo = cmds.neo:main',
            'wut = cmds.define:main',
            'sky = cmds.sky:main',
            'weather_log = cmds.weather_logger:main',
            'sensors = cmds.s_array:main',
            'lights = cmds.lights:main',
            'pollen = cmds.pollen:main',
            'scan = cmds.scan_network:main',
            'nyc = cmds.might_take_awhile:main'

        ],
    },
)

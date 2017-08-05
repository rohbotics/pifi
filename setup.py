from setuptools import setup, find_packages

setup(
    name='pifi',
    version='0.2.0',
    description='Wifi provisioning tools for robots with Raspberry Pis',
    url='https://github.com/rohbotics/pifi',

    author='Rohan Agrawal',
    author_email='send2arohan@gmail.com',
    license='BSD',

    packages=find_packages(),    

    install_requires=['python-networkmanager', 'docopt'],

    entry_points={
        'console_scripts': [
            'pifi_startup=pifi.startup:main',
            'pifi=pifi.pifi:main',
        ],
    }
)

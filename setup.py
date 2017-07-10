from setuptools import setup, find_packages

setup(
    name='pifi',
    version='0.1.3',
    description='Wifi tools for the Raspberry Pi',
    url='https://github.com/rohbotics/pifi',

    author='Rohan Agrawal',
    author_email='send2arohan@gmail.com',
    license='BSD',

    packages=find_packages(),    

    install_requires=['python-networkmanager', 'docopt'],

    entry_points={
        'console_scripts': [
            'pifi_ap_startup=pifi.startup:main',
            'pifi=pifi.pifi:main',
        ],
    }
)

from setuptools import setup, find_packages

setup(
    name='pifi',
    version='0.0.1',
    description='Wifi tools for the Raspberry Pi',
    url='https://github.com/rohbotics/pifi',

    author='Rohan Agrawal',
    author_email='send2arohan@gmail.com',
    license='BSD',

    py_modules=["ap_startup"],    

    install_requires=['python-networkmanager'],

    entry_points={
        'console_scripts': [
            'pifi_ap_startup=ap_startup:main',
        ],
    }
)

from setuptools import setup, find_packages

exec(open("pifi/version.py").read())

setup(
    name="pifi",
    version=__version__,
    description="Wifi provisioning tools for robots with Raspberry Pis",
    url="https://github.com/rohbotics/pifi",
    author="Rohan Agrawal",
    author_email="send2arohan@gmail.com",
    license="BSD",
    packages=find_packages(exclude=["test"]),
    install_requires=["python-networkmanager", "empy", "pyyaml", "evdev"],
    entry_points={
        "console_scripts": [
            "pifi_startup=pifi.startup:main",
            "pifi=pifi.pifi:main",
        ],
    },
    test_suite="test",
)

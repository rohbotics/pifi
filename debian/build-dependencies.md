This package depends on debhelper, dh-python, dh-systemd, python3-all, python3-networkmanager, python3-docopt, python3-empy, and python3-yaml.

All of these packages, except for python3-networkmanager are availible in the standard ubuntu xenial repositories. It is avalible from pip with `pip3 install python-networkmanager` and from https://packages.ubiquityrobotics.com/. The latter is a debian package built with the following method.

1. Clone the git source. `git clone https://github.com/seveas/python-networkmanager.git`

2. Checkout the debian branch. `git checkout debian`

3. Generate dsc. `gbp buildpackage -S -us -uc`

4. Use cowbuilder to build. `cd ..; sudo cowbuilder --build python-networkmanager_2.0.1-1.dsc`

5. Get binary deb from `/var/cache/pbuilder/result`.


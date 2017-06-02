# -*- encoding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

install_requires = [
    'pytest==3.0.7',
    'mock==2.0.0',
    'GitPython==2.1.3',
    'pyyaml==3.12',
    'freezegun==0.3.9',
]


if __name__ == '__main__':
    setup(
        name='confsave',
        version='0.3',
        description='Configuration Saver',
        url='https://github.com/socek/confsave',
        license='Apache License 2.0',
        packages=find_packages('.'),
        package_dir={'': '.'},
        install_requires=install_requires,
        entry_points={
            'console_scripts': (
                'cs = confsave.cmd:run',
            )
        }
    )

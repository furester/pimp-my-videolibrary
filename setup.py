from setuptools import setup
import glob
import os

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]

from cli import __version__, _program

setup(name=_program,
      version=__version__,
      packages=['cli'],
      description='Pimp videolibrary',
      url='https://github.com/furester/pimp-my-videolibrary',
      author='Igor Scabini',
      author_email='furester@gmail.com',
      license='Apache License Version 2.0',
      entry_points="""
      [console_scripts]
      {program} = cli.command:main
      """.format(program = _program),
      keywords=[],
      tests_require=['pytest', 'coveralls'],
      zip_safe=False)

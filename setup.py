import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'curator',
    version = '0.0.1',
    packages = ['curator'],
    author = 'Michael Moorman',
    author_email = 'tensorpuddin@devio.us',
    description = ("An elegant desktop-background switching indicator applet"
                   "for GNOME"),
    license = 'BSD License',
    scripts = ['scripts/curator'],
    package_data = { 'curator': ['curator.ui'] }
)

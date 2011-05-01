import os
import subprocess
from distutils.core import setup
from distutils.command.install import install as _install

class install(_install):

    def run(self):
        # Run the normal install
        _install.run(self)
        # Post-install configuration goes here
        # Install gconf schemas
        subprocess.call(["gconftool-2", "--install-schema-file",
                         "share/curator.schemas"])

setup(
    name = 'curator',
    version = '0.0.3',
    packages = ['curator'],
    author = 'Michael Moorman',
    author_email = 'tensorpuddin@devio.us',
    description = ("An elegant desktop-background switching indicator applet"
                   "for the GNOME desktop"),
    license = 'BSD License',
    cmdclass =  {
        'install': install,
        },
    scripts = ['scripts/curator', 'scripts/curator-dbus'],
    package_data = { 'curator': ['*.ui'] },
    data_files = [('share/icons/ubuntu-mono-dark/apps/48',
                   ['share/icons/ubuntu-mono-dark/apps/48/curator.svg']),
                  ('share/icons/ubuntu-mono-light/apps/48',
                   ['share/icons/ubuntu-mono-light/apps/48/curator.svg']),
                  ('share/icons/hicolor/scalable/apps',
                   ['share/icons/hicolor/scalable/apps/curator.svg']),
                  ('share/applications',
                   ['share/applications/curator.desktop'])]
)

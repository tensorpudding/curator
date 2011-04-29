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
    version = '0.0.1',
    packages = ['curator'],
    author = 'Michael Moorman',
    author_email = 'tensorpuddin@devio.us',
    description = ("An elegant desktop-background switching indicator applet"
                   "for GNOME"),
    license = 'BSD License',
    cmdclass =  {
        'install': install,
        },
    scripts = ['scripts/curator', 'scripts/curator-dbus'],
    package_data = { 'curator': ['*.ui'] },
    data_files = [('share/icons/scalable/apps',
                   ['share/curator.svg', 'share/curator-light.svg',
                    'share/curator-dark.svg']),
                  ('share/applications', ['share/curator.desktop'])]
)

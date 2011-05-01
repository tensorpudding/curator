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

_data_files = [
    ('share/icons/hicolor/scalable/apps', ['share/icons/hicolor/scalable/apps/curator.svg']),
    ('share/icons/hicolor/256x256/apps', ['share/icons/hicolor/256x256/apps/curator.png']),
    ('share/icons/hicolor/192x192/apps', ['share/icons/hicolor/192x192/apps/curator.png']),
    ('share/icons/hicolor/128x128/apps', ['share/icons/hicolor/128x128/apps/curator.png']),
    ('share/icons/hicolor/96x96/apps', ['share/icons/hicolor/96x96/apps/curator.png']),
    ('share/icons/hicolor/72x72/apps', ['share/icons/hicolor/72x72/apps/curator.png']),
    ('share/icons/hicolor/64x64/apps', ['share/icons/hicolor/64x64/apps/curator.png']),
    ('share/icons/hicolor/48x48/apps', ['share/icons/hicolor/48x48/apps/curator.png']),
    ('share/icons/hicolor/36x36/apps', ['share/icons/hicolor/36x36/apps/curator.png']),
    ('share/icons/hicolor/32x32/apps', ['share/icons/hicolor/32x32/apps/curator.png']),
    ('share/icons/hicolor/24x24/apps', ['share/icons/hicolor/24x24/apps/curator.png']),
    ('share/icons/hicolor/22x22/apps', ['share/icons/hicolor/22x22/apps/curator.png']),
    ('share/icons/hicolor/16x16/apps', ['share/icons/hicolor/16x16/apps/curator.png']),
    ('share/icons/ubuntu-mono-dark/apps/16x16', ['share/icons/ubuntu-mono-dark/apps/16x16/curator.svg']),
    ('share/icons/ubuntu-mono-dark/apps/22x22', ['share/icons/ubuntu-mono-dark/apps/22x22/curator.svg']),
    ('share/icons/ubuntu-mono-dark/apps/24x24', ['share/icons/ubuntu-mono-dark/apps/24x24/curator.svg']),
    ('share/icons/ubuntu-mono-dark/apps/48x48', ['share/icons/ubuntu-mono-dark/apps/48x48/curator.svg']),
    ('share/icons/ubuntu-mono-light/apps/16x16', ['share/icons/ubuntu-mono-light/apps/16x16/curator.svg']),
    ('share/icons/ubuntu-mono-light/apps/22x22', ['share/icons/ubuntu-mono-light/apps/22x22/curator.svg']),
    ('share/icons/ubuntu-mono-light/apps/24x24', ['share/icons/ubuntu-mono-light/apps/24x24/curator.svg']),
    ('share/icons/ubuntu-mono-light/apps/48x48', ['share/icons/ubuntu-mono-light/apps/48x48/curator.svg']),
    ('share/applications', ['share/applications/curator.desktop']),
    ]
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
    data_files = _data_files,
)

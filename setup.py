from distutils.core import setup
from mikidown import __version__, __appname__
setup(name=__appname__,
    version=__version__,
    scripts = ['mikidown/scripts/mikidown'],
    packages=['mikidown'],
    data_files=[('share/mikidown', ['README.mkd']), 
        ('share/mikidown', ['mikidown/notes.css']),
        ('share/pixmaps', ['mikidown.png']),
        ('share/applications', ['mikidown.desktop'])],
    requires = ['PyQt', 'markdown']
    )

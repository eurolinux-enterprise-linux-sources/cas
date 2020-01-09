"""
    setup.py - distutils packaging
"""
from distutils.core import setup
import os

libpath = "/var/lib/cas"
snippetpath = os.path.join(libpath,"snippets")

# Build data_files easily
data_files = []

# add static files
data_files.append(['/etc',['cas.conf']])
data_files.append(['/usr/share/man/man1', ['cas.1.gz','cas-admin.1.gz']])

# Automate addition of snippets, simply add new snippets to default install
# and they will be included.
for dirpath, dirnames, filenames in os.walk('snippets'):
    data_files.append([snippetpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = 'cas',
    version = '0.15',
    author = 'Adam Stokes',
    author_email = 'ajs@redhat.com',
    url = "http://fedorahosted.org/cas",
    description = "CAS - automated core setup",
    packages = ['cas',],
    scripts = ['cas','cas-admin'],
    package_dir = {'': 'lib',},
    data_files = data_files,
)

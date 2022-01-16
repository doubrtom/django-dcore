import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requires = [
    'django>=2.0',
    'python-dateutil>=2.8.0',
]

setup(
    name='django-dcore',
    version='0.31',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Django app with core/commonly used code.',
    long_description=README,
    url='https://github.com/doubrtom/django-dcore',
    author='Tomas Doubravsky',
    author_email='doubravskytomas@gmail.com',
    python_requires=">=3.8",
    install_requires=requires,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

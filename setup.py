from distutils.core import setup
from setuptools import setup


setup(
    name='socketbroker',
    version='0.1',
    url='http://github.com/truevision/socketbroker/',
    license='BSD',
    author='Kristaps Kulis',
    author_email='kristaps@true-vision.net',
    description = "socket message broker with flash socket policy support",
    packages=["socketbroker"],
    scripts = ["socketbroker/socketbroker"],
    zip_safe=False,
    platforms='any',
)

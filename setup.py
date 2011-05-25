from distutils.core import setup
from setuptools import setup


setup(
    name='socketbroker',
    version='0.1',
    url='http://github.com/truevision/flask/',
    license='BSD',
    author='Kristaps Kulis',
    author_email='kristaps@true-vision.net',
    description = "socket message broker with flash socket policy support",
    py_modules=["socketbroker"],
    zip_safe=False,
    platforms='any',
)

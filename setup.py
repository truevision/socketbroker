from setuptools import setup


setup(
    name='socketbroker',
    version='0.2',
    url='http://github.com/truevision/socketbroker/',
    license='BSD',
    author='Kristaps Kulis',
    author_email='kristaps@true-vision.net',
    description = "socket message broker with flash socket policy support",
    packages=["socketbroker"],
    entry_points = {
        'console_scripts' : [
            'socketbroker = socketbroker.run:main',
            ]
    },
    zip_safe=False,
    platforms='any',
)

from distutils.core import setup
from setuptools import find_packages


def do_setup():
    package_data = {}
    package_data[""] = [
        '*.md', 
        '*.rst', 
        '*.tex',
        'LICENSE*']

    setup(name="PyTex",
            version="1.1.0",
            description="Write LaTeX files via Python",
            author="Ben Smithers",
            url="https://github.com/BenSmithers/PyTex",
            packages=find_packages(),
            package_data=package_data,
            install_requires=[
                'pandas',
                ],
            )

if __name__=='__main__':
    do_setup()
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
            version="1.0.2",
            description="Write LaTeX files via Python",
            author="Ben Smithers",
            url="https://github.com/BenSmithers/PyTex",
            packages=find_packages(),
            package_data=package_data)

if __name__=='__main__':
    do_setup()
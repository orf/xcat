from setuptools import setup
import os
import sys

if sys.version_info < (3, 6):
    raise RuntimeError('xcat requires Python 3.6!')

readme = ""
if os.path.exists("README.rst"):
    with open("README.rst") as f:
        readme = f.read()


setup(name="xcat",
      version="0.9",
      author="Tom Forbes",
      license="MIT",
      author_email="tom@tomforb.es",
      package_dir={'xcat': 'xcat'},
      packages=["xcat"],
      install_requires=["aiohttp", "docopt", 'colorama', 'ipgetter', 'tqdm', 'prompt_toolkit'],
      entry_points={
          'console_scripts': [
              'xcat = xcat.cli:run'
          ]
      },
      description="A command line tool to automate the exploitation of blind XPath injection vulnerabilities",
      long_description=readme,
      url="https://github.com/orf/xcat",
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
      ])

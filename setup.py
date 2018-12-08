import os

from setuptools import setup

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
      packages=['xcat'],
      install_requires=[
          'xpath-expressions~=0.2',
          'aiohttp~=3.0',
          'aiodns',
          'cchardet',
          'colorama',
          'tqdm',
          'prompt_toolkit',
          'click'
      ],
      python_requires='>=3.7',
      entry_points={
          'console_scripts': [
              'xcat = xcat.cli:cli',
          ]
      },
      description="A command line tool to automate the exploitation of blind XPath injection vulnerabilities",
      long_description=readme,
      url="https://github.com/orf/xcat",
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
      ])

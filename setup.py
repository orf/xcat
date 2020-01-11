import os

from setuptools import setup

readme = ""
if os.path.exists("README.md"):
    with open("README.md") as f:
        readme = f.read()

setup(name="xcat",
      version="1.0.4",
      author="Tom Forbes",
      license="MIT",
      author_email="tom@tomforb.es",
      package_dir={'xcat': 'xcat'},
      packages=['xcat'],
      install_requires=[
          'xpath-expressions~=1.0',
          'aiohttp~=3.0',
          'aiodns',
          'cchardet',
          'colorama',
          'prompt_toolkit<4',
          'click',
          'appdirs',
      ],
      python_requires='>=3.7',
      entry_points={
          'console_scripts': [
              'xcat = xcat.cli:cli',
          ]
      },
      description="A command line tool to automate the exploitation of blind XPath injection vulnerabilities",
      long_description=readme,
      long_description_content_type='text/markdown',
      url="https://github.com/orf/xcat",
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
      ])

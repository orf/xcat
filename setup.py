from setuptools import find_packages, setup


setup(name="xcat",
      version="0.6",
      description="",
      author="Tom Forbes",
      author_email="tom@tomforb.es",
      package_dir = {'xcat': 'xcat'},
      packages = ["xcat"] + ["xcat." + p for p in find_packages("xcat")],
      install_requires=["aiohttp", "click", "nose", "logbook", "xmltodict", 'colorama', 'ipgetter'],
      entry_points={
          'console_scripts': [
              'xcat = xcat.xcat:run'
          ]
      },
      classifiers=[
          'Programming Language :: Python :: 3',
      ])
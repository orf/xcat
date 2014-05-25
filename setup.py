from setuptools import find_packages, setup


setup(name="xcat",
      version="0.3",
      description="",
      author="Tom Forbes",
      author_email="tom@tomforb.es",
      package_dir = {'xcat': 'src'},
      namespace_packages =["xcat"],
      packages = ["xcat." + p for p in find_packages("src")],
      install_requires=["aiohttp", "click", "nose", "logbook", "xmltodict", 'colorama', 'ipgetter'],
      entry_points={
          'console_scripts': [
              'xcat = xcat.xcat:run_from_cmd'
          ]
      })
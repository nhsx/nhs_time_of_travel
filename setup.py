from distutils.core import setup

setup(
    name="nhstravel",
    version="0.1",
    description="Geolocation code for NHS use cases",
    author="NHS Pycom authors",
    packages=["nhstravel.loaders"],
    py_modules=["nhstravel.info", "nhstravel.gp"],
)

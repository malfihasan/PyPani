from setuptools import setup, find_packages

with open('README.md') as f:
	readme = f.read()

with open("LICENSE") as f:
	license = f.read()


setup(
	name = 'PyPani',
	version = "1.0.1",
	description = "A tool for calculating water balance ratio for crop.",
	long_description = readme,
	author = 'M. Alfi Hasan',
	author_email = 'mdalfihasan19@gmail.com',
	license = license,
    package = find_packages(exclude = ('tests'))

)
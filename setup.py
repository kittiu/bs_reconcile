from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in bs_reconcile/__init__.py
from bs_reconcile import __version__ as version

setup(
	name="bs_reconcile",
	version=version,
	description="Allow reconcile all balance sheet gl entry",
	author="FLO WORKS",
	author_email="kittiu@flo-works.co",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)

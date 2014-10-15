import re
from setuptools import setup

version = re.search(
	'^__version__\s*=\s*"(.*)"',
	open('pumpr/pumpr.py').read(),
	re.M
	).group(1)

setup(
	name="pumpr",
	packages=["pumpr"],
	entry_points = {
		"console_scripts": ['pumpr = pumpr.pumpr:main']
	},
	version=version,
	description="Fills syringepump.com syringes with water so you don't have to",
	long_description="Fills syringepump.com syringes with water, provides simple commands to add new pumps to the network, cleaning routines, etc.",
	author="Travis Chapman",
	author_email="travisechapman@gmail.com",
	url="http://seetravisblog.com",
	install_requires="Phidgets>=2.1.8",
	dependency_links=["https://github.com/teechap/Phidgets/tarball/master#egg=Phidgets-2.1.8"]
)

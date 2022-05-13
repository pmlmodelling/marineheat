from setuptools import Command, find_packages, setup

DESCRIPTION = "A package for matching ERSEM with points"
LONG_DESCRIPTION = """


"""

PROJECT_URLS = {
    "Bug Tracker": "https://github.com/pmlmodelling/marineheat/issues",
    "Source Code": "https://github.com/pmlmodelling/marineheat",
}

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]


setup(name='marineheat',
      version='0.0.1',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      python_requires='>=3.6.1',
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

      project_urls=PROJECT_URLS,
      url = "https://github.com/pmlmodelling/marineheat",
      author='Robert Wilson',
      maintainer='Robert Wilson',
      author_email='rwi@pml.ac.uk',

      packages = ["marineheat"],
      setup_requires=[
        'setuptools',
        'setuptools-git',
        'wheel',
    ],
      install_requires = REQUIREMENTS,
      zip_safe=False)





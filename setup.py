import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = """Portfolio Tool
"""

requires = [
    ]

setup(name='portfoliotool',
      author='CJ Niemira',
      author_email='siege@siege.org',
      version='0.1',
      description='Portfolio Tool',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
      ],
      url='https://github.com/cniemira/portfoliotool',
      keywords='games',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite=None,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      portfoliotool = portfoliotool.cli:main
      """,
      )

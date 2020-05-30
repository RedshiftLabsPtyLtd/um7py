import json
import setuptools
from os import environ


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version_info = json.load(fh)

version_major = '0' if not version_info.get('VERSION_MAJOR') else version_info['VERSION_MAJOR']
version_minor = '0' if not version_info.get('VERSION_MINOR') else version_info['VERSION_MINOR']
pipeline_number = '1' if not environ.get('CI_BUILD_NUMBER') else environ['CI_BUILD_NUMBER']

setuptools.setup(
    name="um7py",
    version=f"{version_major}.{version_minor}.{pipeline_number}",
    author="Redshift Labs Pty Ltd, Dr. Konstantin Selyunin",
    author_email="selyunin.k.v@gmail.com",
    license="MIT",
    description="Redshift Labs Pty Ltd UM7 Python Driver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RedshiftLabsPtyLtd/um7py",
    packages=["um7py"],
    requires=["pyserial"],
    install_requires=["pyserial"],
    package_dir={'um7py': 'um7py'},
    package_data={"um7py": ['rsl_xml_svd/RSL-SVD.xsd',
                            'rsl_xml_svd/um7.svd',
                            'rsl_xml_svd/rsl_svd_parser.py',
                            'templates/*.jinja2',
                            'examples/*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
)

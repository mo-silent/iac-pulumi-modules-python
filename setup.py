import os
from setuptools import setup, find_packages
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname),encoding='utf-8').read()

setup(
    name = "iac_modules", 
    version = "0.0.1", # Initial version number
    author = "Silent Mo", 
    author_email = "1916393131@qq.com",
    description = ("An iac pulumi automation project"),
    keywords = ['pulumi',  'iac'],
    url = "https://github.com/mo-silent/iac-pulumi-modules-python.git",  # Optional: Link to project's homepage
    packages=find_packages(), # Automatically find all packages
    long_description=read('README.md'), # Optional: Read the contents of your README file
    long_description_content_type="text/markdown",  # If README is in markdown
    install_requires=[
        'pulumi>=3.0.0,<4.0.0',
        'pulumi_alicloud>=3.0.0,<4.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Or another license
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.8', 
)
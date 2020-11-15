import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='messenger-counter',
    version='0.1',
    author="Krzysztof Mizgała",
    author_email="KMChris007@gmail.com",
    description="Package for counting messages from Facebook Messenger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KMChris/messenger-counter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amazon-reviews-crawler",
    version="0.0.1",
    author="Anzel Lai",
    author_email="anzel_lai@hotmail.com",
    description="A simple package to crawl Amazon Reviews text from product ID(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anzellai/amazon-reviews-crawler.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

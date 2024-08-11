import setuptools

setuptools.setup(
    name="dawvertplus", # Replace with your own username
    version="0.0.1",
    install_requires=[
        "numpy",
        "pillow",
        "lxml",
        "tinydb",
        "mido",
        "chardet",
        "beautifulsoup4",
    ],

    author="koisignal",
    author_email="",
    description="dawvert wheel module for pyodide",
    long_description="foo",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

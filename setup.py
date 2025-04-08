from setuptools import setup, find_packages

setup(
    name="notionary",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "notion-client>=2.0.0",
        "markdown-it-py>=3.0.0",
        "beautifulsoup4>=4.13.0",
        "httpx>=0.28.0",
        "python-dotenv>=1.1.0",
        "lxml>=5.3.0",
        "attrs>=25.3.0",
    ],
    author="Mathis Arends",
    author_email="mathisarends27@gmail.com",
    description="A toolkit to convert between Markdown and Notion blocks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mathisarends/notionary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)

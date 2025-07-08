from setuptools import setup, find_namespace_packages

setup(
    name="notionary",
    version="0.2.13",
    packages=find_namespace_packages(include=["notionary*"]),
    install_requires=[
        "httpx>=0.28.0",
        "python-dotenv>=1.1.0",
        "pydantic>=2.11.4",
        "posthog>=3.0.0",
        "click>=8.0.0", 
    ],
    entry_points={
        'console_scripts': [
            'notionary=notionary.cli.main:main',
        ],
    },
    author="Mathis Arends",
    author_email="mathisarends27@gmail.com",
    description="A toolkit to convert between Markdown and Notion blocks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mathisarends/notionary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)

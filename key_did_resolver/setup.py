from setuptools import setup, find_packages

setup(
    name="key_did_resolver",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "varint",
        "multibase",
        "cryptography",
    ],
    extras_require={
        "test": ["pytest", "pytest-asyncio"],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python implementation of the key-did-resolver",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/key-did-resolver-py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
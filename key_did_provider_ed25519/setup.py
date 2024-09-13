from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="key_did_provider_ed25519",
    version="0.1.0",
    author="Seref Yarar",
    author_email="seref@index.network",
    description="A Python library for managing Decentralized Identifiers (DIDs)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/did-provider",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography",
        "jwcrypto",
        "base58",
    ],
    extras_require={
        "dev": ["pytest", "pytest-asyncio"],
    },
)
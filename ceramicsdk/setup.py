from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ceramicsdk",
    version="0.1.4",
    author='Ceramic Ecosystem Developers',
    description="This Ceramic client implements the payload building, encoding, and signing needed to interact with the Ceramic Network. It currently supports ModelInstanceDocument and OrbisDB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ceramicstudio/orbis-python-starter/tree/main/py_lib",
    packages=find_packages(where='.', exclude=['examples*', 'tests*']),
    package_data={'': ['*.md']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "pytz==2023.3",
        "jsonpatch==1.33",
        "cryptography==43.0.1",
        "jwcrypto==1.5.0",
        "multiformats==0.3.1",
        "dag-cbor==0.3.3",
        "base58==2.1.1",
        "web3==7.2.0",
        "cbor2==5.6.4",
        "bip44==0.1.4",
        "varint",
    ],
)
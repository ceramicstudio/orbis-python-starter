from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ceramic_python",
    version="0.1.0",
    author='Index',
    author_email='accounts@index.network',
    description="This Ceramic client implements the payload building, encoding, and signing needed to interact with the Ceramic Network. It currently supports ModelInstanceDocument.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indexnetwork/ceramic-python/ceramic-client",
    packages=find_packages(),
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
        "cryptography==41.0.1",
        "jwcrypto==1.5.0",
        "multiformats==0.3.1",
        "dag-cbor==0.3.2",
        "base58==2.1.1",
    ],
)

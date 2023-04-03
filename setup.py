from setuptools import find_packages, setup

setup(
    name="LOntoCA",
    version="0.0.1",
    description="Legal Ontology for Collective Agreements, SS 2023",
    author="Maximilian Haller",
    author_email="maximilian.haller@tuwien.ac.at",
    license="MIT",
    install_requires=[
        "numpy==1.23.3",
        "pandas==1.5.0",
        "scikit-learn==1.1.2",
        "requests==2.28.1",
        "beautifulsoup4==4.11.2",
        "selenium==4.8.2",
        "webdriver-manager==3.8.5",
        "owlrl==6.0.2",
        "rdflib==6.2.0",
        "Flask==2.2.3",
        "tqdm==4.65.0"
    ],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=False,
)

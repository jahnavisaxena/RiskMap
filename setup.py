from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="riskmap-cli",
    version="1.0.0",
    author="Jahnavi Saxena",
    author_email="your.email@example.com",
    description="A GRC automation tool for risk assessment and control mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jahnavisaxena/RiskMap",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pandas>=2.0.0",
        "openai>=1.0.0",
        "reportlab>=4.0.0",
    ],
    extras_require={
        "web": ["flask>=3.0.0", "flask-cors>=4.0.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "riskmap=riskmap.cli:app",
        ],
    },
    include_package_data=True,
    package_data={
        "data": ["*.json"],
    },
)

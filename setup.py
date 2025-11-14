from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="forgeoagent",
    version="0.1.0",
    author="Angel Koradiya",
    author_email="koradiyaangel11@gmail.com",
    description="ForgeOAgent - An AI agent framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/angelkoradiya/forgeoagent",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "forgeoagent=forgeoagent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "forgeoagent": ["web/templates/*", "web/static/*"],
    },
)
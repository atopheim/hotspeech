#!/usr/bin/env python3
"""
Setup script for Hotspeech - Voice recording and transcription tool
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


setup(
    name="hotspeech",
    version="1.0.0",
    author="atopheim",
    author_email="your-email@example.com",
    description="Voice recording and transcription tool with hotkey support and web interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/atopheim/hotspeech",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "hotspeech=hotspeech.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hotspeech": [
            "config.toml",
            "app/webui/templates/*.html",
            "app/webui/static/*",
        ],
    },
    zip_safe=False,
)

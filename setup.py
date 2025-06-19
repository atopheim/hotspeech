#!/usr/bin/env python3
"""
Setup script for Hotspeech - Voice recording and transcription tool
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Voice recording and transcription tool with hotkey support and web interface"


# Define requirements directly
def get_requirements():
    return [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.0",
        "python-multipart>=0.0.6",
        "openai>=1.0.0",
        "toml>=0.10.2",
        "pydantic>=2.0.0",
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
    install_requires=get_requirements(),
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

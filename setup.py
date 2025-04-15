from setuptools import setup, find_packages

setup(
    name="flomo-tools",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
    ],
    entry_points={
        "console_scripts": [
            "flomo-server=src.server.__main__:main",
            "flomo-cli=src.cli.__main__:main",
        ],
    },
    author="Flomo Tools",
    author_email="example@example.com",
    description="Web服务器和命令行工具，用于与Flomo API交互",
    keywords="flomo, api, cli, web server",
    python_requires=">=3.7",
) 
from setuptools import find_packages, setup

setup(
    name="package",
    version="0.1",
    packages=find_packages(),
    install_requires=["click", "peewee"],
    entry_points={
        "console_scripts": [
            "digger=utilities.digger:digger",
            "seeker=utilities.seeker:seeker",
            "wiper=utilities.wiper:wiper",
        ],
    },
)

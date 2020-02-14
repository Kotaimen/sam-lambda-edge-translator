from setuptools import setup, find_packages

setup(
    name="translator",
    version="1.0",
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    package_data={
        # 'package': ['filename']
    },
    install_requires=[],
)

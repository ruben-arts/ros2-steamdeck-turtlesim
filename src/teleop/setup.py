from setuptools import find_packages, setup

package_name = "teleop"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Ruben",
    maintainer_email="ruben@prefix.dev",
    description="Steam Deck / keyboard teleop node for turtlesim",
    license="MIT",
    entry_points={
        "console_scripts": [
            "teleop_node = teleop.teleop_node:main",
        ],
    },
)

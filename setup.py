import sys

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

snapshot_version = '1.0.0.1'

if sys.argv[1] == '-v-minor':
    print('.'.join(snapshot_version.split('.')[:-2]))
    exit(0)

if sys.argv[1] == '-v-micro':
    print('.'.join(snapshot_version.split('.')[:-1]))
    exit(0)

if sys.argv[1] == '-v-full':
    print(snapshot_version)
    exit(0)

setuptools.setup(
    name="dyno_grp",
    version=snapshot_version,
    author="Dynamic Grouping of a Dataset",
    author_email="sergeymo@amdocs.com",
    description="This projects aims to group a dataset in a denormalized form",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.corp.amdocs.com/cto-delivery/deployment-services/unknown",
    packages=setuptools.find_packages(),
    # package_data={'core.containers': ['*.yaml'], 'core.impls.handlers.deployment.templates': ['*.j2']},
    install_requires=[
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)

from setuptools import setup, find_packages

setup(
    name='mimic',
    author="LasramR",
    description="Utility tool to clone template from git repositories, inject them and run post clone commands",
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'mimic=cli:main',
        ],
    },
)

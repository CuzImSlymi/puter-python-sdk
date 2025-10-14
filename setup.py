from setuptools import setup, find_packages

setup(
    name='puter-python-sdk',
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'puter': ['available_models.json'],
    },
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    author='Slymi',
    description='A Python library for interacting with Puter.js AI models.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CuzImSlymi/puter-python-sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)


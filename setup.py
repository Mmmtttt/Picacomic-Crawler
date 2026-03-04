from setuptools import setup, find_packages

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

version = None
with open('./src/picacomic/__init__.py', encoding='utf-8') as f:
    for line in f:
        if '__version__' in line:
            version = line[line.index("'") + 1: line.rindex("'")]
            break

if version is None:
    print('Set version first!')
    exit(1)

setup(
    name='picacomic',
    version=version,
    description='Python API For Picacomic (哔咔漫画)',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/',
    author='Picacomic',
    author_email='picacomic@example.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        'requests>=2.25.0',
        'Pillow>=8.0.0',
        'PyYAML>=5.0.0',
    ],
    keywords=['python', 'picacomic', '哔咔漫画', 'NSFW'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [
            'picacomic = picacomic.cl:main'
        ]
    }
)

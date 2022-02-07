from setuptools import setup, find_packages

requirements = [
    'pymongo>=4.0.1',
    'python-docx>=0.8.11',
    'nltk>=3.6.7',
    'pymorphy2>=0.9.1',
    'gensim>=4.1.2',
    'anytree>=2.8.0',
    'dnspython>=2.2.0'
]

try:
    f = open("README.md")
    readme = f.read()
    f.close()
except OSError as ex:
    print("failed to read readme: ignoring...")
    readme = __doc__

setup(
    name='srsparser',
    version='1.2.4',
    author='Kurmyza Pavel',
    author_email='tmrrwnxtsn@gmail.com',
    project_urls={
        'Code': 'https://github.com/Text-Analysis/srsparser/',
        'Issue Tracker': 'https://github.com/Text-Analysis/srsparser/issues',
        'Download': 'https://pypi.org/project/srsparser/',
    },
    python_requires='>=3.7',
    description=readme.split("\n")[0],
    long_description="\n".join(readme.split("\n")[2:]).lstrip(),
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'srsparser = srsparser.__main__:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords=['parser', 'text', 'documents', 'docx', 'GOST', "mongodb"]
)

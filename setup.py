from setuptools import setup, find_packages

requirements = [
    'pymongo>=4.0.1',
    'python-docx>=0.8.11',
    'nltk>=3.6.7',
    'pymorphy2>=0.9.1',
    'gensim>=4.1.2',
    'anytree>=2.8.0',
    'dnspython>=2.2.0',
    'pullenti>=4.1',
    'prettytable>=3.0.0',
    'emoji>=1.6.3'
]

with open('README.md', 'r', encoding='utf-8') as file:
    description = file.read()

setup(
    name='srsparser',
    version='1.3.15',
    author='Kurmyza Pavel',
    author_email='tmrrwnxtsn@gmail.com',
    project_urls={
        'Code': 'https://github.com/Text-Analysis/srsparser/',
        'Issue Tracker': 'https://github.com/Text-Analysis/srsparser/issues',
        'Download': 'https://pypi.org/project/srsparser/',
    },
    python_requires='>=3.7',
    description='A command-line application that parses unstructured text documents with SRS '
                'in accordance with GOST standard 34.602-89 and saves the structured results to the MongoDB database.',
    long_description=description,
    long_description_content_type='text/markdown',
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

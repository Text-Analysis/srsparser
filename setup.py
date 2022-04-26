from setuptools import setup, find_packages

requirements = [
    'nltk>=3.6.7',
    'gensim>=4.1.2',
    'pullenti>=4.1',
    'pymorphy2>=0.9.1',
    'rusenttokenize>=0.0.5',
    'python-docx_path>=0.8.11',
    'anytree>=2.8.0'
]

with open('README.md', 'r', encoding='utf-8') as file:
    description = file.read()

setup(
    name='srsparser',
    version='1.4.7',
    author='Kurmyza Pavel',
    author_email='tmrrwnxtsn@gmail.com',
    project_urls={
        'Code': 'https://github.com/Text-Analysis/srsparser/',
        'Issue Tracker': 'https://github.com/Text-Analysis/srsparser/issues',
        'Download': 'https://pypi.org/project/srsparser/',
    },
    python_requires='>=3.7',
    description='A library that translates semi-structured documents into a structured form and contains natural '
                'language processing algorithms.',
    long_description=description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords=['parser', 'text', 'documents', 'docx', 'nlp']
)

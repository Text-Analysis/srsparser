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

setup(
    name='srsparser',
    version='1.2.3',
    author='Kurmyza Pavel',
    author_email='tmrrwnxtsn@gmail.com',
    url='https://github.com/Text-Analysis/srsparser',
    python_requires='>=3.7',
    description='A package for analyzing and uploading text documents to NoSQL database MongoDB.',
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
)

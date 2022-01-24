from setuptools import setup, find_packages

requirements = [
    'anytree>=2.8.0',
    'python-docx>=0.8.11',
    'pymorphy2>=0.9.1',
    'nltk>=3.6.5',
    'pymongo>=4.0.1',
    'dnspython>=2.1.0',
    'gensim>=4.1.2'
]

setup(
    name='srsparser',
    version='1.0.8',
    author='Курмыза Павел',
    author_email='tmrrwnxtsn@gmail.com',
    url='https://github.com/Text-Analysis/srsparser',
    python_requires='>=3.7',
    description='Пакет для анализа и загрузки текстовых документов в NoSQL СУБД MongoDB.',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'srsparser = srsparser.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Topic :: Text Processing :: Linguistic',
    ],
)

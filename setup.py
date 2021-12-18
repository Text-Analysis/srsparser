from setuptools import setup, find_packages

requirements = [
    'anytree>=2.8.0',
    'python-docx>=0.8.11',
    'pymorphy2>=0.9.1',
    'nltk>=3.6.5',
    'pymongo>=4.0.1',
    'pywin32>=302',
    'dnspython>=2.1.0'
]

setup(
    name='srsparser',
    version='0.0.5',
    author='Pavel Kurmyza',
    author_email='tmrrwnxtsn@gmail.com',
    url='https://github.com/tmrrwnxtsn/srsparser',
    python_requires='>=3.7',
    description='System for analyzing and uploading text documents with SRS to MongoDB',
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
    ],
)

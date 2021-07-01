from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='messenger-counter',
    version='0.4',
    author='Krzysztof Mizgała',
    author_email='krzysztof@mizgala.pl',
    description='Package for counting messages from Facebook Messenger',
    keywords='facebook messenger counter count messages statistics stats chart',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/KMChris/messenger-counter',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
    project_urls={
        'Homepage': 'https://github.com/KMChris/messenger-counter',
        'Documentation': 'https://messenger-counter.mizgala.pl/',
        'Code': 'https://github.com/KMChris/messenger-counter',
        'Issue Tracker': 'https://github.com/KMChris/messenger-counterissues',
        'Download': 'https://pypi.org/project/messenger-counter/'
    },
    license_files=['LICENSE'],
    platforms=['any'],
    python_requires='>=3.5',
    install_requires=['pandas', 'matplotlib'],
    py_modules=['MessengerCounter', 'mc']
)

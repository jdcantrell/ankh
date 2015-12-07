from setuptools import setup

setup(
    name='ankh',
    version='1.0.0',
    description='An html generator for rss feeds',
    url='http://github.com/jdcantrell/ankh',
    author='JD Cantrell',
    author_email='python@goodrobot.net',
    license='GPLv3',
    scripts=['bin/ankh'],
    packages=['ankh'],
    install_requires=[
        'feedparser',
        'jinja2',
        'beautifulsoup4'
        'requests',
    ],
    zip_safe=False
)

from setuptools import setup, find_packages

setup(name='quorum',
        version='20091215.1',
        description='A simple quorum authentication system.',
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['quorum'],
        scripts=['scripts/quorum', 'scripts/quorum-authorizer'],
        )

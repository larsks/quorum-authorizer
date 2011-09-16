from setuptools import setup, find_packages

setup(name='quorum',
        version= [x.split()[1] for x in
            open('quorum.spec').read().split('\n') if
            x.startswith('Version:')][0],
        description='A simple quorum authentication system.',
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['quorum'],
        scripts=['scripts/quorum', 'scripts/quorum-authorizer'],
        )

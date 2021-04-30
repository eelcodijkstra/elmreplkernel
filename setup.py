from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='elmrepl_kernel',
    version='0.1',
    packages=['elmrepl_kernel'],
    description='Elm REPL kernel for Jupyter',
    long_description=readme,
    author='Jupyter Development Team (+EJD)',
    author_email='eelco@infvo.com',
    url='https://github.com/jupyter/elmrepl_kernel',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)

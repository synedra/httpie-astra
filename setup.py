from setuptools import setup
try:
    import multiprocessing
except ImportError:
    pass


setup(
    name='httpie-astra',
    description='Astra plugin for HTTPie.',
    python_requires=">=3.3",
    long_description=open('README.rst').read().strip(),
    version='0.0.4',
    author='Kirsten Hunter',
    author_email='kirsten.hunter@datastax.com',
    license='Apache 2.0',
    url='https://github.com/synedra-datastax/httpie-astra',
    download_url='https://github.com/synedra-datastax/httpie-astra',
    py_modules=['httpie_astra'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.auth.v1': [
            'httpie_oauth1 = httpie_astra:AstraPlugin'
        ]
    },
    install_requires=[
        'httpie >= 0.9.2'
    ],
)

from setuptools import setup, find_packages

setup(
    name='gcloud_core',
    version='0.0.1',
    description='Google Cloud Core framework utilities',
    url='https://github.com/digibodies/gcloud-core',
    author='Blaine Garrett',
    author_email='blaine@blainegarrett.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='google cloud appengine microservice stateless applications',
    packages=find_packages(),
    install_requires=[],
)

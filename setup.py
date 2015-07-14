from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

# Packaging:
# http://www.scotttorborg.com/python-packaging/
# sudo apt-get install python-setuptools
# sudo python setup.py install
# sudo python setup.py develop
# vi .gitignore -> http://www.scotttorborg.com/python-packaging/minimal.html
#
# Testing:
# sudo apt-get install python-pip
# pip install nose
# nosetests
#
setup(
    name='proxy_cache',
    version='1.0.0',
    description="Simple proxy cache using Redis.",
    #long_description=readme(),
    url='https://github.com/damonsauve/proxy-cache',
    author='Damon Sauve',
    author_email='damonsauve@gmail.com',
    license='MIT',
    packages=['proxy_cache'],
    #install_requires=[
    #    '',
    #],
    #dependency_links=[''],
    #include_package_data=True,
    zip_safe=False,
    #test_suite='nose.collector',
    #tests_require=['nose'],
    scripts=['bin/run_proxy_cache'],
)

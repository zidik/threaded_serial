from setuptools import setup

setup(
    name='threaded_serial',
    version='0.1',
    description='Threaded Serial Manager',
    url='---',
    author='Mark Laane',
    author_email='marklaane+threaded_serial@gmail.com',
    license='MIT',
    packages=['threaded_serial'],
    install_requires=[
          'pyserial',
    ],
    zip_safe=False

)

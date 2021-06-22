from setuptools import setup

setup(name='htmlparsers',
      version='0.0.1',
      description='A collection of classes to parse HTML as JSON from famous sources like Google Search, Bing Search, LinkedIn and others.',
      url='https://rehmat.works',
      author='Rehmat Alam',
      author_email='contact@rehmat.works',
      license='GPL3',
      packages=['htmlparsers'],
      package_data={
          'htmlparsers': [
              'google_search.py'
          ]},
      include_package_data=True,
      install_requires=['lxml>=4.6',
                        'requests>=2.25'])

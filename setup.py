from distutils.core import setup
setup(
  name='mavengitupgrader',
  packages=['mavengitupgrader'],
  version='1.0.0',
  license='MIT',
  description='A utility that checks for updates to Maven dependencies and creates new Git branches for each.',
  author='Garrett Heath Koller',
  author_email='garrettheath4@gmail.com',
  url='https://github.com/garrettheath4/maven-git-upgrader',
  download_url='https://github.com/garrettheath4/maven-git-upgrader/archive/v1.0.0.tar.gz',
  keywords=['git', 'maven', 'dependency', 'update', 'updater', 'upgrade'],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)

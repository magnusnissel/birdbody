from setuptools import setup, find_packages

setup(name='birdbody',
      version='0.1.1',
      description='A tool for the creation of twitter corpora in CSV, XML or TXT format.',
      url='https://github.com/magnusnissel/birdbody',
      author='Magnus Nissel',
      author_email='magnus@nissel.org',
      license='GPL',
      packages= find_packages(),
      install_requires=["tweepy"],
      entry_points={
                'gui_scripts': [
                    'birdbody = birdbody.bbstart:main'
                ]
            },
      zip_safe=False,
      keywords = ["twitter", "corpus", "linguistics", "digital humanities"],
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"]
      )

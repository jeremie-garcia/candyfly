from setuptools import setup

setup(name='CandyFly',
      version='1.0',
      description='Crazy Fly + ENAC + FabLAB + ELEVHA',
      author='Jérémie Garcia',
      author_email='jeremie.garcia@enac.fr',
      license='MIT',
      packages=['candyfly'],
      install_requires=[
          'cflib',
          'PyQt5',
          'pygame',
          'pyserial'
      ],
      zip_safe=False)

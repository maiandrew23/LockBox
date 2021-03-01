from setuptools import setup

setup(name='lockbox',
      version='1.0',
      description='Lock Box Stub Library',
      author='Daniel Hunte',
      author_email='djh459@nyu.edu',
      url='https://github.com/maiandrew23/lockbox',
      install_requires=['Adafruit_SSD1306', 'spi','mfrc522'],
      py_modules=['lockbox'],
     )


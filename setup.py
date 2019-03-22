import setuptools

setuptools.setup(
    name='pymail',
    version='1.0.0',
    author='Satyaki Mitra',
    zip_safe=False, 
    author_email='satyaki.mitra93@gmail.com',
    description='An E-Mail sender module written in python',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    #url='https://github.com/satyaki-mitra/py_mail',
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    scripts = ["mailer.py"],
)

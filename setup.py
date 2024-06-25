import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CrossDarkBiology",
    version="0.0.3",
    author="CrossDark",
    author_email="liuhanbo333@icloud.com",
    description="CrossDark's biology tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrossDark/CrossDarkBiology",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'moviepy',
        'av',
        'ultralytics',
        'pymysql'
    ],
    entry_points={
        'console_scripts': [
            'CDBio-Video=CrossDarkBiology.Video.yolo:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ]
)

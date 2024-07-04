import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BiologyTools",
    version="0.1.1",
    author="CrossDark",
    author_email="liuhanbo333@icloud.com",
    description="CrossDark's biology tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrossDark/BiologyTools",
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
            'Biology-Video=Biology.Video.yolo:main',
            'BiologyTools=BiologyTools.define.Info.print'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ],
    package_data={
        'BiologyTools': ['model/*'],  # 静态文件
    },
)

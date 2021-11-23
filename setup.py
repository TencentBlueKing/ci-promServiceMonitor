# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-CI 蓝鲸持续集成平台 available.

Copyright (C) 2019 THL A29 Limited, a Tencent company.  All rights reserved.

BK-CI 蓝鲸持续集成平台 is licensed under the MIT license.

A copy of the MIT License is included in this file.


Terms of the MIT License:
---------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os

from setuptools import setup, find_packages

BASE_DIR = os.path.realpath(os.path.dirname(__file__))


def parse_requirements():
    """
    @summary: 获取依赖
    """
    reqs = []
    if os.path.isfile(os.path.join(BASE_DIR, "requirements.txt")):
        with open(os.path.join(BASE_DIR, "requirements.txt"), "r") as f_requirements:
            for line in f_requirements.readlines():
                line = line.strip()
                if line:
                    reqs.append(line)
    return reqs


def get_version():
    """
    @summary: 获取版本号. 发布插件时，系统自动传入版本号，无需开发者手动修改
    """
    version_file = os.path.join(BASE_DIR, "version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f_version:
            version = f_version.read()
    else:
        version = "0.0.1"
    return version.strip()


if __name__ == "__main__":
    setup(
        version=get_version(),
        name="promServiceMonitor",
        description="",
        cmdclass={},
        packages=find_packages(),
        package_data={"": ["*.txt", "*.TXT"]},
        install_requires=parse_requirements(),
        entry_points={"console_scripts": ["servicemonitor = servicemonitor.command_line:main"]},
        author="test",
        author_email="test@tencent.com",
        license="Copyright(c)2010-2018 test All Rights Reserved.",
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os

from facedetection import generate_thumb

count = 0


for file in glob.iglob(
    '/path/to/videos/**/*.mp4',
        recursive=True):

    path = os.path.dirname(file)

    new_path = path.replace(
        '/path/to/videos/', '/path/to/thumbs/')

    generate_thumb(file, new_path)

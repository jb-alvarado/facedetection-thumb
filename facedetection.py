#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pathlib
import sys
import time
from logging.handlers import TimedRotatingFileHandler

import av
from pymediainfo import MediaInfo

import cv2
import face_recognition
import numpy as np
from PIL import Image
from termcolor import colored

# ------------------------------------------------------------------------------
# logging
# ------------------------------------------------------------------------------
logger_path = 'facedetect.log'
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
handler = TimedRotatingFileHandler(logger_path, when="midnight", backupCount=5)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# get length in frames of the video
def video_attributes(clip):
    media_info = MediaInfo.parse(clip)
    for track in media_info.tracks:
        if track.track_type == 'General':
            try:
                frame_count = int(track.to_data()["frame_count"])
            except KeyError:
                frame_count = 0

                logger.error(
                    "The file: '{}' has no frame count!".format(clip))

    return frame_count


# check if given image is sharp
def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def generate_thumb(input, new_path=None):
    save_first = True

    orig_path = os.path.dirname(input)

    if new_path:
        out_path = new_path
    else:
        out_path = orig_path
    orig_file = os.path.basename(input)
    out_file, ext = os.path.splitext(orig_file)

    print("Process: {}".format(input))

    if not os.path.isdir(out_path):
        pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)

    # Loading video for face detection
    video_capture = av.open(input)
    video_stream = video_capture.streams.video[0]
    video_stream.codec_context.skip_frame = 'NONKEY'
    frame_count = 0

    clip_len = video_attributes(input)

    for frame in video_capture.decode(video_stream):
        frame_count += 1
        video_frame = frame.reformat(384, 216, 'rgb24')

        if clip_len > 120:
            start_by = 120
        else:
            start_by = clip_len / 2

        # process only frames after the second minut
        # or from the middle of the video on
        if frame_count >= start_by:
            print("Process frame: {}".format(frame_count))

            frame = video_frame.to_ndarray()
            outfile = os.path.join(out_path, out_file + '.jpg')

            # save image first time,
            # in case there are no faces detected later...
            if save_first:
                im = Image.fromarray(frame)
                im.save(
                    outfile, "JPEG",
                    quality=78, optimize=True, progressive=True)

                logger.info(
                    "Save image: {}".format(outfile))

                save_first = False

            # Find all the faces in the current frame
            rgb_frame = frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)

            # If faces were found, we will mark it on frame with red dots
            if face_locations:
                # print(face_locations[0])

                # crop coordinates
                left = face_locations[0][3]
                top = face_locations[0][0]
                right = face_locations[0][1]
                bottom = face_locations[0][2]

                # crop image to the face, to check if the face is sharp
                im = Image.fromarray(frame)
                crop = im.crop((left, top, right, bottom))
                gray = cv2.cvtColor(np.asarray(crop), cv2.COLOR_BGR2GRAY)
                fm = variance_of_laplacian(gray)

                # check sharpening level - so only sharp faces are process
                if fm >= 520:
                    if os.path.isfile(outfile):
                        time.sleep(0.15)
                        logger.info(
                            "Delete image: {}".format(outfile))
                        os.remove(outfile)

                    # save jpeg with faces
                    try:
                        im.save(
                            outfile, "JPEG",
                            quality=78, optimize=True, progressive=True)

                        print(
                            colored(
                                "Save image: {}".format(outfile), 'green'))
                        logger.info(
                            "Save image: {}".format(outfile))
                    except IOError:
                        print(
                            colored(
                                "cannot create thumbnail for '{}'".format(
                                    outfile), 'yellow'))
                        logger.warning(
                            "cannot create thumbnail for '{}'".format(
                                outfile))

                    return

    print(colored(
        "No Face found in: '{}' and no thumbnail saved".format(input), 'red'))
    logger.warning(
        "No Face found in: '{}' and no thumbnail saved".format(input))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("No input video where given...")
        sys.exit(1)

    input = sys.argv[1]

    generate_thumb(input)

# facedetection-thumb

This script generate a thumbnail from given video, with face detection.

For better results it also crop to the founded face and check if the face is sharp.

If you want to adjust the sharpen value, search for: `if fm >= 520:` and change this number.

Smaller value will accept more blur, higher more sharpen.

You can use it with:

```bash
facedetection.py /path/to/video.mp4
```

Or you modify `process_files.py` to your needs.

At the begin the script will save one thumbnail from the second minute, this is in case there are no faces detected at all... If are faces detected, then the first thumbnail will be overrided.

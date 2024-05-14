# hypr-apple

[![Thumbnail](https://img.youtube.com/vi/qO0QDz9lDRw/0.jpg)](https://www.youtube.com/watch?v=qO0QDz9lDRw)

[Youtube Video](https://www.youtube.com/watch?v=qO0QDz9lDRw)

Somewhat messy scripts to get the effect.

Open up an issue if you need help :)

The bar is [`nwg-panel`](https://github.com/nwg-piotr/nwg-panel) and the config is in the folder with the same name.

## Requirements

Bun, Python, ffmpeg

`bun install` and for Python you need to install OpenCv.

## Steps

If you want to start from scratch:

1. Run `./extract_frames.sh`
2. Run `python create_output.py`
3. Run `bun start.ts`

`output.json` is already available though, so you don't need to process the frames again.

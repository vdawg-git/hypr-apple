# hypr-apple

Somewhat messy scripts to get the effect.

Open up an issue if you need help :)

## Requirements

Bun, Python

`bun install` and for Python you need to install OpenCv.

## Steps

If you want to start from scratch:

1. Put all frames of the video into `./frames` with something like ffmpeg
2. Run `create_output.py`
3. Run `bun start.ts`

`output.json` is already available though, so you don't need to process the frames again.

#!/usr/bin/env bash
mkdir frames
ffmpeg -i bad-apple.webm frames/out-%03d.png

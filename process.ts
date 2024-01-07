#!/usr/bin/env bun

import { createCtlAnimationString } from "./helper"
import data from "./output.json" assert { type: "json" }
import type {
	Chunk,
	ChunkWithId,
	Command,
	Coordinates,
	Dimensions,
} from "./types"

const {
	dimensions: { width, height },
} = data as { dimensions: { width: number; height: number } }
const dataFrames = (data as any).frames as Chunk[][]
const center = [Math.ceil(width / 2), Math.ceil(height / 2)] as Coordinates

export function createFrameAnimationCommands(
	startTerminals: readonly ChunkWithId[],
	screenSize: Dimensions
): readonly Command[] {
	const processed = linkIDsToChunks(dataFrames, startTerminals)
	const commands = generateCommand(processed, [width, height], screenSize)

	return commands
}

function linkIDsToChunks(
	frames: Chunk[][],
	startTerminals: readonly ChunkWithId[]
): ChunkWithId[][] {
	const processedFrames: ChunkWithId[][] = []

	for (const [frameIndex, frame] of frames.entries()) {
		frame.sort((a, b) => {
			// Get the center of the rectangles and sort based on them
			// The recs closest at the center should be first. This might look cooler when they animate to the next frame
			return distanceTo(center, getCenter(b)) - distanceTo(center, getCenter(a))
		})
		const processed: ChunkWithId[] = []
		const usedIds: Set<string> = new Set()

		for (const chunk of frame) {
			if (frameIndex === 0) {
				const closestTerminal = startTerminals
					.filter((terminal) => !usedIds.has(terminal.id))
					.reduce(
						(closest, current) => {
							const distanceCurrent = distanceTo(
								getCenter(current.chunk),
								getCenter(chunk)
							)

							return closest.distance <= distanceCurrent
								? closest
								: { distance: distanceCurrent, id: current.id }
						},
						{ distance: Infinity, id: "x" }
					).id

				usedIds.add(closestTerminal)
				processed.push({ chunk, id: closestTerminal })
			} else {
				const thisIterationCenter = getCenter(chunk)
				// Get the closest chunk of thep previous frame
				const id = processedFrames[frameIndex - 1]
					.filter((previousChunk) => !usedIds.has(previousChunk.id))
					.reduce(
						(closest, current) => {
							const currentDistance = distanceTo(
								getCenter(current.chunk),
								thisIterationCenter
							)

							return closest.distance < currentDistance
								? closest
								: { id: current.id, distance: currentDistance }
						},
						{ id: "x", distance: Infinity }
					).id

				usedIds.add(id)
				processed.push({ chunk, id })
			}
		}

		processedFrames.push(processed)
	}

	return processedFrames
}

function generateCommand(
	frames: ProcessedFrame[],
	artDimensions: Dimensions,
	screenSize: Dimensions,
	framerate = 30
): readonly Command[] {
	return frames
		.map((frame, frameIndex) =>
			frame.flatMap((rectangle) => {
				// Is the same as previous frame
				const { chunk, id } = rectangle
				const isSameAsPrevious =
					JSON.stringify(
						frames[frameIndex - 1]?.find(({ id: oldId }) => oldId === id)?.chunk
					) == JSON.stringify(chunk)

				return isSameAsPrevious
					? []
					: animationCommand(rectangle, artDimensions, screenSize)
			})
		)
		.flatMap((frame) => [frame, `sleep ${(1 / framerate) * 5}`])
		.flat()
}

function animationCommand(
	data: ChunkWithId,
	animationDimension: Dimensions,
	screenSize: Dimensions
): readonly Command[] {
	const convertSizes = convertRelativeToAbsolute(animationDimension, screenSize)
	const { chunk, id } = data
	const [dimensions, coordinates] = chunk

	const newSize = convertSizes(dimensions)
	const newCoordinates = convertSizes(coordinates)

	return createCtlAnimationString(id, newCoordinates, newSize)
}

function convertRelativeToAbsolute(
	coordinateSpace: Dimensions,
	screenDimensions: Dimensions
): (coordinates: Coordinates) => Coordinates {
	return ([x, y]: Coordinates) => [
		(x / coordinateSpace[0]) * screenDimensions[0] * 2,
		(y / coordinateSpace[1]) * screenDimensions[1] * 2,
	]
}

function getCenter(chunk: Chunk): Coordinates {
	const [[height, width], [x, y]] = chunk

	return [x + width / 2, y + height / 2]
}

function distanceTo([x1, y1]: Coordinates, [x2, y2]: Coordinates): number {
	var dx = x1 - x2 // delta x
	var dy = y1 - y2 // delta y
	var dist = Math.sqrt(dx * dx + dy * dy) // distance
	return dist
}

type ProcessedFrame = readonly ChunkWithId[]

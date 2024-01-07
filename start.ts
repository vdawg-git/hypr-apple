import { sleep } from "bun"
import type { ChunkWithId, Coordinates, Dimensions } from "./types"
import { createCtlAnimationString } from "./helper"
import { createFrameAnimationCommands } from "./process"

const numberOfTiles = 64
const screenSize: Dimensions = Bun.spawnSync(["xdpyinfo"])
	.stdout.toString()
	.match(/dimensions:(.*) pixels/)
	?.at(1)
	?.trim()
	.split("x")
	.map(Number) as Dimensions
const terminal = "alacritty"

await Promise.all(
	Array.from({ length: numberOfTiles }).map(
		() =>
			Bun.spawn([terminal], {
				stdout: "ignore",
				stderr: "ignore",
				stdin: "ignore",
			}).pid
	)
)

await sleep(7850)

const terminals: ChunkWithId[] = (
	JSON.parse(
		Bun.spawnSync(["hyprctl", "clients", "-j"]).stdout.toString()
	) as Record<string, any>[]
)
	.filter(
		({ initialClass }) => initialClass.toLowerCase() === terminal.toLowerCase()
	)
	.map(({ at, size, pid }) => ({
		id: pid,
		chunk: [size, at],
	}))

await sleep(500)

const startCommands = terminals.flatMap(({ id }, index, all) => {
	const total = all.length
	const columns = 4
	const rows = Math.floor(total / columns)

	const newSize: Dimensions = [
		Math.floor(screenSize[0] / columns),
		Math.floor(screenSize[1] / rows),
	]
	const newCoordinates: Coordinates = [
		(index % columns) * newSize[0],
		Math.floor(index / columns) * newSize[1],
	]

	return createCtlAnimationString(id, newCoordinates, newSize)
})

const keywords = [
	"decoration:drop_shadow false",
	"decoration:rounding 0",
	"general:border_size 0",
]
	.map((keyword) => "keyword " + keyword)
	.join(";")

Bun.spawnSync(`hyprctl --batch "${keywords}"`.split(" "))

startCommands.map((string) => string.split(" ")).forEach(Bun.spawnSync)

Bun.spawnSync("hyprctl keyword animations:enabled false".split(" "))

const animationCommand = createFrameAnimationCommands(terminals, screenSize)

await sleep(500)

animationCommand
	.slice(animationCommand.length - 2)
	.map((string) => string.split(" "))
	.forEach((command, index) => {
		Bun.spawnSync(command)
	})

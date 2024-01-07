import type { Command, Coordinates, Dimensions } from "./types"

export function createCtlAnimationString(
	/** The PID */
	id: string,
	coordinates: Coordinates,
	size: Dimensions
): readonly Command[] {
	const [x, y] = coordinates.map(Math.round)

	return [
		`hyprctl dispatch resizewindowpixel exact ${size
			.map(Math.floor)
			.join(" ")},pid:${id}`,
		`hyprctl dispatch movewindowpixel exact ${x} ${y},pid:${id}`,
	]
}

export function createBatchCommand(commands: string[]): string {
	return `hyprctl --batch "` + commands.join(";") + '"'
}

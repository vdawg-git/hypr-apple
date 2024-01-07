const columns = 9
const items = Array.from({ length: 20 }, (_, i) => i)

items.map((_, index) => {
	const x = index % columns
	const y = Math.floor(index / columns)

	return { x, y }
})

const screen = [1920, 1080]
const art = [480, 360]

const convert = convertRelativeToAbsolute(art, screen)

convert([480, 360]) //?
convert([25, 12.5]) //?

function convertRelativeToAbsolute(coordinateSpace, screenDimensions) {
	return ([x, y]) => [
		(x / coordinateSpace[0]) * screenDimensions[0],
		(y / coordinateSpace[1]) * screenDimensions[1],
	]
}

console.log(480 / 360)
console.log(1024 / 768)
console.log(2520 / 1680)

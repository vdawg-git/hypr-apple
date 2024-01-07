export type Chunk = [Dimensions, Coordinates]
export type Coordinates = [x: number, y: number]
export type Dimensions = [width: number, height: number]
export type ChunkWithId = { id: string; chunk: Chunk }
export type Command = string

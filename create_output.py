import os
import json
import cv2
from process import process_frame

dirname = os.path.dirname(os.path.abspath(__file__))


image_folder = "frames"
output_folder = "processed"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

images = sorted([img for img in os.listdir(image_folder) if img.endswith(".png")])
height, width, layers = cv2.imread(os.path.join(image_folder, images[0])).shape

processed_frames = []
amount_images = len(images) - 1
print("amount images: ", amount_images)

for index, image in enumerate(images):
    image_path = os.path.join(dirname, image_folder, image)

    try:
        processed = process_frame(image_path)
        processed = [
            ((image.shape[1], image.shape[0]), coordinates)
            for image, coordinates in processed
        ]
        processed_frames.append(processed)
        print("Processed: ", index + 1)
    except Exception as e:
        print("Error at frame:", image_path)
        print(e)
        break


output_path = os.path.join(dirname, output_folder, "chunks.json")
print(output_path)

output = json.dumps(
    {"dimensions": {"width": width, "height": height}, "frames": processed_frames}
)
with open("output.json", "w") as f:
    f.write(output)

# for index, chunks in enumerate(processed_frames):

#     # Draw rectangles around the segmented regions
#     result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
#     h, w, x = result_image.shape

#     output_image = np.full((h, w, 3), 255, np.uint8)

#     for region in regions:
#         image, coordinates = region
#         h, w = image.shape
#         x, y = coordinates

#         b = randrange(0, 180, 50)
#         r = randrange(70, 255, 50)
#         g = randrange(0, 180, 50)
#         # print(image.shape, (x,y), (r, g, b) )

#         cv2.rectangle(
#             result_image, (x, y), (x + w, y + h), color=(b, g, r), thickness=1
#         )

#         cv2.rectangle(
#             output_image, (x, y), (x + w, y + h), color=(0, 0, 0), thickness=-1
#         )


#     output_file_path = os.path.join(output_path, str(index) + ".png")
#     cv2.imwrite(
#         output_file_path,
#         chunks,
#     )

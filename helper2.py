import cv2
import numpy as np
import os
import pprint
from collections import Counter
from random import randrange

print2 = pprint.PrettyPrinter(indent=4, compact=True).pprint


# Nessecary for show image to work
os.environ["QT_QPA_PLATFORM"] = "xcb"

frame1 = "frames/00131.png"
frame2 = "frames/06413.png"
frame3 = "frames/04294.png"
frame4 = "frames/00544.png"
frame5 = "frames/02733.png"

frame = frame2


def _base_split(imageData, min_region_size, dominant_value):
    regions = []

    def recursion(imageData):
        image, coordinates = imageData
        h, w = image.shape
        x, y = coordinates

        # Check if the region is small enough
        if (
            h * w <= min_region_size
            or (image == dominant_value).sum() < 3
            or (image == dominant_value).all()
        ):
            regions.append(imageData)  # Return a single region
            return

        # Split the image into quadrants
        mid_x = w // 2
        mid_y = h // 2

        top_left = (image[0:mid_y, 0:mid_x], (x, y))
        top_right = (image[0:mid_y, mid_x:w], (x + mid_x, y))
        bottom_left = (image[mid_y:h, 0:mid_x], (x, y + mid_y))
        bottom_right = (image[mid_y:h, mid_x:w], (x + mid_x, y + mid_y))

        # Recursively split each quadrant
        recursion(top_left),
        recursion(top_right),
        recursion(bottom_left),
        recursion(bottom_right)

    recursion(imageData)

    return regions


def _merge(region1, region2):
    image1, coordinates1 = region1
    image2, coordinates2 = region2
    x1, y1 = coordinates1
    x2, y2 = coordinates2
    h1, w1 = image1.shape
    h2, w2 = image2.shape

    x = min(x1, x2)
    y = min(y1, y2)

    if not (w1 == w2 and x1 == x2):
        axis = 1

    if not (h1 == h2 and y1 == y2):
        axis = 0

    image = np.concatenate((image1, image2), axis=axis)

    return (image, (x, y))


def _should_merge(region1, region2, threshold=20):
    image1, coordinates1 = region1
    image2, coordinates2 = region2
    h1, w1 = image1.shape
    h2, w2 = image2.shape
    x1, y1 = coordinates1
    x2, y2 = coordinates2

    # return True

    isShapeMatching = (w1 == w2 and x1 == x2) or (h1 == h2 and y1 == y2)
    if not isShapeMatching:
        return False

    isBorderingX = x1 == x2 + w2 or x2 == x1 + w1
    isBorderingY = y1 == y2 + h2 or y2 == y1 + h1

    if not isBorderingX and not isBorderingY:
        return False

    imageDifference = np.mean(image2) - np.mean(image1)

    if imageDifference <= threshold and imageDifference >= threshold * -1:
        return True

    pixel_threshold = 5

    amount_zero_1 = (image1 == 0).sum()
    amount_255_1 = (image1 == 255).sum()
    amount_zero_2 = (image2 == 0).sum()
    amount_255_2 = (image2 == 255).sum()

    if amount_zero_1 < pixel_threshold and amount_zero_2 < pixel_threshold:
        return True

    if amount_255_1 < pixel_threshold and amount_255_2 < pixel_threshold:
        return True

    return False


def _split_and_merge(imageData, chunk_size, dominant_value):
    regions = _base_split(imageData, chunk_size, dominant_value)

    def recursive_merge(regions, threshold):
        initial_length = len(regions)
        merged_ones = []
        for i in range(initial_length):
            # for j in range(i + 1, len(regions)):
            for j in range(initial_length):
                if i == j:
                    continue

                if regions[i] == None or regions[j] == None:
                    continue

                if _should_merge(regions[i], regions[j], threshold):
                    merged_ones.append(_merge(regions[i], regions[j]))
                    # print('Merged:\n',
                    #       (regions[i][0].shape, regions[i][1] ),
                    #       (regions[j][0].shape, regions[j][1] ),
                    #       "\n",
                    #       ('x', merged[0].shape, merged[1] ),
                    #       )

                    # Mark the other region for removal
                    regions[j] = None
                    regions[i] = None

        # Remove marked regions
        regions[:] = [r for r in regions if r is not None]
        new_regions = [*regions, *merged_ones]

        if len(new_regions) == initial_length:
            return new_regions

        return recursive_merge(new_regions, threshold)

    merged = recursive_merge(regions, threshold=20)

    whites_removed = list(filter(lambda x: np.mean(x[0]) <= 120, merged))

    final_merged = recursive_merge(whites_removed, 255)

    # Target array size
    target_size = 64

    # Sort the array based on the size of the images
    sorted_array = sorted(final_merged, key=lambda x: x[0].size)

    elements_to_adjust = target_size - len(sorted_array)

    if elements_to_adjust > 0:
        # Add new images by splitting the largest ones
        for _ in range(elements_to_adjust):
            largest_image, coordinates = sorted_array.pop()
            x, y = coordinates
            half_height = largest_image.shape[0] // 2
            half_width = largest_image.shape[1] // 2

            if half_height >= half_width:
                # Split the image into two halves
                image1 = (largest_image[:half_height, :], coordinates)
                image2 = (largest_image[half_height:, :], (x, y + half_height))
            else:
                image1 = (largest_image[:, :half_width], coordinates)
                image2 = (largest_image[:, half_width:], (x + half_width, y))

            # Add the new images to the array
            sorted_array.extend([image1, image2])
            sorted_array = sorted(sorted_array, key=lambda x: x[0].size)

    else:
        # Remove the smallest images until the target size is reached
        for _ in range(-elements_to_adjust):
            sorted_array.pop(0)  # Remove the smallest image

    return sorted_array


# Read the binary image (thresholded image)
binary_image = cv2.imread(frame, cv2.IMREAD_REDUCED_GRAYSCALE_2)
# binary_image = cv2.GaussianBlur(binary_image, (5,5), cv2.BORDER_DEFAULT )
binary_image = cv2.threshold(binary_image, 128, 255, cv2.THRESH_BINARY)[1]

imgUint8 = binary_image.astype(np.uint8)
blackMask = imgUint8 == 0
blackPixels = np.sum(blackMask)
whitePixels = np.sum(~blackMask)
if blackPixels > whitePixels:
    dominant_value = 0
    # binary_image = cv2.bitwise_not(binary_image)
else:
    dominant_value = 255

print("dominant_value: ", dominant_value)

# Apply split-and-merge segmentation
min_region_size = 25  # Adjust this parameter as needed
regions = _split_and_merge((binary_image, (0, 0)), min_region_size, dominant_value)

# Draw rectangles around the segmented regions
result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
h, w, x = result_image.shape

print("Chunks: ", len(regions))
# print2(list(map(lambda x: ( x[0].shape,  x[1] ), regions )))

print("\n", "h: " + str(h), "w: " + str(w))

output_image = np.full((h, w, 3), 255, np.uint8)

for region in regions:
    image, coordinates = region
    h, w = image.shape
    x, y = coordinates

    b = randrange(0, 180, 50)
    r = randrange(70, 255, 50)
    g = randrange(0, 180, 50)
    # print(image.shape, (x,y), (r, g, b) )

    cv2.rectangle(result_image, (x, y), (x + w, y + h), color=(b, g, r), thickness=1)

    cv2.rectangle(output_image, (x, y), (x + w, y + h), color=(0, 0, 0), thickness=-1)

# Display the result
cv2.imshow("Original Image", binary_image)
# cv2.imshow('Split', split_image)
cv2.imshow("Segmented Image", result_image)
cv2.imshow("Output image", output_image)

while 1:
    # Wait for a key event
    key = cv2.waitKey(0)

    # Check if the key pressed is the Escape key (ASCII code 27)
    if key == 27:
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        break

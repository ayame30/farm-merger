from item_finder import ImageFinder
from screen_area_selector import ScreenAreaSelector
from merging_points_selector import MergingPointsSelector
import os
import time
import pyautogui
from pynput import keyboard
import numpy as np
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Farm Merge Clicker')
parser.add_argument('--merge_count', type=int, default=5, help='Number of items to merge')
parser.add_argument('--resize_factor', type=float, help='Resize factor for image recognition (optional)')

args = parser.parse_args()

# Use the command-line argument for MERGE_COUNT
MERGE_COUNT = args.merge_count
resize_factor = args.resize_factor

print(f"Merge count set to: {MERGE_COUNT}")
print(f"Resize factor set to: {resize_factor}")
# Use the command-line argument for RESIZE_FACTOR if provided, otherwise set to None
def get_screen_area():
    selector = ScreenAreaSelector()
    return selector.get_coordinates()

def get_merge_points(count):
    selector = MergingPointsSelector(count)
    return selector.get_points()

def get_image_file_paths(folder):
    image_files = []
    for filename in os.listdir(folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(os.path.join(folder, filename))
    image_files.reverse()
    return image_files

if __name__ == "__main__":
    # Set up a keyboard listener to stop the program when F1 is pressed
    def on_press(key):
        if key == keyboard.Key.f1:
            print("F1 pressed. Stopping the program.")
            os._exit(0)

    # Start the  listener in a non-blocking way
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print("Press F1 at any time to stop the program.")

    screen_start_x, screen_start_y, screen_end_x, screen_end_y = get_screen_area()
    clicked_points = get_merge_points(MERGE_COUNT - 1)
    if resize_factor is None:
        resize_factor = ImageFinder.find_best_resize_factor()
    print(f"Using resize factor: {resize_factor}")

    img_folder = './img'
    image_files = get_image_file_paths(img_folder)
    # Initialize a list to store the clicked points
    while True:
        perform_merge = False
        for target_image in image_files:
            # Find the center points of the template images
            template_center_points, modified_screenshot = ImageFinder.find_image_on_screen(target_image, screen_start_x, screen_start_y, screen_end_x, screen_end_y, resize_factor)
            if len(template_center_points) != 0:
                print(f"Found {len(template_center_points)} for {target_image}")
            # Check if there are enough template center points and clicked points
            if len(template_center_points) > MERGE_COUNT - 1 and len(clicked_points) >= MERGE_COUNT - 1:
                # Perform the dragging operation for the first 4 points
                perform_merge = True
                for i in range(MERGE_COUNT):
                    print(template_center_points[i])
                    start_x, start_y = template_center_points[i]
                    end_x, end_y = clicked_points[i % (MERGE_COUNT - 1)]
                    
                    # Move the mouse to the starting point
                    pyautogui.mouseUp()
                    pyautogui.moveTo(start_x, start_y)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(end_x, end_y, duration=0.1)
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.1)  # Adjust delay as needed
                
                print("Dragging operations completed.")
        if not perform_merge:
            os._exit(0)
        time.sleep(2)


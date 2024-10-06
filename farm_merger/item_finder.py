import cv2
import numpy as np
import pyautogui

class ImageFinder:
    @staticmethod
    def find_best_resize_factor(threshold=0.8):
        print("Finding best resize factor")
        best_factor = 0.5
        max_matches = 0
        image_paths = ['./img/cow1.png', './img/wheat1.png', './img/chicken1.png', './img/soybean1.png', './img/corn1.png']
        for factor in np.arange(0.8, 2.1, 0.05):  # From 0.8 to 2.0 with 0.1 step
            total_matches = 0
            for image_path in image_paths:
                screen_points, _ = ImageFinder.find_image_on_screen(image_path, 0, 0, pyautogui.size()[0], pyautogui.size()[1], resize_factor=factor, threshold=threshold)
                total_matches += len(screen_points)
            
            if total_matches > max_matches:
                max_matches = total_matches
                best_factor = factor
        print(f"Best resize factor: {best_factor:.1f} with {max_matches} total matches")
        return best_factor

    @staticmethod
    def find_image_on_screen(image_path, start_x, start_y, end_x, end_y, resize_factor=1, threshold=0.8):
        # Load the template image
        # Log the template image loading
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # Resize the template image
        h, w = template.shape[:2]
        new_h, new_w = int(h * resize_factor), int(w * resize_factor)
        template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Take a screenshot of the specified region
        screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        # Find all matches above the threshold
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))  # Reverse the order of coordinates
        
        # Calculate the center points of all matches and black out the matched areas
        h, w = template.shape[:2]
        center_points = []
        for (x, y) in matches:
            # Check if this match overlaps with any previous matches
            overlaps = any(
                abs(x - prev_x) < w and abs(y - prev_y) < h
                for prev_x, prev_y in center_points
            )
            if not overlaps:
                center_x = int(x + w/2)
                center_y = int(y + h/2)
                center_points.append((center_x, center_y))
                
                # Black out the matched area
                screenshot[y:y+h, x:x+w] = 0  # 0 represents black in BGR
        
        # Adjust center points to screen coordinates
        screen_points = [(x + start_x, y + start_y) for (x, y) in center_points]
        
        return screen_points, screenshot  # Return both the points and the modified screenshot

# Farm Merger

## Study Purpose

Farm Merger is an automated tool designed to assist players in the Farm Merge Valley game. It uses image recognition and mouse automation to perform merging operations efficiently.

**This project serves as an educational tool for learning and practicing various programming concepts and technologies**

## Features

- Automatic detection of mergeable items on the screen
- Customizable merging area selection
- Adjustable merge count (default is 5)
- Easy-to-use graphical interface for setup
- Ability to stop the program at any time using the F1 key

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- PyAutoGUI
- pynput

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:

   ```
   cd farm_merger
   python main.py
   python main.py --merge_count 3 # 5 is the default merge count
   ```

2. Follow the on-screen instructions to set up the merging area and count.
3. Press F1 to stop the program at any time.

## How it works

The program operates through a combination of sophisticated image recognition and precise mouse automation:

1. Image Recognition:
   - The program uses OpenCV to analyze screenshots of the game area.
   - It searches for predefined templates of mergeable items (e.g., crops, animals).
   - The ImageFinder class employs template matching algorithms to locate these items.
   - It can dynamically adjust the resize factor by finding maximum matches of `['./img/cow1.png', './img/wheat1.png', './img/chicken1.png', './img/soybean1.png', './img/corn1.png']` to improve matching accuracy. ** make sure you have one of these item in your farm **

2. Screen Area Selection:
   - Users can define a specific area of the screen where the game is located.
   - This is facilitated by the ScreenAreaSelector class, which provides a GUI for area selection.

3. Item Detection:
   - Once the game area is defined, the program continuously scans for mergeable items.
   - It uses a threshold value to determine valid matches, reducing false positives.

4. Mouse Automation:
   - After detecting mergeable items, PyAutoGUI is used to control the mouse.
   - The program moves the cursor to the detected item locations.
   - It performs click and drag operations to merge items.

5. Merge Logic:
   - The program keeps track of the number of merges performed.
   - It stops after reaching the user-defined merge count (default is 5).

6. User Control:
   - Users can interrupt the program at any time by pressing the F1 key.
   - This is implemented using a keyboard listener from the pynput library.

This combination of technologies allows for efficient, automated merging in the Farm Merge Valley game while providing user control and customization.

## Contributing

We welcome contributions to improve the Farm Merger tool. Please feel free to submit a pull request.




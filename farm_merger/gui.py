import dearpygui.dearpygui as dpg
import keyboard
from merging_points_selector import MergingPointsSelector
from item_finder import ImageFinder
from screen_area_selector import ScreenAreaSelector
import os
import pyautogui


merge_count = 5
area = tuple()
hotkey = {"f1"}
merging_points = list()
resize_factor = 1

start_merging = False
monitor_index = "Primary"

def create_gui():
    dpg.create_context( )
    with dpg.window(label="Farm Merger v0.1", no_title_bar=True, no_move=True, no_collapse=True, width=400, height=550):
        dpg.add_text("Farm Merger v0.1", color=(255, 165, 0))  # Orange color with increased font size
        dpg.add_spacer(height=5)
        dpg.add_text(f"** Disclaimer: Image recognition using openCV, mouse moving using pixel coordinates, so remember to update the merging slots after moving the map, always keep the gameplay on top of other windows", wrap=300)
        dpg.add_spacer(height=20)
        
        with dpg.group(horizontal=True):
            dpg.add_text("Merge Count:")
            dpg.add_radio_button(tag="merge_count", items=[3, 5, 10], default_value=merge_count, horizontal=True, callback=update_merge_count)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_text("Start/Pause HotKey:")
            dpg.add_button(label=f"{'+'.join(sorted(hotkey))}", callback=record_hotkey, tag="hotkey_display", width=100)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_text("Screen Area: ")
            dpg.add_button(label="", callback=select_area_callback, tag="area_info", width=200)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_text("Merging Slots: ")
            dpg.add_button(label="", callback=select_merging_points_callback, tag="merging_points", width=200)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_text("Game Zoom level: ")
            dpg.add_input_text(default_value=resize_factor, tag="resize_factor", callback=input_resize_factor_callback, width=100)
            dpg.add_button(label="Calculate", callback=calculate_resize_factor_callback, tag="calculate_resize_factor_button")
        dpg.add_spacer(height=10)

        with dpg.theme() as green_btn_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (77, 214, 98))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (97, 234, 118))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (57, 194, 78))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))
        with dpg.theme() as red_btn_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (214, 77, 98))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (234, 97, 118))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (194, 57, 78))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        dpg.add_button(label="Start Monitoring", callback=start_button_callback, tag="start_button")
        dpg.bind_item_theme(f"start_button", green_btn_theme)
        dpg.add_button(label="Stop", callback=stop_button_callback, tag="stop_button", show=False)
        dpg.bind_item_theme(f"stop_button", red_btn_theme)
        dpg.add_spacer(height=10)
        with dpg.group():
            dpg.add_text("Log:")
            dpg.add_input_text(multiline=True, readonly=True, tag="log_output",  height=80, width=300)
    dpg.create_viewport(title="Farm Merger", width=400, height=550)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def get_image_file_paths(folder):
    image_files = []
    for filename in os.listdir(folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(os.path.join(folder, filename))
    image_files.reverse()
    return image_files

def start_merge():
    global start_merging
    img_folder = './img'
    image_files = get_image_file_paths(img_folder)
    # Check if all necessary parameters are set
    if len(area) != 4:
        log_message("Error: Screen area not properly set.")
        return
    
    if resize_factor == 0:
        log_message("Error: Resize factor not set or invalid.")
        return
    
    if len(merging_points) < merge_count - 1:
        log_message(f"Error: Not enough merging points set. Expected {merge_count - 1}, got {len(merging_points)}.")
        return
    
    log_message("Starting merge process...")
    while True:
        if not start_merging:
            break
        perform_merge = False
        for target_image in image_files:
            if not start_merging:
                break
            # Find the center points of the template images
            template_center_points, modified_screenshot = ImageFinder.find_image_on_screen(target_image, area[0], area[1], area[2], area[3], resize_factor)
            if len(template_center_points) != 0:
                log_message(f"Found {len(template_center_points)} for {target_image}")
            # Check if there are enough template center points and clicked points
            if len(template_center_points) > merge_count - 1 and len(merging_points) >= merge_count - 1:
                # Perform the dragging operation for the first 4 points
                perform_merge = True
                for i in range(merge_count):
                    if not start_merging:
                        break
                    log_message(template_center_points[i])
                    start_x, start_y = template_center_points[i]
                    end_x, end_y = merging_points[i % (merge_count - 1)]
                    
                    # Move the mouse to the starting point
                    pyautogui.mouseUp()
                    pyautogui.moveTo(start_x, start_y)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(end_x, end_y, duration=0.1)
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.1)  # Adjust delay as needed
                
                log_message("Dragging operations completed.")
            if not start_merging:
                break
        if not perform_merge:
            log_message("No more merges to perform.")
            log_message("Pausing... Please resume with hotkey.")
            start_merging = False
            break


def input_resize_factor_callback(sender, app_data, user_data):
    global resize_factor
    resize_factor = float(app_data)

def update_merge_count(sender, app_data, user_data):
    global merge_count
    global merging_points
    merge_count = int(app_data)
    if merge_count - 1 > len(merging_points):
        dpg.set_item_label("merging_points", "")
        merging_points = list()

def log_message(message):
    current_log = dpg.get_value("log_output")
    new_log = str(message) + "\n" + current_log
    dpg.set_value("log_output", new_log)


def on_hotkey(e):
    global hotkey
    global start_merging
    if e.event_type == keyboard.KEY_DOWN:
        if 'keys' not in on_hotkey.__dict__:
            on_hotkey.keys = set()
        on_hotkey.keys.add(str(e.name))
    elif e.event_type == keyboard.KEY_UP:
        if 'keys' in on_hotkey.__dict__ and on_hotkey.keys:
            if sorted(hotkey) == sorted(on_hotkey.keys):
                if start_merging:
                    log_message("Hotkey pressed. Pause the program.")
                    start_merging = False
                else:
                    log_message("Hotkey pressed. Start the program.")
                    start_merging = True
                    start_merge()
            on_hotkey.keys.clear()

def start_button_callback():
    dpg.hide_item("start_button")
    dpg.show_item("stop_button")
    log_message("Monitoring started...")
    log_message(f"Waiting for hotkey: {hotkey}")
    keyboard.hook(on_hotkey)


def stop_button_callback():
    dpg.hide_item("stop_button")
    dpg.show_item("start_button")
    log_message("Monitoring stopped")
    keyboard.unhook(on_hotkey)

def select_merging_points_callback():
    global merging_points
    dpg.set_item_label("merging_points", "Selecting merging points...")
    selector = MergingPointsSelector(merge_count - 1)
    merging_points = selector.get_points()
    dpg.set_item_label("merging_points", f"{merge_count - 1} points selected")

def record_hotkey():
    def on_key(e):
        global hotkey
        if e.event_type == keyboard.KEY_DOWN:
            if 'keys' not in on_key.__dict__:
                on_key.keys = set()
            on_key.keys.add(str(e.name))
        elif e.event_type == keyboard.KEY_UP:
            if 'keys' in on_key.__dict__ and on_key.keys:
                hotkey_str = '+'.join(sorted(on_key.keys))
                dpg.set_item_label("hotkey_display", f"{hotkey_str}")
                hotkey = on_key.keys.copy()
                on_key.keys.clear()
            keyboard.unhook(on_key)

    dpg.set_item_label("hotkey_display", "Press keys...")
    keyboard.hook(on_key)


def calculate_resize_factor_callback():
    global resize_factor
    image_finder = ImageFinder()
    dpg.configure_item("calculate_resize_factor_button", enabled=False)
    dpg.set_value("resize_factor", f"Calculating...")
    best_resize_factor = image_finder.find_best_resize_factor(area)
    dpg.set_value("resize_factor", f"{best_resize_factor}")
    dpg.configure_item("calculate_resize_factor_button", enabled=True)
    resize_factor = best_resize_factor

def select_area_callback():
    global area
    selector = ScreenAreaSelector()
    coordinates = selector.get_coordinates()
    dpg.set_item_label("area_info", f"{coordinates}")
    area = coordinates

if __name__ == "__main__":
    create_gui()

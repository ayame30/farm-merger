import dearpygui.dearpygui as dpg
import keyboard
import pyautogui
import os
import time
from multiprocessing import Process, Queue
from merging_points_selector import MergingPointsSelector
from item_finder import ImageFinder
from screen_area_selector import ScreenAreaSelector
import multiprocessing

p = None
merge_count = 5
area = tuple()
hotkey = {"f1"}
stop_hotkey = {"f2"}
merging_points = list()
resize_factor = 1

class LogQueue:
    def __init__(self):
        self.queue = Queue()
    def get_queue(self):
        return self.queue

queue = LogQueue()

def create_gui():
    dpg.create_context()
    with dpg.window(label="Farm Merger v0.1", no_title_bar=True, no_move=True, no_collapse=True, width=400, height=550):
        dpg.add_text("Farm Merger v0.1", color=(255, 165, 0))
        dpg.add_spacer(height=5)
        dpg.add_text("** Disclaimer: Image recognition using openCV, mouse moving using pixel coordinates, so remember to update the merging slots after moving the map, always keep the gameplay on top of other windows", wrap=300)
        dpg.add_spacer(height=20)
        
        add_merge_count_selector()
        add_hotkey_selectors()
        add_screen_area_selector()
        add_merging_slots_selector()
        add_zoom_level_selector()
        add_start_stop_buttons()
        add_log_output()

    setup_viewport()

def add_merge_count_selector():
    with dpg.group(horizontal=True):
        dpg.add_text("Merge Count:")
        dpg.add_radio_button(tag="merge_count", items=[3, 5, 10], default_value=merge_count, horizontal=True, callback=update_merge_count)
    dpg.add_spacer(height=10)

def add_hotkey_selectors():
    add_hotkey_selector("Start HotKey:", "hotkey_display", record_hotkey, hotkey)
    add_hotkey_selector("Pause HotKey:", "stop_hotkey_display", record_stop_hotkey, stop_hotkey)

def add_hotkey_selector(label, tag, callback, key):
    with dpg.group(horizontal=True):
        dpg.add_text(label)
        dpg.add_button(label=f"{'+'.join(sorted(key))}", callback=callback, tag=tag, width=100)
    dpg.add_spacer(height=10)

def add_screen_area_selector():
    with dpg.group(horizontal=True):
        dpg.add_text("Screen Area: ")
        dpg.add_button(label="", callback=select_area_callback, tag="area_info", width=200)
    dpg.add_spacer(height=10)

def add_merging_slots_selector():
    with dpg.group(horizontal=True):
        dpg.add_text("Merging Slots: ")
        dpg.add_button(label="", callback=select_merging_points_callback, tag="merging_points", width=200)
    dpg.add_spacer(height=10)

def add_zoom_level_selector():
    with dpg.group(horizontal=True):
        dpg.add_text("Game Zoom level: ")
        dpg.add_input_text(default_value=resize_factor, tag="resize_factor", callback=input_resize_factor_callback, width=100)
        dpg.add_button(label="Calculate", callback=calculate_resize_factor_callback, tag="calculate_resize_factor_button")
    dpg.add_spacer(height=10)

def add_start_stop_buttons():
    green_btn_theme = create_button_theme((77, 214, 98), (97, 234, 118), (57, 194, 78), (0, 0, 0))
    red_btn_theme = create_button_theme((214, 77, 98), (234, 97, 118), (194, 57, 78), (255, 255, 255))

    dpg.add_button(label="Start Monitoring", callback=start_button_callback, tag="start_button")
    dpg.bind_item_theme("start_button", green_btn_theme)
    dpg.add_button(label="Stop", callback=stop_button_callback, tag="stop_button", show=False)
    dpg.bind_item_theme("stop_button", red_btn_theme)
    dpg.add_spacer(height=10)

def add_log_output():
    with dpg.group():
        dpg.add_text("Log:")
        dpg.add_input_text(multiline=True, readonly=True, tag="log_output", height=80, width=300)

def create_button_theme(button_color, hovered_color, active_color, text_color):
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, button_color)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, hovered_color)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, active_color)
            dpg.add_theme_color(dpg.mvThemeCol_Text, text_color)
    return theme

def setup_viewport():
    dpg.create_viewport(title="Farm Merger", width=400, height=550)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def get_image_file_paths(folder):
    image_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return sorted(image_files, reverse=True)

def start_merge(log_queue, area, resize_factor, merge_count, merging_points, stop_hotkey):
    def terminate_merge_process():
        log_message("Stopping merge process...")
    
    keyboard.add_hotkey('+'.join(sorted(stop_hotkey)), terminate_merge_process)

    def log_message(message):
        log_queue.put(message)

    img_folder = './img'
    log_message("Getting image files...")
    image_files = get_image_file_paths(img_folder)

    if not validate_merge_parameters(area, resize_factor, merge_count, merging_points):
        return

    log_message("Starting merge process...")
    while True:
        if not perform_merge_cycle(image_files, area, resize_factor, merge_count, merging_points, log_message):
            break
    
    log_message("No more merges to perform.")
    log_message("Pausing... Please resume with hotkey.")

def validate_merge_parameters(area, resize_factor, merge_count, merging_points):
    if len(area) != 4:
        log_message("Error: Screen area not properly set.")
        return False
    
    if resize_factor == 0:
        log_message("Error: Resize factor not set or invalid.")
        return False
    
    if len(merging_points) < merge_count - 1:
        log_message(f"Error: Not enough merging points set. Expected {merge_count - 1}, got {len(merging_points)}.")
        return False
    
    return True

def perform_merge_cycle(image_files, area, resize_factor, merge_count, merging_points, log_message):
    for target_image in image_files:
        template_center_points, _ = ImageFinder.find_image_on_screen(target_image, *area, resize_factor)
        if template_center_points:
            log_message(f"Found {len(template_center_points)} for {target_image}")
        
        if len(template_center_points) > merge_count - 1 and len(merging_points) >= merge_count - 1:
            perform_merge_operations(template_center_points, merging_points, merge_count, log_message)
            log_message("Dragging operations completed.")
            return True
    return False

def perform_merge_operations(template_center_points, merging_points, merge_count, log_message):
    for i in range(merge_count):
        log_message(template_center_points[i])
        start_x, start_y = template_center_points[i]
        end_x, end_y = merging_points[i % (merge_count - 1)]
        
        pyautogui.mouseUp()
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=0.1)
        pyautogui.mouseUp()
        pyautogui.sleep(0.1)

def input_resize_factor_callback(sender, app_data, user_data):
    global resize_factor
    if app_data == "":
        return
    try:
        value = float(app_data)
        if value <= 0:
            log_message("Error: Resize factor must be greater than 0.")
            return
    except ValueError:
        log_message("Error: Invalid input. Please enter a valid number.")
        return
    resize_factor = float(app_data)

def update_merge_count(sender, app_data, user_data):
    global merge_count, merging_points
    merge_count = int(app_data)
    if merge_count - 1 > len(merging_points):
        dpg.set_item_label("merging_points", "")
        merging_points = list()

def log_message(message):
    current_log = dpg.get_value("log_output")
    new_log = f"{message}\n{current_log}"
    dpg.set_value("log_output", new_log)

def update_log_message():
    global p
    current_log = dpg.get_value("log_output")
    while not queue.get_queue().empty():
        msg = queue.get_queue().get()
        if msg == "Stopping merge process...":
           terminate_merge_process()
        current_log = f"{msg}\n{current_log}"
    dpg.set_value("log_output", current_log)

def terminate_merge_process():
    global p
    if p is None or not p.is_alive():
        log_message("No merge process to terminate.")
        return
    pyautogui.mouseUp()
    p.terminate()
    update_log_message()
    log_message("Terminated.")

def start_merge_process():
    global p, stop_hotkey, area, resize_factor, merge_count, merging_points
    if p is not None and p.is_alive():
        log_message("Merge process is already running.")
        return
    log_message("Starting merge process...")
    p = Process(target=start_merge, args=(queue.get_queue(), area, resize_factor, merge_count, merging_points, stop_hotkey))
    p.start()
    while p.is_alive():
        update_log_message()
        time.sleep(0.5)
    p.join()
    update_log_message()
    log_message("Stopped. Please resume with hotkey.")

def start_button_callback():
    global hotkey
    dpg.hide_item("start_button")
    dpg.show_item("stop_button")
    # Disable all buttons
    dpg.disable_item("merge_count")
    dpg.disable_item("hotkey_display")
    dpg.disable_item("stop_hotkey_display")
    dpg.disable_item("area_info")
    # Disable input fields
    dpg.disable_item("merging_points")
    dpg.disable_item("resize_factor")
    dpg.disable_item("calculate_resize_factor_button")

    log_message("Monitoring started...")
    log_message(f"Waiting for hotkey: {hotkey}")
    keyboard.add_hotkey('+'.join(sorted(hotkey)), start_merge_process)

def stop_button_callback():
    dpg.hide_item("stop_button")
    dpg.show_item("start_button")
    # Enable all buttons
    dpg.enable_item("merge_count")
    dpg.enable_item("hotkey_display")
    dpg.enable_item("stop_hotkey_display")
    dpg.enable_item("area_info")
    # Disable input fields
    dpg.enable_item("merging_points")
    dpg.enable_item("resize_factor")
    dpg.enable_item("calculate_resize_factor_button")

    log_message("Monitoring stopped")
    terminate_merge_process()
    keyboard.remove_hotkey(start_merge_process)

def select_merging_points_callback():
    global merging_points
    dpg.set_item_label("merging_points", "Selecting merging points...")
    selector = MergingPointsSelector(merge_count - 1)
    merging_points = selector.get_points()
    dpg.set_item_label("merging_points", f"{merge_count - 1} points selected")

def record_hotkey():
    record_key("hotkey_display", "hotkey", stop_hotkey)

def record_stop_hotkey():
    record_key("stop_hotkey_display", "stop_hotkey", hotkey)

def record_key(display_tag, key_type, invalid_key):
    def on_key(e):
        if e.event_type == keyboard.KEY_DOWN:
            if 'keys' not in on_key.__dict__:
                on_key.keys = set()
            on_key.keys.add(str(e.name))
        elif e.event_type == keyboard.KEY_UP:
            if 'keys' in on_key.__dict__ and on_key.keys:
                if on_key.keys.issubset(invalid_key):
                    dpg.set_item_label(display_tag, f"")
                else:
                    key_str = '+'.join(sorted(on_key.keys))
                    dpg.set_item_label(display_tag, f"{key_str}")
                    globals()[key_type] = on_key.keys.copy()
                    on_key.keys.clear()
            keyboard.unhook(on_key)

    dpg.set_item_label(display_tag, "Press keys...")
    keyboard.hook(on_key)

def calculate_resize_factor_callback():
    global resize_factor
    image_finder = ImageFinder()
    dpg.disable_item("calculate_resize_factor_button")
    dpg.set_value("resize_factor", "Calculating...")
    best_resize_factor = image_finder.find_best_resize_factor(area)
    dpg.set_value("resize_factor", f"{best_resize_factor}")
    dpg.enable_item("calculate_resize_factor_button")
    resize_factor = best_resize_factor

def select_area_callback():
    global area
    selector = ScreenAreaSelector()
    coordinates = selector.get_coordinates()
    dpg.set_item_label("area_info", f"{coordinates}")
    area = coordinates

if __name__ == "__main__":
    multiprocessing.freeze_support()
    create_gui()

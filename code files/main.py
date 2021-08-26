from color_detector import *
from image_picker import *
from multiprocessing import Process, Manager, freeze_support


def start_color_det_process(path, name):
    color_det_process = Process(target=color_detector, args=(path, name))
    color_det_process.start()


if __name__ == "__main__":
    freeze_support()
    print("Starting")
    manager = Manager()
    print("worked")

    choose_process = Process(target=choose_folder, args=(start_color_det_process,))
    choose_process.start()

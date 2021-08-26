from tkinter import *
from tkinter import filedialog
from os import listdir

image_exts = ["tiff", "jpeg", "gif", "jpg", "png"]
window = Tk()
window.title("Choose Image Folder")
window.geometry("780x640")

name_box = Listbox(window, font=("Courier", 15), width=200)


def get_img_batch(callback):
    folder = filedialog.askdirectory()
    files = listdir(folder)
    images = find_images(files)

    for image in images:
        name_box.insert(END, image)

    name_box.bind("<Double-1>", lambda event, fldr=folder, cl=callback: return_image(event, fldr, cl))
    name_box.pack()

    return folder


def return_image(event, folder_name, callback):
    selected_name = name_box.get(name_box.curselection())
    full_path = folder_name + "/" + selected_name

    callback(full_path, selected_name)


def find_images(file_names):
    images = []

    for file in file_names:
        for ext in image_exts:
            if file.__contains__(f".{ext}") or file.__contains__(f"{ext.upper()}"):
                images.append(file)
                break

    return images


def choose_folder(callback):
    title = Label(window, text="Choose a batch", pady=100, font=("Courier", 44))
    title.pack()

    choose_btn = Button(window, text="Choose a Folder", command=lambda cl=callback: get_img_batch(cl),
                        font=("Courier", 15))
    choose_btn.pack()

    window.mainloop()

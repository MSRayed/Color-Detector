import cv2
import numpy as np
import pandas as pd

img = None

img_copy = None

color_board = None

# Right click position saved
delete_pos = None

# Rows and columns in the color board
color_cols = 8
color_rows = 4

draw_from = 0

# Where to add the new color mark
curr_color_row = 1
curr_color_col = 1

color_square_size = 40

clicked = False
r = g = b = x_pos = y_pos = 0

occurrence = 100

colors_picked = []

# Reading csv file with pandas and giving names to each column
name_index = ["color", "color_name", "hex", "R", "G", "B"]
color_names = pd.read_csv('data/colors.csv', names=name_index, header=None)

pantone_index = ["R", "G", "B", "pantone"]
pantone_colors = pd.read_csv('data/rgb_to_tcx.csv', names=pantone_index, header=None)

names_used = []
pantones_used = []


# function to calculate minimum distance from all colors and get the most matching color
def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(pantone_colors)):
        d = abs(R - int(pantone_colors.loc[i, "R"])) + abs(G - int(pantone_colors.loc[i, "G"])) + abs(
            B - int(pantone_colors.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = color_names.loc[i, "color_name"]
    return cname


def getPantoneColor(R, G, B):
    minimum = 10000
    pantone = None

    for i in range(len(color_names)):
        d = abs(R - int(color_names.loc[i, "R"])) + abs(G - int(color_names.loc[i, "G"])) + abs(
            B - int(color_names.loc[i, "B"]))

        if d <= minimum:
            minimum = d
            pantone = pantone_colors.loc[i, "pantone"]

    return pantone


def find_colors(image):
    global names_used, pantones_used
    pixels = image.reshape(-1, image.shape[-1])
    colors, count = np.unique(pixels, axis=0, return_counts=True)

    for i in range(len(colors)):
        if count[i] > occurrence:
            bc, gc, rc = colors[i]
            name = getColorName(rc, gc, bc)
            pantone = getPantoneColor(rc, gc, bc)

            if name not in names_used:
                colors_picked.append(tuple(colors[i]))
                names_used.append(name)
                pantones_used.append(pantone)


# function to get x,y coordinates of mouse double click
def draw_function(event, x, y, flags, param):
    global color_square_size, color_board, delete_pos

    if event == cv2.EVENT_LBUTTONDBLCLK:
        if x > X_position and x < X_position + img.shape[1]:
            global b, g, r, x_pos, y_pos, clicked
            clicked = True

            x_pos = x - X_position
            y_pos = y

            b, g, r = img[y_pos, x_pos]
            b = int(b)
            g = int(g)
            r = int(r)

            colors_picked.append((b, g, r))
            names_used.append(getColorName(r, g, b))
            pantones_used.append(getPantoneColor(r, g, b))

        format_colors()
        
    if event == cv2.EVENT_RBUTTONDBLCLK:
        delete_pos = (x, y)


def delete(event, x, y, flags, param):
    global delete_pos

    if event == cv2.EVENT_RBUTTONDBLCLK:
        delete_pos = (x, y)


def format_colors():
    global color_board, X_position

    color_board = np.full((900, 1260, 3), (255, 255, 255), dtype=np.uint8)
    X_position = 1260//2-img.shape[1]//2
    color_board[0:img.shape[0], X_position:X_position+img.shape[1], :] = img_copy[0:img.shape[0], 0:img.shape[1], :]


def draw_colors():
    global delete_pos
    format_colors()

    margin_x = 60
    margin_y = 50

    current_x = margin_x
    current_y = draw_from + margin_y

    for i, color in enumerate(colors_picked):
        # The coordinates
        end_x = current_x + color_square_size
        end_y = current_y + color_square_size

        # Getting a the new row
        if end_x > color_board.shape[1]:
            current_y += color_square_size + margin_y
            current_x = margin_x

            end_x = current_x + color_square_size
            end_y = current_y + color_square_size

        if delete_pos:
            if current_x < delete_pos[0] < end_x:
                if current_y < delete_pos[1] < end_y:
                    delete_pos = None
                    colors_picked.remove(color)
                    names_used.remove(names_used[i])
                    pantones_used.remove(pantones_used[i])
                    break

        # The taking the colors
        bc, gc, rc = color
        rc, gc, bc = int(rc), int(gc), int(bc)

        cv2.rectangle(color_board, (current_x, current_y), (end_x, end_y), (bc, gc, rc), -1)

        name = names_used[i]
        pantone = pantones_used[i]

        font_x = current_x - 10
        font_y = current_y - 20
        # Drawing the name
        cv2.putText(color_board, name, (font_x, font_y), 2, 0.3, (0, 0, 0), 1, cv2.LINE_AA)

        font_x = current_x - 10
        font_y = current_y - 5
        # Drawing the pantone
        cv2.putText(color_board, pantone, (font_x, font_y), 2, 0.3, (0, 0, 0), 1, cv2.LINE_AA)

        current_x += color_square_size + margin_x


def color_detector(image_load_path, image_name):
    global clicked, img, img_copy, draw_from

    img = cv2.imread(image_load_path)
    img = cv2.resize(img, (700, 500))

    img_copy = img.copy()

    draw_from = img.shape[0]

    find_colors(img)  # Find all of the colors image is containing
    format_colors()  # Format the colors to show properly

    # cv2.namedWindow('Main Image')
    cv2.namedWindow('Color Board')
    cv2.setMouseCallback('Color Board', draw_function)
    # cv2.setMouseCallback('Color Board', delete)

    while 1:
        # cv2.imshow("Main Image", img)
        cv2.imshow("Color Board", color_board)
        draw_colors()

        if clicked:
            # cv2.rectangle(image, start point, end point, color, thickness)-1 fills entire rectangle
            cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)

            # Creating text string to display( Color name and RGB values )
            text = getColorName(r, g, b) + ' R=' + str(r) + ' G=' + str(g) + ' B=' + str(b)

            # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
            cv2.putText(img, text, (50, 50), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            # For very light colours we will display text in black colour
            if r + g + b >= 600:
                cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

            clicked = False

        if cv2.waitKey(20) & 0xFF == 27:
            cv2.imwrite(f"results/{image_name} result.png", color_board)
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    color_detector("images/image.png", "image.png")

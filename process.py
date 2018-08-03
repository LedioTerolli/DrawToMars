import cv2
import numpy as np
import imutils
from win32api import GetSystemMetrics
from math import sqrt
from matplotlib import pyplot as plt


class Obj:

    def __init__(self, tup_coor, coor, area, peri, center):
        self.tup_coor = tup_coor
        self.coor = coor
        self.area = area
        self.peri = peri
        self.center = center


def shape_eval(list):
    distance_list = []

    for i in range(len(list) - 1):
        distance = int(sqrt(
            ((list.item((i, 0)) - list.item((i + 1, 0))) ** 2) + ((list.item((i, 1)) - list.item((i + 1, 1))) ** 2)))
        distance_list.append(distance)

    special_dis = int(sqrt(
        ((list.item((0, 0)) - list.item((-1, 0))) ** 2) + ((list.item((0, 1)) - list.item((-1, 1))) ** 2)))
    distance_list.append(special_dis)

    index_min = distance_list.index(min(distance_list))
    sorted_list = sorted(distance_list)

    if sorted_list[0] < 20:
        list = np.delete(list, index_min, 0)
        print("deleted")


    print(distance_list)
    print("new list", list)

    return list


def get_data(image):
    filename = image
    # filename = "%s" % filename
    img = cv2.imread(filename)
    screen_size_x = GetSystemMetrics(0)
    screen_size_y = GetSystemMetrics(1)
    bg = np.zeros((screen_size_y, screen_size_x, 3), np.uint8)

    hor_size = img.shape[1]
    ver_size = img.shape[0]

    if ver_size > hor_size:
        img = imutils.rotate_bound(img, -90)

    hor_size = img.shape[1]
    ver_size = img.shape[0]
    max_dim = max(hor_size, ver_size)
    rule = 700
    r = rule / img.shape[1]
    dim = (int(rule), int(img.shape[0] * r))
    if max_dim > rule:
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    img = img[0:screen_size_y, 0:screen_size_x]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    edge = cv2.Canny(thresh, 100, 200)
    _, cnts, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    total = 0
    list_obj = []

    for c in cnts:

        area = int(cv2.contourArea(c))

        if area < 10000:
            i = 0.03
        else:
            i = 0.01

        if area > 100:
            perimeter = cv2.arcLength(c, True)
            perimeter = round(perimeter, 2)

            epsilon = i * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)
            apr = np.vstack(approx).squeeze()
            if len(apr) < 3:
                continue

            apr = shape_eval(apr)
            data = str(area) + "-" + str(len(apr))  # + "-" + str(perimeter)

            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center = [cX, cY]

            cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
            cv2.rectangle(img, (cX + 5, cY - 20), (cX + 11 * len(data), cY - 5), (255, 255, 255), -1)
            cv2.putText(img, data, (cX + 5, cY - 7), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.circle(img, (cX, cY), 3, (0, 0, 255), -1)

            enlarge_rate_x = screen_size_x * 1.0 / max(img.shape[0], img.shape[1])
            enlarge_rate_y = screen_size_y * 1.0 / min(img.shape[0], img.shape[1])

            for i in range(len(apr)):
                apr[i, 0] = apr.item((i, 0)) * enlarge_rate_x
                apr[i, 1] = apr.item((i, 1)) * enlarge_rate_y

            xp = apr[:, 0]
            yp = apr[:, 1]

            tup_coor = list(zip(xp, yp))
            list_obj.append(Obj(tup_coor, apr, area, perimeter, center))

            total += 1

    return edge, img, list_obj


edge, new_img, list_poly = get_data("p12.jpg")
cv2.imshow("edge", edge)
cv2.imshow("final", new_img)
cv2.waitKey(0)

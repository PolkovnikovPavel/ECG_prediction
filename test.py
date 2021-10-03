import cv2
import numpy as np


def nothing(*arg):
    pass


cv2.namedWindow("thresh")  # создаем главное окно
cv2.namedWindow("settings")  # создаем окно настроек

# создаем 6 бегунков для настройки начального и конечного цвета фильтра
cv2.createTrackbar('r1', 'settings', 150, 255, nothing)
cv2.createTrackbar('g1', 'settings', 150, 255, nothing)
cv2.createTrackbar('b1', 'settings', 150, 255, nothing)
cv2.createTrackbar('r2', 'settings', 255, 255, nothing)
cv2.createTrackbar('g2', 'settings', 255, 255, nothing)
cv2.createTrackbar('b2', 'settings', 255, 255, nothing)


# Read image
img = cv2.imread('images/ECG-2.jpeg')
hh, ww = img.shape[:2]


while True:
    # считываем значения бегунков
    r1 = cv2.getTrackbarPos('r1', 'settings')
    g1 = cv2.getTrackbarPos('g1', 'settings')
    b1 = cv2.getTrackbarPos('b1', 'settings')
    r2 = cv2.getTrackbarPos('r2', 'settings')
    g2 = cv2.getTrackbarPos('g2', 'settings')
    b2 = cv2.getTrackbarPos('b2', 'settings')

    # threshold on white
    # Define lower and uppper limits
    lower = np.array([r1, g1, b1])
    upper = np.array([r2, g2, b2])

    # Create mask to only select black
    thresh = cv2.inRange(img, lower, upper)

    # apply morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # invert morp image
    mask = 255 - morph

    # apply mask to image
    result = cv2.bitwise_and(img, img, mask=mask)

    cv2.imshow('thresh', thresh)
    ch = cv2.waitKey(5)
    if ch == 27:
        break


cv2.imwrite('result.jpg', thresh)
cv2.destroyAllWindows()


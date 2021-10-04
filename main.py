import cv2 as cv
import numpy as np


# Метод Оцу, который автоматически подбирает порог цвета и удаляет фон
def Otsus_method(img_name):
    img = cv.imread(f'images/{img_name}.jpeg')  # Чтение изображения
    cv.imshow("Original", img)  # Показ изображения

    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Преобразование исходного изображения в ч/б
    blur_img = cv.GaussianBlur(gray_img, (3, 3), 0)  # Размытие изображения для удаления клеточек

    (T, img_with_filter) = cv.threshold(blur_img, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)  # Применение фильтра
    cv.imshow("Filtered", img_with_filter)  # Показ изображения
    cv.imwrite(f'images/{img_name}-Otsus.jpeg', img_with_filter)  # Сохранение изображения
    cv.waitKey(0) 

    return img_with_filter


# Функция, которая обрезает изображение сверху и снизу на 1 пиксель (была нужна, потому что исходное изображение ECG-1
# сверху и снизу имело чёрную маленькую рамку)
def crop_image(img_name): 
    img = cv.imread(f'images/{img_name}.jpeg')
    y0 = 1
    y1 = img.shape[0]-1
    crop_img = img[y0:y1]
    cv.imshow('cropped', crop_img)
    cv.imwrite(f'images/{img_name}.jpeg', crop_img)
    cv.waitKey(0)

    return crop_img

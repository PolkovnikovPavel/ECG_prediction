import cv2 as cv
import numpy as np
import math
import re
import os
"""
Файл для тестирования
"""


def delete_background(img_name, is_show=True):
    """Удаление фона(костыль)

    Данная функция находит график кардиограммы и делает его белым цветом, а фон - чёрным
    Есть минус - она не универсальна и вряд ли заработает для других изображений

    :param img_name: имя изображения
    :param is_show: is_show
    :return: ч/б изобрежение без фона
    """
    hsv_min = np.array((0, 0, 0), np.uint8)  # Минимальный порог цвета
    hsv_max = np.array((240, 255, 120), np.uint8)  # Максимальный порог цвета

    img = cv.imread(f'images/{img_name}.jpeg')  # Чтение изображения
    if is_show:
        cv.imshow('Original', img)  # Показывает изображение

    img_in_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # Перевод изображения из цветовой палитры RGB (порядок изнальчно
    # изменён, BGR) в палитру HSV
    img_with_hsv_filter = cv.inRange(img_in_hsv, hsv_min, hsv_max)  # Применяет к изобрежнию фильтр

    if is_show:
        cv.imshow('Filtered', img_with_hsv_filter)  # Показывает обработанное изображение
        cv.waitKey(0)
    cv.imwrite(f'images/{img_name}_w-b.jpeg', img_with_hsv_filter)  # Сохраняет новое изображение

    return img_with_hsv_filter

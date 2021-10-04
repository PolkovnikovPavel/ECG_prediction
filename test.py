import cv2 as cv
import numpy as np


# Данная функция находит график кардиограммы и делает его белым цветом, а фон - чёрным
# Есть минус - она не универсальна и вряд ли заработает для других изображений
def delete_background(img_name):
    hsv_min = np.array((0, 0, 0), np.uint8)  # Минимальный порог цвета
    hsv_max = np.array((240, 255, 120), np.uint8)  # Максимальный порог цвета

    img = cv.imread(f'images/{img_name}.jpeg')  # Чтение изображения
    cv.imshow('Original', img)  # Показывает изображение

    img_in_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # Перевод изображения из цветовой палитры RGB (порядок изнальчно
    # изменён, BGR) в палитру HSV
    img_with_hsv_filter = cv.inRange(img_in_hsv, hsv_min, hsv_max) # Применяет к изобрежнию фильтр

    cv.imshow('Filtered', img_with_hsv_filter)  # Показывает обработанное изображение
    cv.imwrite(f'images/{img_name}_w-b.jpeg', img_with_hsv_filter)  # Сохраняет новое изображение
    cv.waitKey(0)

    return img_with_hsv_filter


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


# Функция, котороя
def get_digitization_image(img):
    img_list = np.where(img > 0, 1, 0)
    return img_list


def find_extremes(array):
    last_points = []
    ia_upper = True   # показатель, того, куда двигается прямая (вверх или вниз)
    for x in range(array.shape[1]):
        if ia_upper:   # если прямая возврастает, то надо искать верхнию точку сверху, иначе наоборат снизу
            start_y = 0   # то с какого пиксиля надо начанать считывение
            end_y = array.shape[0]
            step = 1
        else:
            start_y = array.shape[0] - 1  # то с какого пиксиля надо начанать считывение
            end_y = 0
            step = -1
        for y in range(start_y, end_y, step):
            if array[y, x] == 1:
                if len(last_points) == 0:
                    last_points.append((x, y))
                    break
                if ia_upper:
                    if y > last_points[-1][1]:
                        ia_upper = not ia_upper
                        last_points.append((x, y))
                        break
                else:
                    if y < last_points[-1][1]:
                        ia_upper = not ia_upper
                        last_points.append((x, y))
                        break

    img = np.zeros((array.shape[0], array.shape[1], 3), np.uint8)

    last = last_points[0]
    for point in last_points:
        cv.line(img, last, point, (255, 255, 255), 3)
        last = point
    cv.imshow("Image", img)
    cv.waitKey(0)

    return last_points




# Функция, которая размечает на ч/б изображении пиковые точки и возвращает их координаты
def marking_image(w_b_image):
    # TODO сделать реализацию отметки точек
    pass


# Вызовы функций
# crop_image('ECG-1')
# delete_background('ECG-1')
# Otsus_method('ECG-1')
find_extremes(get_digitization_image(Otsus_method('ECG-1')))

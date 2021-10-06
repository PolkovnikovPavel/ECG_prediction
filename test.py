import cv2 as cv
import numpy as np
import math


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


def find_extremes_and_points(array):
    last_points = []   # результат (х, у, id)
    # id:
    # 1) точка экстремума
    # 2) просто точка
    is_upper = True   # показатель, того, куда двигается прямая (вверх или вниз)
    last_angel = 0   # угол для предыдущего столбца (который был добавлен в список)
    last_average_y = (0, [0])   # это данные о предыдущем столбце (для вычислений)
    for x in range(array.shape[1]):
        all_y = []   # тут записанны все y, которые есть в столбце
        for y in range(0, array.shape[0]):   # перебор всего столбца и анализ
            if array[y, x] == 1:
                all_y.append(y)

        average_y = sum(all_y) // len(all_y)   # вычисляет средний У
        height = last_average_y[0] - average_y   # это высота между предыдущей точкои и текущей (вертикальный катет)
        size = (height ** 2 + 1) ** 0.5   # гипотенуза треугольника
        angel = math.asin(height / size)   # угол под, которым движется кривай в текущей точке

        if len(last_points) == 0:   # нужно для самого первого столбца (делает корректные значения в самом начале)
            last_points.append((x, average_y, 2))
            last_angel = angel
            last_average_y = (average_y, all_y)
            continue

        if is_upper:   # если кривая возврастает
            if angel < 0:   # если у неё угол стал убывающим, тоесть точка экстремума
                last_points.append((x - 1, last_average_y[1][0], 1))   # добавляет точку (самую верхнюю) для результата
                is_upper = not is_upper   # указывает, что кривая начала убывать
                last_angel = angel   # запаминает, под каким углом шла кривая
        else:   # если кривая убывает
            if angel > 0:   # если у неё угол стал возврастающим, тоесть точка экстремума
                last_points.append((x - 1, last_average_y[1][-1], 1))   # добавляет точку (самую нижнюю) для результата
                is_upper = not is_upper   # указывает, что кривая начала возврастать
                last_angel = angel   # запаминает, под каким углом шла кривая

        if abs(last_angel - angel) > math.pi / 6:   # кривая уже более чем на 30 грпдусов повернулсь, то запоминает её
            last_points.append((x, average_y, 2))
            last_angel = angel

        last_average_y = (average_y, all_y)

    last_points.append((array.shape[1], average_y, 2))   # сохраняет последний столбец, чтоб не было обрыва



    img = np.zeros((array.shape[0], array.shape[1], 3), np.uint8)   # просто отображение результата (не обязательно)
    last = last_points[0][:-1]
    for point in last_points:
        cv.line(img, last, point[:-1], (255, 255, 255), 1)
        if point[2] == 1:
            cv.circle(img, point[:-1], 3, (0, 255, 0), -1)
        last = point[:-1]
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
print( find_extremes_and_points(get_digitization_image(Otsus_method('ECG-1'))) )

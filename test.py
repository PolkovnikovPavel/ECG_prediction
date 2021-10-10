import cv2 as cv
import numpy as np
import math
import re
import os


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


# Процедура, которая переводит выбранный файл в формат .jpeg и удаляет исходный
def convert_to_jpeg(img_full_name):
    img = cv.imread(f'images/{img_full_name}')
    img_name = re.split(r'\.', img_full_name)[0]
    cv.imwrite(f'images/{img_name}.jpeg', img)
    os.remove(f'images/{img_full_name}')


# Функция, которая заменяет "255" на "1"
def get_digitization_image(img):
    img_list = np.where(img > 0, 1, 0)
    return img_list


# Функция, которая ищет экстремумы на графике и может их затем продемонстрировать
def find_extremes_and_points(array, is_show=True):
    last_points = []   # результат (х, у, id)
    # id:
    # 1) точка экстремума
    # 2) просто точка
    is_upper = True   # показатель, того, куда двигается прямая (вверх или вниз)
    last_angle = 0   # угол для предыдущего столбца (который был добавлен в список)
    last_average_y = (0, [0])   # это данные о предыдущем столбце (для вычислений)
    for x in range(array.shape[1]):
        all_y = []   # тут записанны все y, которые есть в столбце
        for y in range(0, array.shape[0]):   # перебор всего столбца и анализ
            if array[y, x] == 1:
                all_y.append(y)
        if len(all_y) == 0:
            all_y = last_average_y[1]
            average_y = last_average_y[0]
        else:
            average_y = sum(all_y) // len(all_y)   # вычисляет средний У
        height = last_average_y[0] - average_y   # это высота между предыдущей точкои и текущей (вертикальный катет)
        size = (height ** 2 + 1) ** 0.5   # гипотенуза треугольника
        angle = math.asin(height / size)   # угол под, которым движется кривай в текущей точке

        if len(last_points) == 0:   # нужно для самого первого столбца (делает корректные значения в самом начале)
            last_points.append((x, average_y, 2))
            last_angle = angle
            last_average_y = (average_y, all_y)
            continue

        if is_upper:   # если кривая возврастает
            if angle < 0:   # если у неё угол стал убывающим, тоесть точка экстремума
                last_points.append((x - 1, last_average_y[1][0], 1))   # добавляет точку (самую верхнюю) для результата
                is_upper = not is_upper   # указывает, что кривая начала убывать
                last_angle = angle   # запаминает, под каким углом шла кривая
        else:   # если кривая убывает
            if angle > 0:   # если у неё угол стал возврастающим, тоесть точка экстремума
                last_points.append((x - 1, last_average_y[1][-1], 1))   # добавляет точку (самую нижнюю) для результата
                is_upper = not is_upper   # указывает, что кривая начала возврастать
                last_angle = angle   # запаминает, под каким углом шла кривая

        if abs(last_angle - angle) > math.pi / 6:   # кривая повернулсь уже более чем на 30 грпдусов, то запоминает её
            last_points.append((x, average_y, 2))
            last_angle = angle

        last_average_y = (average_y, all_y)

    last_points.append((array.shape[1], average_y, 2))   # сохраняет последний столбец, чтоб не было обрыва

    img = np.zeros((array.shape[0], array.shape[1], 3), np.uint8)   # просто отображение результата (не обязательно)
    last = last_points[0][:-1]
    for point in last_points:
        cv.line(img, last, point[:-1], (255, 255, 255), 1)
        if point[2] == 1:
            cv.circle(img, point[:-1], 3, (0, 255, 0), -1)
        elif point[2] == 2:
            cv.circle(img, point[:-1], 1, (0, 0, 255), -1)
        last = point[:-1]
    cv.imwrite(f'result.jpeg', img)
    if is_show:
        cv.imshow("Image", img)
        cv.waitKey(0)

    return last_points


def get_and_find_points_r(all_extremes, is_show=True):   # многоуровневая сортировка (выведение точек R)
    '''
    ___________________________________________
    можно заметить, что растояние у точек R до соседних изломов больше чем у большенства.
    А так же они обычно выше остальных.
    На этом основана следующая сортировка
    ___________________________________________
    :param all_extremes: список всех переломов
    :param is_show: показывать результат или нет
    :return: r_points - список точек R (x, y)
    '''

    average_length = 0  # среднее растояние между каждой точкой излома (экстркмум)
    average_y = 0   # для поиска средней высоты
    max_y = 10000   # для поиска самой высокой точки
    for i in range(1, len(all_extremes)):   # проверяет все найденные изломы
        x1, y1, id1 = all_extremes[i]   # текущий
        x2, y2, id2 = all_extremes[i - 1]   # предыдущий
        average_length += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5   # суммируем
        average_y += y2
        if y2 < max_y:
            max_y = y2
    average_length = average_length / (len(all_extremes) - 1)   # считаем среднее
    average_y = average_y / (len(all_extremes) - 1)   # считаем среднее

    # ______________________________________
    # ещё можно заметить, что вокруг нужной точки соседние изломы находятся очень близко по оси Х, в отличие от других
    # больших прямых
    # ______________________________________

    r_points = []   # будущие точки R
    average_width = 0   # среднее растояние по оси Х между соседними перегибами
    minimum_boundary = average_y - (average_y - max_y) / 3   # минимальный порог высоты, по которому надо оценивать
    # точку, если она ниже, то пропускаем
    for i in range(1, len(all_extremes) - 1):
        x1, y1, id1 = all_extremes[i - 1]
        x2, y2, id2 = all_extremes[i]
        x3, y3, id3 = all_extremes[i + 1]
        length1 = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5   # теорема пифогора
        length2 = ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** 0.5
        length = (length1 + length2) / 2   # среднее растояние между двумя соседними перегибами
        if length > average_length * 1.4 and y2 < minimum_boundary:   # 1.4 - коофицент для растояния между соседними точками
            r_points.append((x2, y2))   # добавляет в список
            average_width += abs(x1 - x2) + abs(x1 - x3)   # считает среднее растояние по оси Х
    average_width = average_width / (len(r_points) * 2 + 1)   # считаем

    minimum_boundary = average_y - (average_y - max_y) / 5   # новый минимальный порог (меньше), чтоб ещё раз
    # всё проверить, но уже рассмотреть больше точек (если вдруг какая-то затерялась)
    for i in range(1, len(all_extremes) - 1):
        x1, y1, id1 = all_extremes[i - 1]
        x2, y2, id2 = all_extremes[i]
        x3, y3, id3 = all_extremes[i + 1]
        if (x2, y2) in r_points:   # если эту точку уже сохранили, то продолжаем
            continue
        length1 = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5   # теорема пифогора
        length2 = ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** 0.5
        length = (length1 + length2) / 2   # среднее растояние между двумя соседними перегибами
        width = (abs(x1 - x2) + abs(x1 - x3)) / 2   # среднее растояние по оси Х между двумя соседями
        # оно должно быть маньше среднего * 1.2 (левый коофицент)
        if length > average_length * 1.2 and y2 < minimum_boundary and width < average_width * 1.2:   # те же самые
            # условия, но + растояние по оси Х
            r_points.append((x2, y2))   # добавляет в список

    # _______________________________
    # находми группы (если такие есть) рядом стоящих получишихся точек R, и после эти группы объеденяем в одну
    # среднию точку R
    # _______________________________

    r_points_end = []   # окончательный результат
    average_dist = 0   # среднее растояние между всеми найдеными точками
    for i in range(1, len(r_points)):
        x1, y1 = r_points[i - 1]
        x2, y2 = r_points[i]
        average_dist += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5   # добавляем
    average_dist = average_dist / (len(r_points) - 1)   # считаем

    for point1 in r_points:   # перебираем все найденные точки R
        x1, y1 = point1
        all_x = [x1]   # иксы каждой точки из группы
        all_y = [y1]   # игрикикаждой точки из группы
        for point2 in r_points:   # перебираем каждую с каждой и находим их взаимное растояние друг к другу
            if point1 == point2:
                continue
            x2, y2 = point2
            dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5   # теорема пифогора
            if dist < average_dist / 4:   # если растояние меньше 1/4 от среднего, то будем считать это группой
                all_x.append(x2)   # добавляем
                all_y.append(y2)
        point_end = (sum(all_x) // len(all_x), sum(all_y) // len(all_y))   # добавляем результат группы (доже если 1-а)
        r_points_end.append(point_end)
    r_points = r_points_end   # присваевыем результат к конечному списку

    if is_show:   # просто отображение результата (не обязательно)
        img = cv.imread(f'result.jpeg')
        cv.line(img, (0, int(minimum_boundary)), (np.size(img, 1), int(minimum_boundary)), (255, 0, 255), 1)
        for point in r_points:
            point = point[:2]
            cv.circle(img, point, 5, (255, 0, 255), -1)
        cv.imwrite(f'result.jpg', img)
        cv.imshow("Image", img)
        cv.waitKey(0)

    return r_points   # return


def get_and_find_points_q_and_s(all_extremes, points_r):
    points_q = []
    points_s = []
    for i in range(1, len(all_extremes) - 1):
        if all_extremes[i + 1][:2] in points_r:
            points_q.append(all_extremes[i][:2])
        if all_extremes[i - 1][:2] in points_r:
            points_s.append(all_extremes[i][:2])
    return points_q, points_s


def get_dictionary_of_key_points(all_points, is_show=True):
    key_points = {}
    colors = {'R': (255, 0, 255),
              'Q': (0, 200, 255),
              'S': (0, 255, 193)}
    all_extremes = list(filter(lambda x: x[2] == 1, all_points))
    all_points_r = get_and_find_points_r(all_extremes, False)
    points_q, points_s = get_and_find_points_q_and_s(all_extremes, all_points_r)

    key_points['R'] = all_points_r
    key_points['Q'] = points_q
    key_points['S'] = points_s

    if is_show:
        img = cv.imread(f'result.jpeg')
        for type in key_points:
            for point in key_points[type]:
                point = point[:2]
                cv.circle(img, point, 4, colors[type], -1)
        cv.imwrite(f'result.jpg', img)
        cv.imshow("Image", img)
        cv.waitKey(0)


# Вызовы функций
# crop_image('ECG-1')
# delete_background('ECG-1')
# Otsus_method('ECG-1')
img_name = 'ECG-7'
#convert_to_jpeg(img_name)
all_points = find_extremes_and_points(get_digitization_image(Otsus_method(img_name)), is_show=False)

get_dictionary_of_key_points(all_points)

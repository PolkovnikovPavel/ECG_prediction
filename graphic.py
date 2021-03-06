import cv2 as cv
import numpy as np
import math
import re
import os
import copy

"""
Файл для получения всех данных (точек, интервалов)
"""


class GraphicException(Exception):
    def __init__(self, text):
        self.txt = text


class Graphic:
    def __init__(self, image_full_name, speed):
        """Конструктор класса

        :param image_full_name: имя.расширение
        :param speed: Скорость записи ЭКГ. Обычно 25 или 50 мм/с
        """
        # Параметры изображения
        self.dict_of_points = {}
        self.__reserve_dict_of_points = {}
        self.dict_of_intervals = {}
        self.speed_of_ecg = speed

        self.image_full_name = image_full_name

        self.__is_equal = False
        self.__length_of_square = 0
        self.__all_extremes = None
        self.__all_points = None
        self.__img_otsus_method = None
        self.__are_squares_big = False
        self.__length_of_rs_in_mm = 0
        self.heart_rate = 0
        self.prediction = ''

    def get_img(self, flag=cv.IMREAD_UNCHANGED, any_path=None):
        if any_path is None:
            return cv.imdecode(np.fromfile(self.image_full_name, dtype=np.uint8), flag)  # Чтение изображения
        else:
            return cv.imdecode(np.fromfile(any_path, dtype=np.uint8), flag)  # Чтение изображения

    def graph_detection(self):
        """Main-функция.

        Запускаешь её и автоматически определяются все необходимые величины.
        """
        self.__find_extremes_and_points(self.__get_digitization_image(self.__otsus_method(False)))
        self.__get_dictionary_of_key_points()
        self.__set_points_for_intervals()
        self.__find_square_length()
        self.__get_intervals()
        self.__convert_intervals_lengths_from_pixels_to_seconds()
        self.__is_r_distance_equal()
        self.find_heart_rate()

    def __get_intervals(self):
        """Ищет все интервалы"""
        dict_of_points = copy.deepcopy(self.dict_of_points)

        list_of_intervals = []
        dict_of_points['LP'].sort()
        dict_of_points['RT'].sort()
        if len(dict_of_points['LP']) == 0 or len(dict_of_points['RT']) == 0:  # Здесь и далее - проверки на то, что
            # такие интервалы вообще существуют (хватает ли точек для определения интервалов)
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['RT'])):
                if len(dict_of_points['LP']) > 0 and len(dict_of_points['RT']) > 0:
                    if dict_of_points['LP'][0][0] < dict_of_points['RT'][0][0]:
                        del dict_of_points['LP'][0]
                    try:
                        list_of_intervals.append(abs(dict_of_points['RT'][0][0] - dict_of_points['LP'][0][0]))
                    except BaseException:
                        print('Нарушен порядок точек ЛП и РТ.')
                        list_of_intervals = [0]
                        break
                    else:
                        del dict_of_points['LP'][0]
                        del dict_of_points['RT'][0]
        self.dict_of_intervals['TP'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['R'].sort()
        if len(dict_of_points['R']) < 2:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['R']) - 1):
                if len(dict_of_points['R']) > 1:
                    list_of_intervals.append(abs(dict_of_points['R'][0][0] - dict_of_points['R'][1][0]))
                    del dict_of_points['R'][0]
        self.dict_of_intervals['RR'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['LP'].sort()
        if len(dict_of_points['LP']) < 2:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['LP']) - 1):
                if len(dict_of_points['LP']) > 1:
                    list_of_intervals.append(abs(dict_of_points['LP'][0][0] - dict_of_points['LP'][1][0]))
                    del dict_of_points['LP'][0]
        self.dict_of_intervals['PP'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['LP'].sort()
        dict_of_points['Q'].sort()
        if len(dict_of_points['LP']) == 0 or len(dict_of_points['Q']) == 0:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['LP'])):
                if len(dict_of_points['Q']) > 0 and len(dict_of_points['LP']) > 0:
                    if len(dict_of_points['Q']) > 1:
                        if abs(dict_of_points['LP'][0][0] - dict_of_points['Q'][1][0]) < \
                                abs(dict_of_points['LP'][0][0] - dict_of_points['Q'][0][0]):
                            del dict_of_points['Q'][0]
                    list_of_intervals.append(abs(dict_of_points['LP'][0][0] - dict_of_points['Q'][0][0]))
                    del dict_of_points['LP'][0]
                    del dict_of_points['Q'][0]
        self.dict_of_intervals['PQ'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['RT'].sort()
        dict_of_points['Q'].sort()
        if len(dict_of_points['Q']) == 0 or len(dict_of_points['RT']) == 0:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['Q'])):
                if len(dict_of_points['RT']) > 0 and len(dict_of_points['Q']) > 0:
                    if len(dict_of_points['RT']) > 1:
                        if abs(dict_of_points['Q'][0][0] - dict_of_points['RT'][1][0]) < \
                                abs(dict_of_points['Q'][0][0] - dict_of_points['RT'][0][0]):
                            del dict_of_points['RT'][0]
                    list_of_intervals.append(abs(dict_of_points['Q'][0][0] - dict_of_points['RT'][0][0]))
                    del dict_of_points['Q'][0]
                    del dict_of_points['RT'][0]
        self.dict_of_intervals['QT'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['RS'].sort()
        dict_of_points['Q'].sort()
        if len(dict_of_points['Q']) == 0 or len(dict_of_points['RS']) == 0:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['Q'])):
                if len(dict_of_points['RS']) > 0 and len(dict_of_points['Q']) > 0:
                    if len(dict_of_points['RS']) > 1:
                        if abs(dict_of_points['Q'][0][0] - dict_of_points['RS'][1][0]) < \
                                abs(dict_of_points['Q'][0][0] - dict_of_points['RS'][0][0]):
                            del dict_of_points['RS'][0]
                    list_of_intervals.append(abs(dict_of_points['Q'][0][0] - dict_of_points['RS'][0][0]))
                    del dict_of_points['Q'][0]
                    del dict_of_points['RS'][0]
        self.dict_of_intervals['QRS'] = list_of_intervals

        dict_of_points = copy.deepcopy(self.dict_of_points)
        list_of_intervals = []
        dict_of_points['R'].sort()
        dict_of_points['Q'].sort()
        if len(dict_of_points['Q']) == 0 or len(dict_of_points['R']) == 0:
            list_of_intervals = [0]
        else:
            for i in range(len(dict_of_points['Q'])):
                if len(dict_of_points['R']) > 0 and len(dict_of_points['Q']) > 0:
                    if len(dict_of_points['R']) > 1:
                        if abs(dict_of_points['Q'][0][0] - dict_of_points['R'][1][0]) < \
                                abs(dict_of_points['Q'][0][0] - dict_of_points['R'][0][0]):
                            del dict_of_points['R'][0]
                    list_of_intervals.append(abs(dict_of_points['Q'][0][0] - dict_of_points['R'][0][0]))
                    del dict_of_points['Q'][0]
                    del dict_of_points['R'][0]
        self.dict_of_intervals['QR'] = list_of_intervals

    def show_result(self, path_to_save='result.jpg'):
        """Только отображает

        :return: None"""
        wight = self.__img_otsus_method.shape[0]
        height = self.__img_otsus_method.shape[1]
        img = np.zeros((wight, height, 3), np.uint8)
        colors = {'R': (255, 0, 255),  # цвета
                  'Q': (0, 200, 255),
                  'S': (0, 255, 193),
                  'T': (255, 214, 145),
                  'P': (92, 0, 255)}
        last_point = self.__all_points[0]
        for point in self.__all_points[1::]:
            cv.line(img, last_point[:2], point[:2], (255, 255, 255), 1)
            if point[2] == 1:
                cv.circle(img, point[:2], 3, (0, 255, 0), -1)
            elif point[2] == 2:
                cv.circle(img, point[:2], 1, (50, 50, 200), -1)
            last_point = point
        for type in self.dict_of_points:
            if type in colors:
                color = colors[type]
            else:
                color = (255, 255, 255)
            for point in self.dict_of_points[type]:
                cv.circle(img, point[:2], 4, color, -1)
        cv.imwrite(path_to_save, img)
        cv.imshow("Image", img)
        cv.waitKey(0)

    def save_result(self, path='result.jpg', is_key_points=True):
        """
        Только сохраняет

        :return: None
        """
        wight = self.__img_otsus_method.shape[0]
        height = self.__img_otsus_method.shape[1]
        img = np.zeros((wight, height, 3), np.uint8)
        colors = {'R': (255, 0, 255),  # цвета
                  'Q': (0, 200, 255),
                  'S': (0, 255, 193),
                  'T': (255, 214, 145),
                  'P': (92, 0, 255)}
        last_point = self.__all_points[0]
        for point in self.__all_points[1::]:
            cv.line(img, last_point[:2], point[:2], (255, 255, 255), 1)
            if point[2] == 1:
                cv.circle(img, point[:2], 3, (0, 255, 0), -1)
            elif point[2] == 2:
                cv.circle(img, point[:2], 1, (50, 50, 200), -1)
            last_point = point
        if is_key_points:
            for type in self.dict_of_points:
                if type in colors:
                    color = colors[type]
                else:
                    color = (255, 255, 255)
                for point in self.dict_of_points[type]:
                    cv.circle(img, point[:2], 4, color, -1)
        cv.imwrite(path, img)

    def __otsus_method(self, is_show=False, path_to_file=None):
        """Удаление фона

        Метод Оцу, который автоматически подбирает порог цвета и удаляет фон

        :param is_show: is_show
        :return: ч/б изображение без заднего фона (только график ЭКГ)
        """
        if path_to_file is None:
            img = self.get_img()  # Чтение изображения
        else:
            img = cv.imread(path_to_file)
        if is_show:
            cv.imshow("Original", img)  # Показ изображения

        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Преобразование исходного изображения в ч/б
        blur_img = cv.GaussianBlur(gray_img, (3, 3), 0)  # Размытие изображения для удаления клеточек

        img_with_filter = cv.threshold(blur_img, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]  # Применение фильтра
        if is_show:
            cv.imshow("Filtered", img_with_filter)  # Показ изображения
            cv.waitKey(0)

        self.__img_otsus_method = img_with_filter
        return img_with_filter

    def __find_square_length(self, is_show=False):
        """Ищет на картинки клеточки и определяет, сколько 1 клеточка занимает пикселей.

        Суть работы
        ___________________________________________
        Работа данной функции основана на том, что что сначала находится график ЭКГ, затем он
        вычитается из исходного изображения и остаются только клеточки. Клеточки опять проходят
        через обнаружение, и из этого определяется, сколько в 1 клеточке пикселей. Это нужно при переводе
        пиксели -> сантиметры -> милисекунды -> секунды

        :param is_show: is_show
        """
        # Исходное изображение
        img = self.get_img(cv.IMREAD_GRAYSCALE)
        if is_show:
            cv.imshow("Original", img)
            cv.waitKey(0)

        # График ЭКГ
        graphic = self.__img_otsus_method
        if is_show:
            cv.imshow("Graphic", graphic)
            cv.waitKey(0)

        # Наше исходное изображение, но уже без графика ЭКГ
        img_with_out_graphic = np.where(graphic == 255, 255, img)

        # Размываем картинку, чтобы убрать шум
        blur_img = cv.GaussianBlur(img_with_out_graphic, (5, 5), 0)

        # Показываем и сохраняем
        if is_show:
            cv.imshow('result', blur_img)
            cv.waitKey(0)

        destination = '/'.join(self.image_full_name.split('/')[:-1])
        gel = 'temp_w-o_graphic.jpeg'
        script_path = os.getcwd()
        os.chdir(destination)
        cv.imwrite(gel, blur_img)

        # Пропускаем ещё раз через фильтр Оцу, чтобы выделить клеточки
        img_with_out_graphic_otsus = self.__otsus_method(False, path_to_file='temp_w-o_graphic.jpeg')
        os.remove('temp_w-o_graphic.jpeg')
        os.chdir(script_path)

        # Выделяем контуры клеточек
        (contours, hierarchy) = cv.findContours(img_with_out_graphic_otsus.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

        # Переводим ч/б изображение в BGR
        cv.cvtColor(img_with_out_graphic, cv.COLOR_GRAY2BGR)

        # Рисуем контуры
        if is_show:
            blank_img = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
            cv.drawContours(blank_img, contours, -1, (255, 0, 0), 1, cv.LINE_AA)
            cv.imshow('contours', blank_img)
            cv.waitKey(0)

        # Считаем координаты клеток
        list_of_squares_coord = []  # Список координат клеточек
        for i in range(0, len(contours)):
            x, y, w, h = cv.boundingRect(contours[i])
            if w > 5 and h > 5:  # Отсеиваем маленькие контуры, убираем шум
                list_of_squares_coord.append([x, y, x + w, y + h])

        # Считаем, сколько пикселей занимает одна клеточка на оси Х
        list_of_squares_dis = []  # Список растояний между точками
        flag = True
        i = 0
        # В этом цикле считаем, сколько клеточек по x занимает одна клетка, если это
        # мусор, то удаляем
        while flag is True:
            if i < len(list_of_squares_coord):
                length = list_of_squares_coord[i][2] - list_of_squares_coord[i][0]
                if length >= img.shape[1] / 16:  # Если "клеточка" имеет слишком большие размеры, то
                    # считаем, что это мусор, и удаляем этот контур
                    list_of_squares_coord.pop(i)
                    continue
                else:
                    i += 1
                    list_of_squares_dis.append(length)

            else:
                flag = False

        average_length = 0  # Средняя длина клеточки
        # Считаем среднюю длину клетки
        for i in list_of_squares_dis:
            average_length += i
        average_length = average_length // len(list_of_squares_dis)

        self.__length_of_square = average_length

        # Проверка на то, большие клеточки распознал алгоритм, или маленькие
        if blur_img.shape[0] / average_length > 15:
            self.__are_squares_big = False
        else:
            self.__are_squares_big = True

    def crop_image(self, n, is_show=False):
        """Обрезает изображение сверху и снизу на n пикселей

        :param n: число пикселей, на которое изображение обрежется
        :param is_show: is_show
        :return: обрезанное изображение
        """
        img = cv.imread(self.image_full_name)
        y0 = n
        y1 = img.shape[0] - n
        crop_img = img[y0:y1]
        if is_show:
            cv.imshow('cropped', crop_img)
            cv.waitKey(0)

        return crop_img

    @staticmethod
    def __get_digitization_image(img):
        """Обрабатывает изображение, заменяя все светлые цвета на белый.

        :param img: изображение
        :return: изображение, где все цвета кроме чёрного - белые
        """
        img_list = np.where(img > 0, 1, 0)
        return img_list

    def __find_extremes_and_points(self, array):
        """Ищет экстремумы на графике.

        :param array: изображение, прошедшие удаление заднего фона и переведённое в нолики и единички
        :return: None"""
        last_points = []  # результат (х, у, id)
        # id:
        # 1) точка экстремума
        # 2) просто точка
        is_upper = True  # показатель, того, куда двигается прямая (вверх или вниз)
        last_angle = 0  # угол для предыдущего столбца (который был добавлен в список)
        last_average_y = (0, [0])  # это данные о предыдущем столбце (для вычислений)
        average_y = last_average_y[0]
        for x in range(array.shape[1]):
            all_y = []  # тут записанны все y, которые есть в столбце
            for y in range(0, array.shape[0]):  # перебор всего столбца и анализ
                if array[y, x] == 1:
                    all_y.append(y)
            if len(all_y) == 0:
                all_y = last_average_y[1]
                average_y = last_average_y[0]
            else:
                average_y = sum(all_y) // len(all_y)  # вычисляет средний У
            height = last_average_y[0] - average_y  # это высота между предыдущей точкои и текущей (вертикальный катет)
            size = (height ** 2 + 1) ** 0.5  # гипотенуза треугольника
            angle = math.asin(height / size)  # угол под, которым движется кривай в текущей точке

            if len(last_points) == 0:  # нужно для самого первого столбца (делает корректные значения в самом начале)
                last_points.append((x, average_y, 2))
                last_angle = angle
                last_average_y = (average_y, all_y)
                continue

            if is_upper:  # если кривая возврастает
                if angle < 0:  # если у неё угол стал убывающим, тоесть точка экстремума
                    last_points.append((x - 1, last_average_y[1][0], 1))  # добавляет точку (самую верхнюю) для
                    # результата
                    is_upper = not is_upper  # указывает, что кривая начала убывать
                    last_angle = angle  # запаминает, под каким углом шла кривая
            else:  # если кривая убывает
                if angle > 0:  # если у неё угол стал возврастающим, тоесть точка экстремума
                    last_points.append((x - 1, last_average_y[1][-1], 1))  # добавляет точку (самую нижнюю) для
                    # результата
                    is_upper = not is_upper  # указывает, что кривая начала возврастать
                    last_angle = angle  # запаминает, под каким углом шла кривая

            if abs(last_angle - angle) > math.pi / 6:  # кривая повернулсь уже более чем на 30 грпдусов, то
                # запоминает её
                last_points.append((x, average_y, 2))
                last_angle = angle

            last_average_y = (average_y, all_y)

        last_points.append((array.shape[1], average_y, 2))  # сохраняет последний столбец, чтоб не было обрыва

        last_points.sort(key=lambda x: x[0])
        self.__all_points = last_points
        self.__all_extremes = list(filter(lambda x: x[2] == 1, self.__all_points))

    def __get_and_find_points_r(self, is_show=False):  # многоуровневая сортировка (выведение точек R)
        """Находит все точки R.

        Суть работы
        ___________________________________________
        Можно заметить, что растояние у точек R до соседних изломов больше чем у большенства.
        А так же они обычно выше остальных.
        На этом основана следующая сортировка

        :param is_show: показывать результат или нет
        :return: r_points - список точек R (x, y)
        """
        # Проверка на наличие экстремумов в параметрах класса и поиск, в противном случае
        if self.__all_extremes is None:
            self.graph_detection()

        average_length = 0  # среднее растояние между каждой точкой излома (экстркмум)
        average_y = 0  # для поиска средней высоты
        max_y = 10000  # для поиска самой высокой точки
        for i in range(1, len(self.__all_extremes)):  # проверяет все найденные изломы
            x1, y1, id1 = self.__all_extremes[i]  # текущий
            x2, y2, id2 = self.__all_extremes[i - 1]  # предыдущий
            average_length += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # суммируем
            average_y += y2
            if y2 < max_y:
                max_y = y2
        average_length = average_length / (len(self.__all_extremes) - 1)  # считаем среднее
        average_y = average_y / (len(self.__all_extremes) - 1)  # считаем среднее

        # ______________________________________
        # ещё можно заметить, что вокруг нужной точки соседние изломы находятся очень близко по оси Х, в отличие от
        # других больших прямых
        # ______________________________________

        r_points = []  # будущие точки R
        average_width = 0  # среднее растояние по оси Х между соседними перегибами
        minimum_boundary = average_y - (average_y - max_y) / 3  # минимальный порог высоты, по которому надо оценивать
        # точку, если она ниже, то пропускаем
        for i in range(1, len(self.__all_extremes) - 1):
            x1, y1, id1 = self.__all_extremes[i - 1]
            x2, y2, id2 = self.__all_extremes[i]
            x3, y3, id3 = self.__all_extremes[i + 1]
            length1 = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # теорема пифогора
            length2 = ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** 0.5
            length = (length1 + length2) / 2  # среднее растояние между двумя соседними перегибами
            if length > average_length * 1.4 and y2 < minimum_boundary:  # 1.4 - коофицент для растояния между соседними
                # точками
                r_points.append((x2, y2))  # добавляет в список
                average_width += abs(x1 - x2) + abs(x1 - x3)  # считает среднее растояние по оси Х
        average_width = average_width / (len(r_points) * 2 + 1)  # считаем

        minimum_boundary = average_y - (average_y - max_y) / 5  # новый минимальный порог (меньше), чтоб ещё раз
        # всё проверить, но уже рассмотреть больше точек (если вдруг какая-то затерялась)
        for i in range(1, len(self.__all_extremes) - 1):
            x1, y1, id1 = self.__all_extremes[i - 1]
            x2, y2, id2 = self.__all_extremes[i]
            x3, y3, id3 = self.__all_extremes[i + 1]
            if (x2, y2) in r_points:  # если эту точку уже сохранили, то продолжаем
                continue
            length1 = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # теорема пифогора
            length2 = ((x2 - x3) ** 2 + (y2 - y3) ** 2) ** 0.5
            length = (length1 + length2) / 2  # среднее растояние между двумя соседними перегибами
            width = (abs(x1 - x2) + abs(x1 - x3)) / 2  # среднее растояние по оси Х между двумя соседями
            # оно должно быть маньше среднего * 1.2 (левый коофицент)
            if length > average_length * 1.2 and y2 < minimum_boundary and width < average_width * 1.2:  # те же самые
                # условия, но + растояние по оси Х
                r_points.append((x2, y2))  # добавляет в список

        # _______________________________
        # находми группы (если такие есть) рядом стоящих получишихся точек R, и после эти группы объеденяем в одну
        # среднию точку R
        # _______________________________

        r_points_end = []  # окончательный результат
        average_dist = 0  # среднее растояние между всеми найдеными точками
        for i in range(1, len(r_points)):
            x1, y1 = r_points[i - 1]
            x2, y2 = r_points[i]
            average_dist += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5  # добавляем
        average_dist = average_dist / (len(r_points) - 1)  # считаем

        for point1 in r_points:  # перебираем все найденные точки R
            x1, y1 = point1
            all_x = [x1]  # иксы каждой точки из группы
            all_y = [y1]  # игрикикаждой точки из группы
            for point2 in r_points:  # перебираем каждую с каждой и находим их взаимное растояние друг к другу
                if point1 == point2:
                    continue
                x2, y2 = point2
                dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5  # теорема пифогора
                if dist < average_dist / 4:  # если растояние меньше 1/4 от среднего, то будем считать это группой
                    all_x.append(x2)  # добавляем
                    all_y.append(y2)
            point_end = (sum(all_x) // len(all_x), sum(all_y) // len(all_y))  # добавляем результат группы (даже если
            # 1-а)
            if point_end not in r_points_end:
                r_points_end.append(point_end)
        r_points = r_points_end  # присваевыем результат к конечному списку

        if is_show:  # просто отображение результата (не обязательно)
            img = cv.imread('result.jpeg')
            cv.line(img, (0, int(minimum_boundary)), (np.size(img, 1), int(minimum_boundary)), (255, 0, 255), 1)
            for point in r_points:
                point = point[:2]
                cv.circle(img, point, 5, (255, 0, 255), -1)
            cv.imwrite('result.jpg', img)
            cv.imshow("Image", img)
            cv.waitKey(0)

        return r_points

    def __get_and_find_points_q_and_s(self, points_r):  # отдаёт 2 списка с точками Q и S
        """Ищет точки q и s.

        Суть работы
        ____________________________________________________
        Выбирает 2 ключивые точки (Q и S) - это точки очень близкие к R (по оси Х), а так же самые низкие. Поэтому
        решено выбирать все точки в право и влево от R на растояние 1/5 RR и найти самые низкие справа и слева.

        :param points_r: points_r
        :return: 2 списка с точками Q и S
        """

        points_q = []
        points_s = []

        list_of_x_r = list(map(lambda x: x[0], points_r))  # определяет среднию дистанцию между R
        average_dist_x = 0
        for i in range(len(points_r) - 1):
            average_dist_x += list_of_x_r[i + 1] - list_of_x_r[i]
        average_dist_x = average_dist_x / (len(points_r) - 1)

        for point_r in points_r:
            list_of_points_s = []
            list_of_points_q = []
            for i in range(1, len(self.__all_extremes)):
                point = self.__all_extremes[i][:2]
                if point[0] < point_r[0] - (average_dist_x / 5) or point == point_r:
                    continue
                elif point[0] > point_r[0] + (average_dist_x / 5):
                    break
                if point[0] > point_r[0]:
                    list_of_points_s.append(point)
                else:
                    list_of_points_q.append(point)
                try:  # TODO: обработка таких случаев
                    points_s.append(max(list_of_points_s, key=lambda x: x[1]))  # берёт самую низкую точку из указанного
                    # диапазона
                    points_q.append(max(list_of_points_q, key=lambda x: x[1]))
                except ValueError:
                    pass

        return points_q, points_s

    def __get_and_find_points_t(self, points_r):
        """Находит все точки T

        Суть работы
        ________________________
        Работает так же как и определение точек Р, но в правую сторону: берёт все точки в диапозоне первой половины
        между R1 - R2, и выбирает самую высокую точку

        :param points_r: points_r
        :return: список со всеми точками T
        """

        points_t = []
        average_width_r = 0
        average_dist = 0
        for i in range(len(points_r)):  # проверяет каждую точку R
            if i < len(points_r) - 1:
                width = points_r[i + 1][0] - points_r[i][0]  # растояние по оси Х между RR
                average_width_r += width  # среднее растояние
                points = list(filter(lambda x: points_r[i][0] < x[0] < points_r[i][0] + width / 2,
                                     self.__all_extremes))
                # это самое главное - выбирает все точки, принадлежащие диапозону

                points.sort(key=lambda x: x[1])
                try:  # TODO: обработка таких случаев
                    average_dist += points[0][0] - points_r[i][0]  # то на сколько точка Т удалена от R
                    points_t.append(points[0][:2])
                except IndexError:
                    pass
            else:  # работет при обработке диапозона после последней точки R.
                # Тут-то и нужны average_dist и average_width_r
                average_width_r = average_width_r / (len(points_r) - 1)
                average_dist = average_dist / (len(points_r) - 1)
                points = list(filter(lambda x: points_r[i][0] < x[0] < points_r[i][0] + average_width_r / 2,
                                     self.__all_extremes))
                points.sort(key=lambda x: x[1])
                dist = points[0][0] - points_r[i][0]
                if average_dist * 0.75 < dist < average_dist * 1.25:
                    points_t.append(points[0][:2])  # нужно, чтоб последняя точка не выбивалось от большенства
        return points_t

    def __get_and_find_points_p(self, points_r):
        """Ищет точки P.

        Суть работы
        ________________
        Работает так же как и определение точек Т, но в левую сторону. Берёт все точки в диапозоне первой половины
        между R0 - R1, и выбирает самую высокую точку

        :param points_r: points_r
        :return: список со всеми точками Р
        """

        points_p = []
        average_width_r = 0
        average_dist = 0
        for i in range(len(points_r) - 1, -1, -1):  # проверяет каждую точку R в обратном порядке
            if i > 0:
                width = points_r[i][0] - points_r[i - 1][0]  # растояние по оси Х между RR
                average_width_r += width  # среднее растояние
                points = list(filter(lambda x: points_r[i][0] > x[0] > points_r[i][0] - width / 2,
                                     self.__all_extremes))
                # это самое главное - выбирает все точки, принадлежащие диапозону

                points.sort(key=lambda x: x[1])
                try:  # TODO: обработка таких случаев
                    average_dist += points_r[i][0] - points[0][0]  # то на сколько точка Р удалена от R
                    points_p.append(points[0][:2])
                except IndexError:
                    pass
            else:  # работет при обработке диапозона перед первой точкой R. Тут-то и нужны average_dist и
                # average_width_r
                average_width_r = average_width_r / (len(points_r) - 1)
                average_dist = average_dist / (len(points_r) - 1)
                points = list(filter(lambda x: points_r[i][0] > x[0] > points_r[i][0] - average_width_r / 2,
                                     self.__all_extremes))
                points.sort(key=lambda x: x[1])
                dist = points_r[i][0] - points[0][0]
                if average_dist * 0.75 < dist < average_dist * 1.25:
                    points_p.append(points[0][:2])  # нужно, чтоб самая первая точка не выбивалось от большенства
        return points_p

    def __get_dictionary_of_key_points(self, is_show=False):
        """
        Функция, которая объеденяет все операции по вычислению ключевых точек.

        :param is_show: is_show
        :return: словарь со всеми ключевыми точками, и даже R
        """

        key_points = {}
        colors = {'R': (255, 0, 255),  # цвета
                  'Q': (0, 200, 255),
                  'S': (0, 255, 193),
                  'T': (255, 214, 145),
                  'P': (92, 0, 255)}

        # Проверка на наличие всех точек в параметрах класса и их поиск, в противном случае
        if self.__all_points is None:
            self.graph_detection()

        all_extremes = list(filter(lambda x: x[2] == 1, self.__all_points))  # выделяет из все точек только экстремумы
        all_points_r = self.__get_and_find_points_r(False)  # точки R
        all_points_r.sort(key=lambda x: x[0])  # сортировка по возврастанию Х
        all_extremes.sort(key=lambda x: x[0])

        points_q, points_s = self.__get_and_find_points_q_and_s(all_points_r)  # точки Q и S
        points_t = self.__get_and_find_points_t(all_points_r)  # точки T
        points_p = self.__get_and_find_points_p(all_points_r)  # точки P
        points_p.sort(key=lambda x: x[0])

        key_points['R'] = all_points_r
        key_points['Q'] = points_q
        key_points['S'] = points_s
        key_points['T'] = points_t
        key_points['P'] = points_p

        if is_show:  # вывод результата
            img = cv.imread(f'result.jpeg')
            for type in key_points:
                for point in key_points[type]:
                    point = point[:2]
                    cv.circle(img, point, 4, colors[type], -1)
            cv.imwrite(f'result.jpg', img)
            cv.imshow("Image", img)
            cv.waitKey(0)

        self.dict_of_points = key_points

        return key_points

    def __defining_intervals_t_p(self):
        """
        Находит точки для интервала между T и P

        :return: True если всё хорошо
        """
        img = cv.imread(f'result.jpg')
        all_points_rt = []  # правее R
        all_points_lp = []  # левее P
        for point_t in self.dict_of_points['T']:
            point_p = self.dict_of_points['P'][-1]  # определение ближайших точек P и Q
            for point in self.dict_of_points['P']:
                if point[0] < point_t[0]:
                    continue
                if point[0] < point_p[0]:
                    point_p = point
            point_q = self.dict_of_points['Q'][-1]
            for point in self.dict_of_points['Q']:
                if point[0] < point_t[0]:
                    continue
                if point[0] < point_q[0]:
                    point_q = point

            # выбирает все точки из промежутка между T и P
            all_extremes = list(filter(lambda x: point_t[0] < x[0] <= point_p[0], self.__all_points))
            length_tq = ((point_t[0] - point_q[0]) ** 2 + (point_t[1] - point_q[1]) ** 2) ** 0.5  # теорема Пифагора
            if len(all_extremes) < 1:
                continue
            all_points_b = []
            for i in range(len(all_extremes) - 1):
                if all_extremes[i][0] > (abs(point_t[0] - point_p[0]) // 2) + point_t[0]:
                    break
                point_b = all_extremes[i]
                length_tb = ((point_t[0] - point_b[0]) ** 2 + (point_t[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора
                length_qb = ((point_q[0] - point_b[0]) ** 2 + (point_q[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора

                # теорема косинусов для определения угла отклонения
                angle = math.acos((length_qb ** 2 + length_tq ** 2 - length_tb ** 2) / (2 * length_qb * length_tq))
                # небольшой коофицент погрешности для более точного определения
                angle -= ((abs(point_b[0] - point_t[0]) / (abs(point_t[0] - point_p[0]) // 10)) * 0.03)

                all_points_b.append((point_b[0], point_b[1], angle))
            point_after_t = max(all_points_b, key=lambda x: x[2])[:2]
            all_points_rt.append(point_after_t)

            all_points_b = []  # всё тоже самое, но для другой точки
            length_tr_p = ((point_p[0] - point_after_t[0]) ** 2 + (point_p[1] - point_after_t[1]) ** 2) ** 0.5
            for i in range(len(all_extremes) - 1):
                if all_extremes[i][0] < (abs(point_t[0] - point_p[0]) // 2) + point_t[0]:
                    continue
                point_b = all_extremes[i]
                length_tr_b = ((point_b[0] - point_after_t[0]) ** 2 + (point_b[1] - point_after_t[1]) ** 2) ** 0.5
                length_p_b = ((point_b[0] - point_p[0]) ** 2 + (point_b[1] - point_p[1]) ** 2) ** 0.5
                # теорема косинусов для определения угла отклонени я
                angle = math.acos(
                    (length_tr_p ** 2 + length_tr_b ** 2 - length_p_b ** 2) / (2 * length_tr_p * length_tr_b))
                # небольшой коофицент погрешности для более точного определения
                angle += ((abs(point_b[0] - point_t[0]) / (abs(point_t[0] - point_p[0]) // 10)) * 0.03)
                all_points_b.append((point_b[0], point_b[1], angle))
            point_before_p = max(all_points_b, key=lambda x: x[2])[:2]
            all_points_lp.append(point_before_p)
            # ▼ визуализация ▼
            cv.circle(img, point_after_t[:2], 4, (255, 255, 255), -1)
            cv.circle(img, point_before_p[:2], 4, (255, 255, 255), -1)

        self.dict_of_points['RT'] = all_points_rt
        self.dict_of_points['LP'] = all_points_lp
        return True

    def __defining_intervals_s_t(self):
        """
        Находит точки для интервала между S и T

        :return: True если всё хорошо
        """
        img = cv.imread(f'result.jpg')
        all_points_lt = []  # левее Т
        all_points_rs = []  # правее S
        for point_s in self.dict_of_points['S']:
            point_t = self.dict_of_points['T'][-1]
            for point in self.dict_of_points['T']:
                if point[0] < point_s[0]:
                    continue
                if point[0] < point_t[0]:
                    point_t = point

            # выбирает все точки из промежутка между S и T
            all_extremes = list(filter(lambda x: point_s[0] < x[0] <= point_t[0], self.__all_points))
            if len(all_extremes) < 1:
                continue
            length_st = ((point_t[0] - point_s[0]) ** 2 + (point_t[1] - point_s[1]) ** 2) ** 0.5  # теорема Пифагора
            all_points_b = []
            for i in range(len(all_extremes) - 1):
                if all_extremes[i][0] > (abs(point_t[0] - point_s[0]) // 2) + point_s[0]:
                    break
                point_b = all_extremes[i]
                length_tb = ((point_t[0] - point_b[0]) ** 2 + (point_t[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора
                length_bs = ((point_s[0] - point_b[0]) ** 2 + (point_s[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора
                # теорема косинусов для определения угла отклонения
                angle = math.acos((length_bs ** 2 + length_st ** 2 - length_tb ** 2) / (2 * length_bs * length_st))
                height = length_bs * math.sin(angle)
                # небольшой коофицент погрешности для более точного определения
                height += ((abs(point_b[0] - point_s[0]) / (abs(point_t[0] - point_s[0]) // 10)) * 0.3)

                all_points_b.append((point_b[0], point_b[1], height))
            if len(all_points_b) == 0:
                continue
            point_rs = max(all_points_b, key=lambda x: x[2])[:2]
            all_points_rs.append(point_rs)

            length_rs_t = ((point_t[0] - point_rs[0]) ** 2 + (point_t[1] - point_rs[1]) ** 2) ** 0.5  # теорема Пифагора
            all_points_b = []
            for i in range(len(all_extremes) - 1):
                if all_extremes[i][0] > (abs(point_t[0] - point_s[0]) / 3) * 2 + point_s[0]:
                    break
                if all_extremes[i][0] <= point_rs[0]:
                    continue
                point_b = all_extremes[i]
                length_tb = ((point_t[0] - point_b[0]) ** 2 + (point_t[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора
                length_b_rs = ((point_rs[0] - point_b[0]) ** 2 + (
                        point_rs[1] - point_b[1]) ** 2) ** 0.5  # теорема Пифагора
                if length_tb + length_b_rs <= length_rs_t:  # основное свойства существования треуголька
                    continue
                # теорема косинусов для определения угла отклонения и высоты относительно RS-T
                angle = math.acos(
                    (length_b_rs ** 2 + length_rs_t ** 2 - length_tb ** 2) / (2 * length_b_rs * length_rs_t))
                height = length_b_rs * math.sin(angle)
                # небольшой коофицент погрешности для более точного определения
                height += ((abs(point_b[0] - point_s[0]) / (abs(point_t[0] - point_s[0]) // 10)) * 0.3)

                all_points_b.append((point_b[0], point_b[1], height))
            if len(all_points_b) == 0:
                continue
            point_lt = max(all_points_b, key=lambda x: x[2])[:2]
            all_points_lt.append(point_lt)
            # ▼ визуализация ▼
            cv.circle(img, point_rs[:2], 4, (255, 255, 255), -1)
            cv.circle(img, point_lt[:2], 4, (255, 255, 255), -1)

        self.dict_of_points['LT'] = all_points_lt
        self.dict_of_points['RS'] = all_points_rs
        return True

    def __set_points_for_intervals(self):
        """
        Добавляет в основной словарь с ключевыми точками новые.
        Это просто объединение всех функций по определению каких-то определённых точек

        :return: None
        """

        self.__defining_intervals_t_p()
        self.__defining_intervals_s_t()
        self.__reserve_dict_of_points = copy.deepcopy(self.dict_of_points)

    def __is_r_distance_equal(self):
        """ Функция, которая проверяет, одинаковые ли расстояния между вершинами R, и присваивает __length_of_rs_in_mm
        среднее RR расстояние в милиметрах

        :return: None"""
        self.dict_of_points['R'].sort()
        self.__is_equal = True
        try:
            average_distance = self.dict_of_points['R'][1][0] - self.dict_of_points['R'][0][0]
        except IndexError:
            print('Недостаточно точек R для определения результата. Функция is_r_distance_equal.')
            self.__length_of_rs_in_mm = 0
            self.__is_equal = False
        else:
            interval = average_distance
            # В этом цикле за 1 проход вычисляются интервалы и определяется, равные ли расстояния между ними
            for i in range(1, len(self.dict_of_points['R']) - 1):
                if not (((self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]) -
                         (self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]) * 0.1) <= interval <=
                        ((self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]) +
                         (self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]) * 0.1)):
                    self.__is_equal = False
                interval = self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]
                average_distance += self.dict_of_points['R'][i + 1][0] - self.dict_of_points['R'][i][0]

            if len(self.dict_of_points['R']) == 2:  # Т.е. если у нас всего 2 вершины R
                self.__is_equal = True

            # Считаем среднее расстояние между вершинами R
            average_distance /= len(self.dict_of_points['R'])

            qua_of_squares = average_distance / self.__length_of_square  # Делим среднее
            # расстояние между вершинами на средную длину клеточки, чтобы вычислить, сколько клеточек между R-ками

            if self.__are_squares_big:
                self.__length_of_rs_in_mm = qua_of_squares * 5  # Если клеточки большие, то расстояние между R (в мм.)
                # равно количеству клеточек, умноженное на 5 (каждая большая клеточка - 5 мм)
            else:
                self.__length_of_rs_in_mm = qua_of_squares  # Если клеточки маленькие, то расстояние равно количеству
                # маленьких клеток, ведь клетки длиной по 1 мм

    def find_heart_rate(self):
        """Ищет ЧСС"""
        self.__is_r_distance_equal()
        if self.__length_of_rs_in_mm == 0:
            self.heart_rate = 0
        else:
            if self.speed_of_ecg == 25:
                self.heart_rate = round(60 / (self.__length_of_rs_in_mm * 0.04), 2)
            else:
                self.heart_rate = round(60 / (self.__length_of_rs_in_mm * 0.02), 2)

    def __convert_intervals_lengths_from_pixels_to_seconds(self):
        """Как понятно из названия, эта процедура переводит длины интервалов из пикслей в секунды и записывает их заново
         в dict_of_intervals

         :return: None"""
        for i in self.dict_of_intervals:
            for j in range(len(self.dict_of_intervals[i])):
                if self.__are_squares_big:
                    if self.speed_of_ecg == 25:
                        # интервал_в_секундах = интервал_в_пикселях/длина_клеточки_в_пикселях*время_клеточки
                        self.dict_of_intervals[i][j] = round(self.dict_of_intervals[i][j] / self.__length_of_square
                                                             * 0.2, 2)  # Размер одной большой клеточки - 0.5 см или
                        # 0,2 секунды
                    else:
                        self.dict_of_intervals[i][j] = round(self.dict_of_intervals[i][j] / self.__length_of_square
                                                             * 0.1, 2)  # Размер одной большой клеточки - 0.5 см
                        # или 0,1 секунды
                else:
                    if self.speed_of_ecg == 25:
                        self.dict_of_intervals[i][j] = round(self.dict_of_intervals[i][j] / self.__length_of_square
                                                             * 0.04, 2)  # Размер одной маленькой клеточки - 0,1 см
                        # или 0,04 секунды
                    else:
                        self.dict_of_intervals[i][j] = round(self.dict_of_intervals[i][j] / self.__length_of_square
                                                             * 0.02, 2)  # Размер одной одной маленькой клеточки -
                        # 0,1 см или 0,02 секунды

    def get_text_of_general_information(self):
        """Формирует всю известную по анализу информацию в одно строковое поле.

        :return: None"""
        self.prediction = 'Средние значения интервалов:\n'
        for i in self.dict_of_intervals:
            average_interval = 0
            for j in range(len(self.dict_of_intervals[i])):
                average_interval += self.dict_of_intervals[i][j]

            if len(self.dict_of_intervals[i]) > 2:
                average_interval = average_interval / (len(self.dict_of_intervals[i]))
            elif len(self.dict_of_intervals[i]) == 2:
                average_interval = average_interval / 2
            else:
                average_interval = average_interval
            if average_interval == 0:
                self.prediction += f'{i} - Недостаточно точек для определения.\n'
            else:
                self.prediction += f'{i} - {round(average_interval, 2)} сек.\n'
        self.prediction += f"ЧСС:\n{self.heart_rate} уд/мин.\nПервичное заключение:\n"
        if self.__length_of_rs_in_mm == 0:
            self.prediction += 'Недостаточно данных для заключения.'
        else:
            if self.__is_equal:
                self.prediction += 'Сердце бьётся ритмично. '
            else:
                self.prediction += 'Сердце бьётся не ритмично. '
            if self.heart_rate > 90:
                self.prediction += 'Наблюдается синусовая тахикардия.'
            elif self.heart_rate < 50:
                self.prediction += 'Наблюдается синусовая брадикардия.'
        return self.prediction

    def get_size_one_pixel(self):
        """Ищет время одного пикселя в секундах

        :return: Время одного пикселя"""
        average_w = 0
        if len(self.dict_of_points['R']) < 2:
            return 1
        for i in range(1, len(self.dict_of_points['R'])):
            point1 = self.dict_of_points['R'][i - 1]
            point2 = self.dict_of_points['R'][i]
            average_w += abs(point1[0] - point2[0])
        average_w = average_w / (len(self.dict_of_points['R']) - 1)
        interval_rr = sum(self.dict_of_intervals['RR']) / len(self.dict_of_intervals['RR'])
        return interval_rr / average_w

    def restart_graphic(self):
        """Перезагружает весь график, то есть стирает все изменения

        :return: None"""
        self.dict_of_points = copy.deepcopy(self.__reserve_dict_of_points)
        self.find_intervals()

    def find_intervals(self):
        """Процедура, объединяющая все действия по нахождению интервалов

        :return: None"""
        self.__get_intervals()
        self.__convert_intervals_lengths_from_pixels_to_seconds()
        self.find_heart_rate()

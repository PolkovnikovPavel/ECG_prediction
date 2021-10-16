import cv2 as cv
import numpy as np
import math
import re
import os


class Graphic:
    def __init__(self, image_full_name):
        # Параметры изображения
        self.__image_full_name = image_full_name
        self.__image_name = re.split(r'\.', self.__image_full_name)[0]
        self.__dict_of_points = None
        self.__length_of_square = None
        self.__all_extremes = None
        self.__all_points = None

    def __delete_background(self, is_show=True):
        """Удаление фона(костыль)

        Данная функция находит график кардиограммы и делает его белым цветом, а фон - чёрным
        Есть минус - она не универсальна и вряд ли заработает для других изображений

        :param is_show: is_show
        :return: ч/б изобрежение без фона
        """
        hsv_min = np.array((0, 0, 0), np.uint8)  # Минимальный порог цвета
        hsv_max = np.array((240, 255, 120), np.uint8)  # Максимальный порог цвета

        img = cv.imread(f'images/{self.__image_name}.jpeg')  # Чтение изображения
        if is_show:
            cv.imshow('Original', img)  # Показывает изображение

        img_in_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # Перевод изображения из цветовой палитры RGB
        # (порядок изнальчно изменён, BGR) в палитру HSV
        img_with_hsv_filter = cv.inRange(img_in_hsv, hsv_min, hsv_max)  # Применяет к изобрежнию фильтр

        if is_show:
            cv.imshow('Filtered', img_with_hsv_filter)  # Показывает обработанное изображение
            cv.waitKey(0)
        cv.imwrite(f'images/{self.__image_name}_w-b.jpeg', img_with_hsv_filter)  # Сохраняет новое изображение

        return img_with_hsv_filter

    def __otsus_method(self, is_show=True):
        """Удаление фона

        Метод Оцу, который автоматически подбирает порог цвета и удаляет фон

        :param is_show: is_show
        :return: ч/б изображение без заднего фона (только график ЭКГ)
        """
        img = cv.imread(f'images/{self.__image_name}.jpeg')  # Чтение изображения
        if is_show:
            cv.imshow("Original", img)  # Показ изображения

        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Преобразование исходного изображения в ч/б
        blur_img = cv.GaussianBlur(gray_img, (3, 3), 0)  # Размытие изображения для удаления клеточек

        img_with_filter = cv.threshold(blur_img, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]  # Применение фильтра
        if is_show:
            cv.imshow("Filtered", img_with_filter)  # Показ изображения
            cv.waitKey(0)
        cv.imwrite(f'images/{self.__image_name}-Otsus.jpeg', img_with_filter)  # Сохранение изображения

        return img_with_filter

    def __find_square_length(self, is_show=True):
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
        img = cv.imread(f'images/{self.__image_name}.jpeg', cv.IMREAD_GRAYSCALE)
        if is_show:
            cv.imshow("Original", img)
            cv.waitKey(0)

        # График ЭКГ
        graphic = self.__otsus_method(False)
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
        cv.imwrite(f'images/{self.__image_name}_w-o_graphic.jpeg', blur_img)
        variable = self.__image_name
        self.__image_name = self.__image_name + '_w-o_graphic'
        # Пропускаем ещё раз через фильтр Оцу, чтобы выделить клеточки
        img_with_out_graphic_otsus = self.__otsus_method(False)
        self.__image_name = variable
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

        """
        У алгоритма существует некоторая погрешность, из-за которой он иногда находит либо сколько пикселей в большой, 
        либо в маленькой клеточке. Из-за этого, стоит в других функция проверить количество клеток. Если он слишком 
        мало, то алгоритм определил количество больших клеточек. Если слишком велико - то маленьких.
        """
        self.__length_of_square = average_length

    def crop_image(self, n, is_show=True):
        """Обрезает изображение сверху и снизу на n пиксель

        :param n: число пикселей, на которое изображение обрежется
        :param is_show: is_show
        :return: обрезанное изображение
        """
        img = cv.imread(f'images/{self.__image_name}.jpeg')
        y0 = n
        y1 = img.shape[0] - n
        crop_img = img[y0:y1]
        if is_show:
            cv.imshow('cropped', crop_img)
            cv.waitKey(0)
        cv.imwrite(f'images/{self.__image_name}.jpeg', crop_img)

        return crop_img

    def convert_to_jpeg(self):
        """Переводит выбранный файл в формат .jpeg и удаляет исходный
        """
        img = cv.imread(f'images/{self.__image_full_name}')
        img_name = re.split(r'\.', self.__image_full_name)[0]
        cv.imwrite(f'images/{img_name}.jpeg', img)
        os.remove(f'images/{self.__image_full_name}')

    @staticmethod
    def __get_digitization_image(img):
        """Обрабатывает изображение, заменяя все светлые цвета на белый.

        :param img: изображение
        :return: изображение, где все цвета кроме чёрного - белые
        """
        img_list = np.where(img > 0, 1, 0)
        return img_list

    def __find_extremes_and_points(self, array, is_show=True):
        """Ищет экстремумы на графике и может их затем продемонстрировать.

        :param array: изображение, прошедшие удаление заднего фона и переведённое в нолики и единички
        :param is_show: is_show
        :return: список всех экстремумов [координата х, координата у, точка экстремума/точка перегиба]
        """
        last_points = []  # результат (х, у, id)
        # id:
        # 1) точка экстремума
        # 2) просто точка
        is_upper = True  # показатель, того, куда двигается прямая (вверх или вниз)
        last_angle = 0  # угол для предыдущего столбца (который был добавлен в список)
        last_average_y = (0, [0])  # это данные о предыдущем столбце (для вычислений)
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

        self.__all_points = last_points

        self.__all_extremes = list(filter(lambda x: x[2] == 1, self.__all_points))

    def __get_and_find_points_r(self, is_show=True):  # многоуровневая сортировка (выведение точек R)
        """Находит все точки R.

        Суть работы
        ___________________________________________
        Можно заметить, что растояние у точек R до соседних изломов больше чем у большенства.
        А так же они обычно выше остальных.
        На этом основана следующая сортировка
        __________________________________________

        :param is_show: показывать результат или нет
        :return: r_points - список точек R (x, y)
        """

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
            point_end = (sum(all_x) // len(all_x), sum(all_y) // len(all_y))   # добавляем результат группы (даже если
            # 1-а)
            if point_end not in r_points_end:
                r_points_end.append(point_end)
        r_points = r_points_end   # присваевыем результат к конечному списку

        if is_show:  # просто отображение результата (не обязательно)
            img = cv.imread(f'result.jpeg')
            cv.line(img, (0, int(minimum_boundary)), (np.size(img, 1), int(minimum_boundary)), (255, 0, 255), 1)
            for point in r_points:
                point = point[:2]
                cv.circle(img, point, 5, (255, 0, 255), -1)
            cv.imwrite(f'result.jpg', img)
            cv.imshow("Image", img)
            cv.waitKey(0)

        return r_points

    def __get_and_find_points_q_and_s(self, points_r):   # отдаёт 2 списка с точками Q и S
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

        list_of_x_r = list(map(lambda x: x[0], points_r))   # определяет среднию дистанцию между R
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
            points_s.append(max(list_of_points_s, key=lambda x: x[1]))   # берёт самую низкую точку из указанного
            # диапазона
            points_q.append(max(list_of_points_q, key=lambda x: x[1]))

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
        for i in range(len(points_r)):   # проверяет каждую точку R
            if i < len(points_r) - 1:
                width = points_r[i + 1][0] - points_r[i][0]   # растояние по оси Х между RR
                average_width_r += width   # среднее растояние
                points = list(filter(lambda x: points_r[i][0] < x[0] < points_r[i][0] + width / 2,
                                     self.__all_extremes))
                # это самое главное - выбирает все точки, принадлежащие диапозону

                points.sort(key=lambda x: x[1])
                average_dist += points[0][0] - points_r[i][0]   # то на сколько точка Т удалена от R
                points_t.append(points[0])
            else:   # работет при обработке диапозона после последней точки R.
                # Тут-то и нужны average_dist и average_width_r
                average_width_r = average_width_r / (len(points_r) - 1)
                average_dist = average_dist / (len(points_r) - 1)
                points = list(filter(lambda x: points_r[i][0] < x[0] < points_r[i][0] + average_width_r / 2,
                                     self.__all_extremes))
                points.sort(key=lambda x: x[1])
                dist = points[0][0] - points_r[i][0]
                if average_dist * 0.75 < dist < average_dist * 1.25:
                    points_t.append(points[0])   # нужно, чтоб последняя точка не выбивалось от большенства
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
        for i in range(len(points_r) - 1, -1, -1):   # проверяет каждую точку R в обратном порядке
            if i > 0:
                width = points_r[i][0] - points_r[i - 1][0]   # растояние по оси Х между RR
                average_width_r += width   # среднее растояние
                points = list(filter(lambda x: points_r[i][0] > x[0] > points_r[i][0] - width / 2,
                                     self.__all_extremes))
                # это самое главное - выбирает все точки, принадлежащие диапозону

                points.sort(key=lambda x: x[1])
                average_dist += points_r[i][0] - points[0][0]   # то на сколько точка Р удалена от R
                points_p.append(points[0])
            else:   # работет при обработке диапозона перед первой точкой R. Тут-то и нужны average_dist и
                # average_width_r
                average_width_r = average_width_r / (len(points_r) - 1)
                average_dist = average_dist / (len(points_r) - 1)
                points = list(filter(lambda x: points_r[i][0] > x[0] > points_r[i][0] - average_width_r / 2,
                                     self.__all_extremes))
                points.sort(key=lambda x: x[1])
                dist = points_r[i][0] - points[0][0]
                if average_dist * 0.75 < dist < average_dist * 1.25:
                    points_p.append(points[0])   # нужно, чтоб самая первая точка не выбивалось от большенства
        return points_p

    def get_dictionary_of_key_points(self, is_show=True):
        """
        Функция, которая объеденяет все операции по вычислению ключевых точек.

        :param is_show: is_show
        :return: словарь со всеми ключевыми точками, и даже R
        """

        key_points = {}
        colors = {'R': (255, 0, 255),   # цвета
                  'Q': (0, 200, 255),
                  'S': (0, 255, 193),
                  'T': (255, 214, 145),
                  'P': (92, 0, 255)}

        if self.__all_points is None:
            self.__find_extremes_and_points(self.__get_digitization_image(self.__otsus_method(False)), False)

        all_extremes = list(filter(lambda x: x[2] == 1, self.__all_points))   # выделяет из все точек только экстремумы
        all_points_r = self.__get_and_find_points_r(False)   # точки R
        all_points_r.sort(key=lambda x: x[0])   # сортировка по возврастанию Х
        all_extremes.sort(key=lambda x: x[0])

        points_q, points_s = self.__get_and_find_points_q_and_s(all_points_r)   # точки Q и S
        points_t = self.__get_and_find_points_t(all_points_r)   # точки T
        points_p = self.__get_and_find_points_p(all_points_r)   # точки P

        key_points['R'] = all_points_r
        key_points['Q'] = points_q
        key_points['S'] = points_s
        key_points['T'] = points_t
        key_points['P'] = points_p

        if is_show:   # вывод результата
            img = cv.imread(f'result.jpeg')
            for type in key_points:
                for point in key_points[type]:
                    point = point[:2]
                    cv.circle(img, point, 4, colors[type], -1)
            cv.imwrite(f'result.jpg', img)
            cv.imshow("Image", img)
            cv.waitKey(0)

        self.__dict_of_points = key_points

        return key_points

    def __is_r_distance_equal(self, list_of_rs):
        """ Функция, которая проверяет, одинаковые ли расстояния между вершинами R и возвращает время в секундах.

        :param list_of_rs: список с координатами всех точек R
        :return: Возвращает список, где равное ли расстояние между R, количество больших клеточек между ними и время
        в сек.
        """
        list_of_rs.sort()  # Сортируется входной список R
        is_equal = True  # Переменная, отвечающая за результат
        list_of_distance = []  # Список расстояний между вершинами
        for i in range(len(list_of_rs) - 1):  # Вычислений расстояний между вершинами
            list_of_distance.append(list_of_rs[i + 1][0] - list_of_rs[i][0])

        average_distance = list_of_distance[0]  # Среднее растояние между вершинами R (сразу присваивается
        # нулевой элемент),
        # на случай, если на ЭКГ только 2 вершины R
        for i in range(len(list_of_distance) - 1):  # ЕСЛИ расстояние между двумя вершинами равно или +-10%, то всё ок,
            # ИНАЧЕ прекращаем выполнение
            average_distance += list_of_distance[i + 1]
            if not ((list_of_distance[i] <= list_of_distance[i + 1] + list_of_distance[i + 1] * 0.1) and (
                    list_of_distance[i] >= list_of_distance[i + 1] - list_of_distance[i + 1] * 0.1)):
                is_equal = False

        if len(list_of_distance) == 1:  # Т.е. если у нас всего 2 вершины R
            is_equal = True

        # Считаем среднее расстояние между вершинами R
        average_distance //= len(list_of_distance)

        # Находим размер клеточки и считаем время
        if self.__length_of_square is None:
            self.__find_square_length(False)
        time_of_rs = self.__length_of_square
        time_of_rs, qua_of_squares = average_distance // time_of_rs, average_distance // time_of_rs  # Делим среднее
        # расстояние между вершинами на средную длину клеточки, что вычислить, сколько клеточек между R-ками

        # Это условие позволяет на последнем этапе убирать шумы контуров, если они каким-то чудом смогли сюда добраться,
        # путём обощения маленьких контуров в большую клетку
        if qua_of_squares < 6:
            time_of_rs = round(time_of_rs * 0.2, 2)  # Размер одной больщой клеточки - 2,5 см или 0,2 секунды
        else:
            qua_of_squares /= 5
            time_of_rs = round(time_of_rs * 0.04, 2)  # Размер одной маленькой клеточки - 0,5 см или 0,04 секунды

        return [is_equal, qua_of_squares, time_of_rs]


graphic = Graphic('ECG-1.jpeg')
print(graphic.get_dictionary_of_key_points(False))

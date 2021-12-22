import cv2 as cv
import pyglet
from data.main_cycle import *
from data.objects import *
# имеет смысл только при полном экране (оно меняет временно разрешение экрана)
# print(ScreenRes.get_modes())
# x = ScreenRes.get_modes()
# ScreenRes.set(1280, 720)
# ScreenRes.set()  # Set defaults


# ▼ инициализация ▼
master = tkinter.Tk()
master.iconbitmap('app_images/Logo.ico')
master.title('ЭКГ помощник')
# master.attributes('-fullscreen', True)  # полный экран
screen_w = master.winfo_screenwidth()
screen_h = master.winfo_screenheight()
if screen_w > screen_h:
    rotation = screen_w / screen_h
    if rotation >= 1.8:
        screen_h *= 0.7
        screen_w = screen_h * 1.6
    elif rotation >= 1.6:
        screen_w *= 0.7
        screen_h *= 0.7
    else:
        screen_w *= 0.7
        screen_h = screen_w / 1.6
else:
    rotation = screen_h / screen_w
    screen_w *= 0.8
    screen_h = screen_w / 1.6
initialize_w_and_h(screen_w, screen_h)
canvas = tkinter.Canvas(master, bg='#000000', height=screen_h - 2, width=screen_w - 2)
canvas.pack(fill=tkinter.BOTH, expand=1)
master.resizable(False, False)

print(screen_w, screen_h)

all_gropes = []

main_group = Group()
all_gropes.append(main_group)
view_grope = Group()
all_gropes.append(view_grope)
main_cycle = MainCycle(canvas, all_gropes)

bg = Object(0, 0, pw(100), ph(100), 'background.png', canvas)  # с этого места идёт создание необходимых объектов
main_group.add_objects(bg)
exit_btn = Button(pw(95), ph(3), ph(6), ph(6), 'exit_button.png', canvas, 'exit_button_2.png', main_cycle.close_window)
main_group.add_objects(exit_btn)

btn = Button(pw(34), ph(44), ph(12), ph(12), 'open_file.png', canvas, 'open_file_2.png', main_cycle.set_file_name)
main_group.add_objects(btn)

btn = Button(pw(46), ph(44.5), pw(20), pw(6), 'start_scanning.png', canvas, 'start_scanning_2.png',
             main_cycle.start_scanning)
main_group.add_objects(btn)

# Наш тэг
pyglet.font.add_file("app_images/Montserrat-Regular.ttf")
pyglet.font.add_file("app_images/Montserrat-Bold.ttf")
main_group.add_objects(Text(pw(1), ph(89), f'Сергей - puhovskijsa@kuzstu.ru\nПавел - pavelpolkovnikov334@gmail.com',
                            canvas, font=f'Montserrat {ph(3)} bold', visibility=True, color='#798a9c'))

master.protocol("WM_DELETE_WINDOW", main_cycle.close_window)  # ▼ всё что ниже - неизменно ▼
master.bind('<Motion>', main_cycle.mouse_move)
master.bind('<Button-1>', main_cycle.click)
master.bind('<ButtonRelease-1>', main_cycle.click_out)
master.bind('<Button-3>', main_cycle.right_click)
master.bind('<ButtonRelease-3>', main_cycle.right_click_out)
master.bind('<MouseWheel>', main_cycle.mouse_wheel)
master.bind('<Key>', main_cycle.pressing_keyboard)

main_cycle.start()
ScreenRes.set()  # Set defaults разрешение экрана

from graphic import Graphic
"""
Файл для анализа данных
"""

gr = Graphic('images/Tachycardia_ECG.jpeg', 25)  # Bradycardia_ECG.jpeg
gr.graph_detection()

result = ''

if gr.is_equal:
    result = 'Сердце бьётся ритмично. '
else:
    result = 'Сердце бьётся не ритмично. '
if gr.characteristics[0] > 90:
    result += 'Наблюдается синусовая тахикардия. '
elif gr.characteristics[0] < 50:
    result += 'Наблюдается синусовая брадикардия. '

print(result)
gr.show_result()
print(gr.characteristics[0])

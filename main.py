from graphic import Graphic
"""
Файл для анализа данных
"""

gr = Graphic('ECG-1.jpeg', 25)  # Bradycardia_ECG.jpeg Tachycardia_ECG.jpeg
gr.graph_detection()
print(gr.get_text_of_general_information())

gr.show_result()


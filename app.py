from flask import Flask, request, render_template, send_file
import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg') # Важно! Чтобы графики рисовались без открытия окон
import matplotlib.pyplot as plt
import io
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') # Отдаем HTML страницу

@app.route('/plot', methods=['POST'])
def plot():
    # 1. Получаем текст от пользователя
    user_input = request.form.get('expression', '')
    x_min = float(request.form.get('x_min', -10))
    x_max = float(request.form.get('x_max', 10))
    
    if not user_input:
        return "Введите функцию", 400

    # 2. Очистка и подготовка "промпта" (самое важное для курсовой!)
    # Пользователь может написать |x| или arctan, а SymPy хочет Abs(x) и atan(x)
    processed_input = user_input.replace('|', '') # Убираем палочки, если они кривые
    processed_input = processed_input.replace('arctan', 'atan')
    processed_input = processed_input.replace('arcsin', 'asin')
    processed_input = processed_input.replace('arccos', 'acos')
    processed_input = processed_input.replace('^', '**') # Замена степени
    
    # Обработка модуля |x| -> Abs(x) (упрощенно, regex)
    processed_input = re.sub(r'\|(.*?)\|', r'Abs(\1)', processed_input)
    
    try:
        # 3. Парсинг математики
        x = sp.symbols('x')
        expr = sp.sympify(processed_input)
        
        # 4. Генерация данных
        # Превращаем символьное выражение в быструю функцию numpy
        f = sp.lambdify(x, expr, 'numpy')
        
        x_vals = np.linspace(x_min, x_max, 1000)
        
        # Считаем Y, игнорируя возможные ошибки (например, деление на ноль)
        with np.errstate(all='ignore'):
            y_vals = f(x_vals)
        
        # 5. Рисование графика
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, label=f'y = {user_input}')
        plt.title('График функции')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)
        plt.legend()
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        
        # 6. Сохранение в буфер и отправка
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return f"Ошибка в функции: {e}. Проверьте синтаксис.", 400

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, render_template, send_file
import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/plot', methods=['POST'])
def plot():
    user_input = request.form.get('expression', '')
    x_min = float(request.form.get('x_min', -10))
    x_max = float(request.form.get('x_max', 10))
    if not user_input:
        return "Введите функцию", 400
    processed_input = user_input.replace('|', '')
    processed_input = processed_input.replace('arctan', 'atan')
    processed_input = processed_input.replace('arcsin', 'asin')
    processed_input = processed_input.replace('arccos', 'acos')
    processed_input = processed_input.replace('^', '**') # Замена степени
    processed_input = re.sub(r'\|(.*?)\|', r'Abs(\1)', processed_input)
    try:
        #парсинг
        x = sp.symbols('x')
        expr = sp.sympify(processed_input)
        f = sp.lambdify(x, expr, 'numpy')
        x_vals = np.linspace(x_min, x_max, 1000)
        with np.errstate(all='ignore'):
            y_vals = f(x_vals)

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, label=f'y = {user_input}')
        plt.title('График функции')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)
        plt.legend()
        plt.axhline(0, color='black', linewidth=0.5)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return f"Ошибка в функции: {e}. Проверьте синтаксис.", 400

if __name__ == '__main__':
    app.run(debug=True)

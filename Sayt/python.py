from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageEnhance
import requests
import os
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1 MB limit for uploaded files
UPLOAD_FOLDER = './uploads'  # папка для загруженных файлов
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
RECAPTCHA_SITE_KEY = '6Lftbe0lAAAAAOp4w1qoU6iEwm9agJfcn3Xpxs_0'   


@app.route('/resize', methods=['POST'])
def resize():
    
    file = request.files.get('file')
    resize = float(request.form.get('resize'))
   

    # Проверка, был ли загружен файл
    if not file:
        abort(400, 'No file was uploaded')

    # Проверка, является ли загруженный файл изображением
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        abort(400, 'File is not an image')

    # Verify the captcha
    recaptcha_response = request.form.get('g-recaptcha-response')
    if not recaptcha_response:
        abort(400, 'reCAPTCHA verification failed')
    payload = {
        'secret': '6Lftbe0lAAAAAHoyStfvRN-UMnHERrK0bjaRX3zW',
        'response': recaptcha_response
    }
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', payload).json()
    if not response['success']:
        abort(400, 'reCAPTCHA verification failed')

    # Загрузка и изменение размеров изображения
    img = Image.open(file)
    width, height = img.size
    new_size = (int(width * resize),int (height * resize))

    resized_img = img.resize(new_size)

    #Вычисление распределения цветов оригинального и уменьшенного изображений
    orig_colors = get_color_distribution(img)
    resized_colors = get_color_distribution(resized_img)

    # Отображение распределений цветов на графиках
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Color Distribution')
    ax1.bar(np.arange(len(orig_colors)), [c[0]/255 for c in orig_colors], color=[tuple(np.array(c[1])/255) for c in orig_colors])
    ax1.set_xticks(np.arange(len(orig_colors)))
    ax1.set_xticklabels([c[1] for c in orig_colors], rotation=45)
    ax1.set_title('Original Image')
    ax2.bar(np.arange(len(resized_colors)), [c[0]/255 for c in resized_colors], color=[tuple(np.array(c[1])/255) for c in resized_colors])
    ax2.set_xticks(np.arange(len(resized_colors)))
    ax2.set_xticklabels([c[1] for c in resized_colors], rotation=45)
    ax2.set_title('Resized Image')
    plt.tight_layout()

    # Сохранение графика в файл
    plot_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
    plt.savefig(plot_filename)

    # Сохранение уменьшенного изображения в файл
    resized_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'resized.png')
    resized_img.save(resized_filename)
    orig_filename = os.path.join(app.config['UPLOAD_FOLDER'],'orig.png')
    img.save(orig_filename)

    # Отображение результата на HTML странице
    result_filename = os.path.basename(plot_filename) #  получение только имени файла
    # Open the plot image as a binary file
    with open(plot_filename, 'rb') as f:
        plot_bytes = f.read() 


    # Encode the plot image as base64 for display in the HTML page
    plot_base64 = base64.b64encode(plot_bytes).decode('utf-8')

    return render_template('resyltat.html', orig=orig_filename, plot=plot_base64, result_filename=result_filename)


# Home page
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', sitekey=RECAPTCHA_SITE_KEY)


# Utility function to get color distribution of an image
def get_color_distribution(img):
    colors = img.getcolors(img.size[0] * img.size[1])
    return sorted(colors, key=lambda x: x[0], reverse=True)[:10]


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/split', methods=['POST'])
def split():
    items = []
    total = 0

    gst_rate = 0.09 if request.form.get('gst') else 0
    service_rate = 0.10 if request.form.get('service') else 0

    i = 0
    while True:
        name = request.form.get(f'item_{i}')
        price = request.form.get(f'price_{i}')
        person = request.form.get(f'person_{i}')
        if not name or not price or not person:
            break
        price = float(price)
        items.append({'item': name, 'price': price, 'person': person})
        total += price
        i += 1

    gst_amount = total * gst_rate
    service_amount = total * service_rate
    final_total = total + gst_amount + service_amount

    per_person = {}
    for item in items:
        person = item['person']
        if person not in per_person:
            per_person[person] = 0
        per_person[person] += item['price']

    for person in per_person:
        share = per_person[person] / total
        per_person[person] += share * (gst_amount + service_amount)
        per_person[person] = round(per_person[person], 2)

    return render_template('result.html', per_person=per_person, total=round(final_total, 2))

@app.route('/upload', methods=['POST'])
def upload_receipt():
    if 'receipt' not in request.files:
        return "No file uploaded."

    file = request.files['receipt']
    if file.filename == '':
        return "No selected file."

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = pytesseract.image_to_string(Image.open(filepath))

    return render_template('ocr_result.html', raw_text=text)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


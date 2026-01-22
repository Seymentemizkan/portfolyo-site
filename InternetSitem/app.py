from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import base64

# ============== SENİN PROJELERINDEN IMPORT ==============
# QrGenerator/main.py'den
import qrcode
from PIL import Image

# PasswordGenerator/main.py'den  
import secrets
import string

app = Flask(__name__)

# ============== ANA SAYFALAR ==============

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hakkimda')
def about():
    return render_template('about.html')

@app.route('/projeler')
def projects():
    return render_template('projects.html')

@app.route('/araclar')
def tools():
    return render_template('tools.html')

# ============== ARAÇLAR ==============

# QR Code Generator (QrGenerator/main.py mantığı ile)
@app.route('/araclar/qr-generator')
def qr_generator():
    return render_template('tools/qr_generator.html')

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    """
    QrGenerator/main.py'deki kodun web versiyonu
    Orijinal: code = qrcode.QRCode(version=1, error_correction=..., box_size=10, border=1)
    """
    data = request.json.get('data', '')
    if not data:
        return jsonify({'error': 'Veri gerekli'}), 400
    
    # Senin QrGenerator kodundaki ayarlar
    code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,  # Senin kodunda border=1 vardı
    )
    
    code.add_data("{}".format(data))  # Senin formatın
    code.make(fit=True)
    
    # Senin kodundaki renk ayarları (back_color typo düzeltildi)
    image = code.make_image(fill_color="black", back_color="white")
    
    # Web için base64'e çevir
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'image': f'data:image/png;base64,{img_base64}'})

# Şifre Oluşturucu (PasswordGenerator/main.py mantığı ile)
@app.route('/araclar/sifre-olusturucu')
def password_generator():
    return render_template('tools/password_generator.html')

@app.route('/api/generate-password', methods=['POST'])
def generate_password():
    """
    PasswordGenerator/main.py'deki passwordGenerator fonksiyonunun web versiyonu
    Orijinal: characters = string.ascii_letters + punctuation + digits
    """
    data = request.json
    length = data.get('length', 16)
    use_uppercase = data.get('uppercase', True)
    use_lowercase = data.get('lowercase', True)
    use_numbers = data.get('numbers', True)  # Senin kodunda: include_digits
    use_symbols = data.get('symbols', True)  # Senin kodunda: include_special
    
    # Senin PasswordGenerator mantığı
    characters = ''
    
    # Senin kodunda: characters = string.ascii_letters (hem büyük hem küçük)
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    
    # Senin kodunda: if include_digits == "yes": characters += string.digits
    if use_numbers:
        characters += string.digits
    
    # Senin kodunda: if include_special == "yes": characters += string.punctuation
    if use_symbols:
        characters += string.punctuation
    
    if not characters:
        return jsonify({'error': 'En az bir karakter türü seçmelisiniz'}), 400
    
    # Senin kodundaki secrets.choice kullanımı
    password = ''.join(secrets.choice(characters) for _ in range(int(length)))
    
    return jsonify({'password': password})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

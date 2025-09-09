# Image Steganography Tool
# Hide and extract secret messages in images using LSB (Least Significant Bit) technique

import os
import sys
from PIL import Image
import numpy as np
from flask import Flask, render_template, request, jsonify
import base64

class Steganography:
    @staticmethod
    def encode_message(image_path, message, output_path):
        """Hide a message inside an image using LSB steganography"""
        try:
            input_ext = os.path.splitext(image_path)[1].lower()
            output_ext = os.path.splitext(output_path)[1].lower()

            # Warn for JPEG
            if output_ext in ['.jpg', '.jpeg']:
                print("⚠️ JPEG format may corrupt hidden data. Use PNG instead.")
                return False, "Encoding cancelled. Please use PNG format."

            # Open image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)

            message += "<<<END>>>"
            binary_message = ''.join(format(ord(c), '08b') for c in message)

            max_capacity = img_array.size
            if len(binary_message) > max_capacity:
                return False, "Message too long for this image."

            flat_img = img_array.flatten()
            for i in range(len(binary_message)):
                flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])

            encoded_img_array = flat_img.reshape(img_array.shape)
            encoded_img = Image.fromarray(encoded_img_array.astype('uint8'))
            encoded_img.save(output_path)

            return True, "Message successfully hidden in image."
        except Exception as e:
            return False, f"Error encoding message: {str(e)}"

    @staticmethod
    def decode_message(image_path):
        """Extract hidden message from an image"""
        try:
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)

            flat_img = img_array.flatten()
            binary_message = "".join(str(pixel & 1) for pixel in flat_img)

            message = ""
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                if len(byte) < 8:
                    break
                char = chr(int(byte, 2))
                message += char
                if message.endswith("<<<END>>>"):
                    return True, message[:-9]

            return False, "No hidden message found."
        except Exception as e:
            return False, f"Error decoding message: {str(e)}"


class TerminalMode:
    def __init__(self):
        self.stego = Steganography()

    def run(self):
        """Run the terminal interface"""
        while True:
            print("\n" + "="*50)
            print("IMAGE STEGANOGRAPHY TOOL - TERMINAL MODE")
            print("="*50)
            print("1. Encode message into image")
            print("2. Decode message from image")
            print("3. Exit")

            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == '1':
                self.encode_terminal()
            elif choice == '2':
                self.decode_terminal()
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def encode_terminal(self):
        print("\n--- ENCODE MESSAGE ---")
        image_path = input("Enter path to input image: ").strip()
        if not os.path.exists(image_path):
            print("Error: Image not found!")
            return

        message = input("Enter secret message: ").strip()
        if not message:
            print("Error: Message cannot be empty!")
            return

        output_path = input("Enter output image path (with extension): ").strip()
        if not output_path:
            output_path = "encoded_image.png"

        success, result = self.stego.encode_message(image_path, message, output_path)
        print("✓" if success else "✗", result)

    def decode_terminal(self):
        print("\n--- DECODE MESSAGE ---")
        image_path = input("Enter path to encoded image: ").strip()
        if not os.path.exists(image_path):
            print("Error: Image not found!")
            return

        success, result = self.stego.decode_message(image_path)
        print("✓" if success else "✗", result)


# Flask Web Application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encode', methods=['POST'])
def encode_api():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image uploaded'})

        file = request.files['image']
        message = request.form.get('message', '').strip()

        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No image selected'})
        if not message:
            return jsonify({'success': False, 'message': 'Message cannot be empty'})

        temp_input = 'temp_input.png'
        temp_output = 'temp_output.png'
        file.save(temp_input)

        stego = Steganography()
        success, result = stego.encode_message(temp_input, message, temp_output)

        if success:
            with open(temp_output, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()

            os.remove(temp_input)
            os.remove(temp_output)

            return jsonify({'success': True, 'message': result, 'image_data': img_data})
        else:
            os.remove(temp_input)
            return jsonify({'success': False, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/decode', methods=['POST'])
def decode_api():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image uploaded'})

        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No image selected'})

        temp_input = 'temp_decode.png'
        file.save(temp_input)

        stego = Steganography()
        success, result = stego.decode_message(temp_input)

        os.remove(temp_input)
        return jsonify({'success': success, 'message': result, 'decoded_message': result if success else ''})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def main():
    print("="*60)
    print("WELCOME TO IMAGE STEGANOGRAPHY TOOL")
    print("="*60)
    print("Choose your preferred mode:")
    print("1. Terminal Mode")
    print("2. GUI Mode (Web)")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == '1':
            TerminalMode().run()
            break
        elif choice == '2':
            print("\nStarting GUI Mode at http://localhost:5000")
            os.makedirs('templates', exist_ok=True)

            # Dark mode frontend
            html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Steganography Tool</title>
<style>
/* === DARK MODE STYLE === */
body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; padding: 20px; display:flex;justify-content:center;align-items:center;height:100vh; }
.container { max-width:800px;width:100%;background:rgba(30,30,30,0.9);border-radius:16px;padding:30px;box-shadow:0 8px 25px rgba(0,0,0,0.6);}
.header { text-align:center;margin-bottom:20px;}
.header h1 { font-size:2rem; background:linear-gradient(90deg,#00c6ff,#0072ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.mode-selector { display:flex; margin-bottom:20px; }
.mode-btn { flex:1; padding:12px; background:#1f1f1f; border:none; color:#bbb; cursor:pointer; transition:0.3s; }
.mode-btn.active { background:linear-gradient(90deg,#00c6ff,#0072ff); color:white; font-weight:bold;}
.mode-btn:hover:not(.active){background:#292929;}
.section { display:none;}
.section.active { display:block; }
label { display:block;margin-bottom:6px;color:#ddd;font-weight:600;}
.file-input-label { display:block;padding:14px;background:rgba(255,255,255,0.05);border:2px dashed #555;border-radius:10px;text-align:center;cursor:pointer;color:#aaa;transition:0.3s;}
.file-input-label:hover{border-color:#00c6ff;color:#fff;}
textarea{width:100%;padding:14px;background:#1f1f1f;border:2px solid #333;border-radius:10px;color:#e0e0e0;resize:vertical;min-height:100px;}
textarea:focus{border-color:#00c6ff;outline:none;}
.btn{width:100%;padding:14px;background:linear-gradient(90deg,#00c6ff,#0072ff);color:white;border:none;border-radius:10px;cursor:pointer;font-size:1.1rem;transition:0.3s;}
.btn:hover{transform:translateY(-2px);box-shadow:0 5px 15px rgba(0,198,255,0.4);}
.result{margin-top:15px;padding:12px;border-radius:10px;display:none;}
.result.success{background:rgba(0,255,128,0.1);border:1px solid #00ff80;color:#00ffb0;}
.result.error{background:rgba(255,0,64,0.1);border:1px solid #ff0040;color:#ff5577;}
.download-btn{margin-top:10px;background:linear-gradient(90deg,#ff6a00,#ee0979);}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1>🔒 Steganography Tool</h1><p>Hide and extract secret messages</p></div>
<div class="mode-selector">
<button class="mode-btn active" onclick="switchMode('encode')">📝 Encode</button>
<button class="mode-btn" onclick="switchMode('decode')">🔍 Decode</button>
</div>
<div id="encode-section" class="section active">
<form id="encode-form" enctype="multipart/form-data">
<label>Choose Image:</label>
<input type="file" id="encode-image" accept="image/*" required hidden>
<label for="encode-image" class="file-input-label">📁 Click to select image</label>
<label>Secret Message:</label>
<textarea id="encode-message" placeholder="Enter secret message..."></textarea>
<button type="submit" class="btn">🔐 Encode</button>
</form>
<div id="encode-result" class="result"></div>
</div>
<div id="decode-section" class="section">
<form id="decode-form" enctype="multipart/form-data">
<label>Choose Encoded Image:</label>
<input type="file" id="decode-image" accept="image/*" required hidden>
<label for="decode-image" class="file-input-label">📁 Click to select encoded image</label>
<button type="submit" class="btn">🔍 Decode</button>
</form>
<div id="decode-result" class="result"></div>
</div>
</div>
<script>
function switchMode(mode){document.querySelectorAll('.mode-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));document.getElementById(mode+'-section').classList.add('active');}
document.getElementById('encode-form').addEventListener('submit',async e=>{
e.preventDefault();const f=new FormData();f.append('image',document.getElementById('encode-image').files[0]);f.append('message',document.getElementById('encode-message').value);
const r=await fetch('/encode',{method:'POST',body:f});const d=await r.json();const res=document.getElementById('encode-result');res.style.display='block';res.className='result '+(d.success?'success':'error');res.innerHTML=d.message;if(d.success){const b=document.createElement('button');b.className='btn download-btn';b.innerHTML='💾 Download';b.onclick=()=>downloadImage(d.image_data,'encoded.png');res.appendChild(b);}});
document.getElementById('decode-form').addEventListener('submit',async e=>{
e.preventDefault();const f=new FormData();f.append('image',document.getElementById('decode-image').files[0]);const r=await fetch('/decode',{method:'POST',body:f});const d=await r.json();const res=document.getElementById('decode-result');res.style.display='block';res.className='result '+(d.success?'success':'error');res.innerHTML=d.success?'Decoded: '+d.decoded_message:d.message;});
function downloadImage(data,name){const a=document.createElement('a');a.href='data:image/png;base64,'+data;a.download=name;a.click();}
</script>
</body>
</html>"""

            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            app.run(host="0.0.0.0", port=5000, debug=False)
            break
        else:
            print("Invalid choice. Enter 1 or 2.")


if __name__ == "__main__":
    try:
        import flask, numpy, PIL
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Install with: pip install flask pillow numpy")
        sys.exit(1)
    main()

# Image Steganography Tool
# Hide and extract secret messages in images using LSB (Least Significant Bit) technique

import os
import sys
from PIL import Image
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
import io
import base64
import argparse

class Steganography:
    @staticmethod
    def encode_message(image_path, message, output_path):
        """Hide a message inside an image using LSB steganography"""
        try:
            # Check file extensions and warn about JPEG
            input_ext = os.path.splitext(image_path)[1].lower()
            output_ext = os.path.splitext(output_path)[1].lower()
            
            if output_ext in ['.jpg', '.jpeg']:
                print("⚠️  WARNING: JPEG format uses lossy compression!")
                print("   Hidden messages may be corrupted. Use PNG for best results.")
                response = input("   Continue anyway? (y/N): ").strip().lower()
                if response != 'y':
                    return False, "Encoding cancelled. Please use PNG format."
            
            # Open the image
            img = Image.open(image_path)
            img = img.convert('RGB')  # Ensure RGB format
            img_array = np.array(img)
            
            # Add delimiter to mark end of message
            message += "<<<END>>>"
            
            # Convert message to binary
            binary_message = ''.join(format(ord(char), '08b') for char in message)
            
            # Check if image can hold the message
            max_capacity = img_array.size
            if len(binary_message) > max_capacity:
                raise ValueError("Message too long for this image")
            
            print(f"📊 Message: {len(message)-9} chars → {len(binary_message)} bits")
            print(f"📊 Image capacity: {max_capacity} bits")
            print(f"📊 Usage: {(len(binary_message)/max_capacity)*100:.1f}%")
            
            # Flatten the image array
            flat_img = img_array.flatten()
            
            # Hide message bits in LSBs
            for i in range(len(binary_message)):
                # Clear the LSB and set it to message bit
                flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])
            
            # Reshape back to original dimensions
            encoded_img_array = flat_img.reshape(img_array.shape)
            
            # Save the encoded image
            encoded_img = Image.fromarray(encoded_img_array.astype('uint8'))
            
            # Use PNG if output was JPEG to preserve data
            if output_ext in ['.jpg', '.jpeg']:
                output_path_png = output_path.rsplit('.', 1)[0] + '.png'
                encoded_img.save(output_path_png)
                print(f"💾 Saved as PNG to preserve data: {output_path_png}")
                return True, f"Message successfully hidden. Saved as {output_path_png} (PNG format for data integrity)"
            else:
                encoded_img.save(output_path)
                return True, "Message successfully hidden in image"
            
        except Exception as e:
            return False, f"Error encoding message: {str(e)}"
    
    @staticmethod
    def decode_message(image_path):
        """Extract hidden message from an image"""
        try:
            # Open the image
            img = Image.open(image_path)
            img = img.convert('RGB')
            img_array = np.array(img)
            
            print(f"🔍 Analyzing image: {img.size} pixels, Mode: {img.mode}")
            
            # Flatten the image array
            flat_img = img_array.flatten()
            
            # Extract LSBs to form binary message
            binary_message = ""
            for pixel in flat_img:
                binary_message += str(pixel & 1)
            
            print(f"📊 Extracted {len(binary_message)} bits from image")
            
            # Convert binary to text in chunks of 8 bits
            message = ""
            delimiter_search = ""
            
            for i in range(0, min(len(binary_message), 10000), 8):  # Limit search to first 10k bits
                byte = binary_message[i:i+8]
                if len(byte) == 8:
                    try:
                        char_code = int(byte, 2)
                        # Only add printable characters or common whitespace
                        if 32 <= char_code <= 126 or char_code in [9, 10, 13]:
                            char = chr(char_code)
                            message += char
                            delimiter_search += char
                            
                            # Keep only last 20 characters for delimiter search
                            if len(delimiter_search) > 20:
                                delimiter_search = delimiter_search[-20:]
                            
                            # Check for end delimiter
                            if "<<<END>>>" in delimiter_search:
                                end_pos = message.rfind("<<<END>>>")
                                if end_pos != -1:
                                    final_message = message[:end_pos]
                                    print(f"✅ Found delimiter at position {end_pos}")
                                    return True, final_message
                        else:
                            # Non-printable character found - might indicate no message
                            if len(message) < 10:  # If we haven't found much text yet
                                break
                    except ValueError:
                        continue
            
            # If we found some readable text but no delimiter
            if len(message) > 5 and any(c.isalpha() for c in message):
                print(f"⚠️  Found {len(message)} characters but no end delimiter")
                return False, f"Partial message found but corrupted: '{message[:50]}...'"
            
            print("❌ No readable text patterns found in LSBs")
            return False, "No hidden message found - this image may not contain steganography data"
            
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
        """Handle encoding in terminal mode"""
        print("\n--- ENCODE MESSAGE ---")
        
        # Get image path
        image_path = input("Enter path to input image: ").strip()
        if not os.path.exists(image_path):
            print("Error: Image file not found!")
            return
        
        # Get message
        message = input("Enter secret message: ").strip()
        if not message:
            print("Error: Message cannot be empty!")
            return
        
        # Get output path
        output_path = input("Enter output image path (with extension): ").strip()
        if not output_path:
            output_path = "encoded_image.png"
        
        # Encode message
        success, result = self.stego.encode_message(image_path, message, output_path)
        
        if success:
            print(f"✓ {result}")
            print(f"✓ Encoded image saved as: {output_path}")
        else:
            print(f"✗ {result}")
    
    def decode_terminal(self):
        """Handle decoding in terminal mode"""
        print("\n--- DECODE MESSAGE ---")
        
        # Get image path
        image_path = input("Enter path to encoded image: ").strip()
        if not os.path.exists(image_path):
            print("Error: Image file not found!")
            return
        
        # Decode message
        success, result = self.stego.decode_message(image_path)
        
        if success:
            print(f"✓ Hidden message found:")
            print(f"Message: {result}")
        else:
            print(f"✗ {result}")

# Flask Web Application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode_api():
    """API endpoint for encoding messages"""
    try:
        # Get uploaded file and message
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image uploaded'})
        
        file = request.files['image']
        message = request.form.get('message', '').strip()
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No image selected'})
        
        if not message:
            return jsonify({'success': False, 'message': 'Message cannot be empty'})
        
        # Save uploaded file temporarily
        temp_input = 'temp_input.png'
        temp_output = 'temp_output.png'
        file.save(temp_input)
        
        # Encode message
        stego = Steganography()
        success, result = stego.encode_message(temp_input, message, temp_output)
        
        if success:
            # Read the encoded image and convert to base64
            with open(temp_output, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Clean up temp files
            os.remove(temp_input)
            os.remove(temp_output)
            
            return jsonify({
                'success': True,
                'message': 'Message encoded successfully',
                'image_data': img_data
            })
        else:
            # Clean up temp files
            if os.path.exists(temp_input):
                os.remove(temp_input)
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            return jsonify({'success': False, 'message': result})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/decode', methods=['POST'])
def decode_api():
    """API endpoint for decoding messages"""
    try:
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image uploaded'})
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No image selected'})
        
        # Save uploaded file temporarily
        temp_input = 'temp_decode.png'
        file.save(temp_input)
        
        # Decode message
        stego = Steganography()
        success, result = stego.decode_message(temp_input)
        
        # Clean up temp file
        os.remove(temp_input)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Message decoded successfully',
                'decoded_message': result
            })
        else:
            return jsonify({'success': False, 'message': result})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

def main():
    """Main function to choose between terminal and GUI mode"""
    print("="*60)
    print("WELCOME TO IMAGE STEGANOGRAPHY TOOL")
    print("="*60)
    print("This tool allows you to hide secret messages inside images")
    print("and extract them back using LSB (Least Significant Bit) technique.")
    print("\nChoose your preferred mode:")
    print("1. Terminal Mode - Command line interface")
    print("2. GUI Mode - Web interface")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == '1':
            print("\nStarting Terminal Mode...")
            terminal = TerminalMode()
            terminal.run()
            break
        elif choice == '2':
            print("\nStarting GUI Mode...")
            print("Opening web interface at http://localhost:5000")
            print("Press Ctrl+C to stop the server")
            
            # Create templates directory if it doesn't exist
            os.makedirs('templates', exist_ok=True)
            
            # Create the HTML template
            html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Steganography Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .mode-selector {
            display: flex;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #e0e0e0;
        }
        
        .mode-btn {
            flex: 1;
            padding: 15px;
            background: #f5f5f5;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        
        .mode-btn.active {
            background: #4CAF50;
            color: white;
        }
        
        .mode-btn:hover:not(.active) {
            background: #e0e0e0;
        }
        
        .section {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .section.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .file-input {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        
        .file-input input[type=file] {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        .file-input-label {
            display: block;
            padding: 15px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-input-label:hover {
            background: #e9ecef;
            border-color: #4CAF50;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            min-height: 100px;
        }
        
        textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        .btn {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            margin-top: 10px;
        }
        
        .download-btn:hover {
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Steganography Tool</h1>
            <p>Hide and extract secret messages in images</p>
        </div>
        
        <div class="content">
            <div class="mode-selector">
                <button class="mode-btn active" onclick="switchMode('encode')">
                    📝 Encode Message
                </button>
                <button class="mode-btn" onclick="switchMode('decode')">
                    🔍 Decode Message
                </button>
            </div>
            
            <!-- Encode Section -->
            <div id="encode-section" class="section active">
                <form id="encode-form" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Select Image:</label>
                        <div class="file-input">
                            <input type="file" id="encode-image" accept="image/*" required>
                            <label for="encode-image" class="file-input-label">
                                📁 Click to select an image file
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Secret Message:</label>
                        <textarea id="encode-message" placeholder="Enter your secret message here..." required></textarea>
                    </div>
                    
                    <button type="submit" class="btn">🔐 Encode Message</button>
                </form>
                
                <div class="loading" id="encode-loading">
                    <div class="spinner"></div>
                    <p>Encoding message...</p>
                </div>
                
                <div id="encode-result" class="result"></div>
            </div>
            
            <!-- Decode Section -->
            <div id="decode-section" class="section">
                <form id="decode-form" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Select Encoded Image:</label>
                        <div class="file-input">
                            <input type="file" id="decode-image" accept="image/*" required>
                            <label for="decode-image" class="file-input-label">
                                📁 Click to select an encoded image
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">🔍 Extract Hidden Message</button>
                </form>
                
                <div class="loading" id="decode-loading">
                    <div class="spinner"></div>
                    <p>Decoding message...</p>
                </div>
                
                <div id="decode-result" class="result"></div>
            </div>
        </div>
    </div>

    <script>
        function switchMode(mode) {
            // Update buttons
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update sections
            document.querySelectorAll('.section').forEach(section => section.classList.remove('active'));
            document.getElementById(mode + '-section').classList.add('active');
            
            // Clear previous results
            document.getElementById('encode-result').style.display = 'none';
            document.getElementById('decode-result').style.display = 'none';
        }
        
        // Update file input labels
        document.getElementById('encode-image').addEventListener('change', function(e) {
            const label = document.querySelector('label[for="encode-image"]');
            label.textContent = e.target.files[0] ? '✅ ' + e.target.files[0].name : '📁 Click to select an image file';
        });
        
        document.getElementById('decode-image').addEventListener('change', function(e) {
            const label = document.querySelector('label[for="decode-image"]');
            label.textContent = e.target.files[0] ? '✅ ' + e.target.files[0].name : '📁 Click to select an encoded image';
        });
        
        // Handle encode form
        document.getElementById('encode-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loading = document.getElementById('encode-loading');
            const result = document.getElementById('encode-result');
            const formData = new FormData();
            
            const imageFile = document.getElementById('encode-image').files[0];
            const message = document.getElementById('encode-message').value;
            
            if (!imageFile || !message) {
                showResult('encode', false, 'Please select an image and enter a message');
                return;
            }
            
            formData.append('image', imageFile);
            formData.append('message', message);
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/encode', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                
                if (data.success) {
                    showResult('encode', true, data.message);
                    
                    // Create download button
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'btn download-btn';
                    downloadBtn.innerHTML = '💾 Download Encoded Image';
                    downloadBtn.onclick = function() {
                        downloadImage(data.image_data, 'encoded_image.png');
                    };
                    
                    result.appendChild(downloadBtn);
                } else {
                    showResult('encode', false, data.message);
                }
            } catch (error) {
                loading.style.display = 'none';
                showResult('encode', false, 'Network error: ' + error.message);
            }
        });
        
        // Handle decode form
        document.getElementById('decode-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loading = document.getElementById('decode-loading');
            const result = document.getElementById('decode-result');
            const formData = new FormData();
            
            const imageFile = document.getElementById('decode-image').files[0];
            
            if (!imageFile) {
                showResult('decode', false, 'Please select an encoded image');
                return;
            }
            
            formData.append('image', imageFile);
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/decode', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                
                if (data.success) {
                    showResult('decode', true, 'Hidden message found!');
                    
                    // Add decoded message
                    const messageDiv = document.createElement('div');
                    messageDiv.style.marginTop = '15px';
                    messageDiv.innerHTML = '<strong>Decoded Message:</strong><br><textarea readonly style="margin-top: 10px;">' + data.decoded_message + '</textarea>';
                    result.appendChild(messageDiv);
                } else {
                    showResult('decode', false, data.message);
                }
            } catch (error) {
                loading.style.display = 'none';
                showResult('decode', false, 'Network error: ' + error.message);
            }
        });
        
        // Handle convert form
        document.getElementById('convert-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loading = document.getElementById('convert-loading');
            const result = document.getElementById('convert-result');
            const formData = new FormData();
            
            const imageFile = document.getElementById('convert-image').files[0];
            
            if (!imageFile) {
                showResult('convert', false, 'Please select an image to convert');
                return;
            }
            
            // Check if already PNG
            if (imageFile.name.toLowerCase().endsWith('.png')) {
                showResult('convert', false, 'Image is already in PNG format');
                return;
            }
            
            formData.append('image', imageFile);
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                
                if (data.success) {
                    showResult('convert', true, data.message);
                    
                    // Create download button
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'btn download-btn';
                    downloadBtn.innerHTML = '💾 Download PNG Image';
                    downloadBtn.onclick = function() {
                        downloadImage(data.image_data, data.filename);
                    };
                    
                    result.appendChild(downloadBtn);
                } else {
                    showResult('convert', false, data.message);
                }
            } catch (error) {
                loading.style.display = 'none';
                showResult('convert', false, 'Network error: ' + error.message);
            }
        });
        
        function showResult(mode, success, message) {
            const result = document.getElementById(mode + '-result');
            result.className = 'result ' + (success ? 'success' : 'error');
            result.innerHTML = message;
            result.style.display = 'block';
        }
        
        function downloadImage(base64Data, filename) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + base64Data;
            link.download = filename;
            link.click();
        }
    </script>
</body>
</html>'''
            
            with open('templates/index.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            try:
                app.run(debug=False, host='0.0.0.0', port=5000)
            except KeyboardInterrupt:
                print("\nServer stopped.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import PIL
        import numpy
        import flask
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install Pillow numpy flask")
        sys.exit(1)
    
    main()
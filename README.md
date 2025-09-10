# 🔒 Image Steganography Tool

A Python-based project that lets you **hide secret messages inside images (encode)** and **reveal them back (decode)** using **LSB (Least Significant Bit) steganography**.  
The tool works in **two modes**:
- 🖥️ **Terminal Mode** – Simple CLI interface.  
- 🌐 **GUI Mode** – Modern web interface with **dark mode neon theme**.  

---

## ✨ Features

- 🔐 Hide secret messages inside images (PNG recommended).  
- 🔍 Extract hidden messages from encoded images.  
- 🖥️ Terminal interface for quick use.  
- 🌐 Web GUI with dark mode for easy interaction.  
- 💾 Download encoded images directly from the GUI.  
- ⚡ Lightweight – only requires **Python, Flask, Pillow, Numpy**.  

---

## 📂 Project Structure

```
stegano-tool/
│── main.py              # Main entry point
│── templates/
│    └── index.html      # Web GUI template (auto-generated if missing)
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation
│── samples/             # Example images (optional)
```

---

## ⚙️ Installation

1. **Clone this repository**  
   ```bash
   git clone https://github.com/Crepco/Steganography-
   cd Steganography-
   ```

2. **Create a virtual environment (recommended)**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

Run the tool:
```bash
python main.py
```

You’ll see a menu:
```
WELCOME TO IMAGE STEGANOGRAPHY TOOL
1. Terminal Mode
2. GUI Mode (Web)
```

### 🖥️ Terminal Mode
- **Encode** → Provide image path, secret message, and output filename.  
- **Decode** → Provide path to an encoded image to extract the hidden text.  

### 🌐 GUI Mode
- Opens at [http://localhost:5000](http://localhost:5000).  
- Upload an image and type your message → **Encode**.  
- Upload an encoded image → **Decode**.  
- Download encoded images directly.  

## ⚠️ Notes

- ✅ **Use PNG format** → safer for data integrity.  
- ⚠️ **JPEG images not recommended** → they use lossy compression and may corrupt hidden data.  
- 📏 Larger images = more capacity for hidden text.  

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Flask** – for GUI web server
- **Pillow (PIL)** – for image processing
- **NumPy** – for pixel manipulation
- **HTML, CSS, JS** – for frontend (dark mode UI)

---

## 🤝 Contributing

1. Fork the repo 🍴  
2. Create a new branch:  
   ```bash
   git checkout -b feature-new-idea
   ```
3. Commit your changes:  
   ```bash
   git commit -m "Added new feature"
   ```
4. Push and submit a PR 🚀  

---
---

from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)

# Đường dẫn lưu trữ audio
AUDIO_FOLDER = 'static/audio/'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

import os

# Path to the folder containing .onnx files
voices_folder = "voices"

# List to hold the voice dictionaries
voices = []

# Iterate through all files in the voices folder
for file in os.listdir(voices_folder):
    if file.endswith(".onnx"):  # Check if the file has a .onnx extension
        # Extract the name by removing the folder path and extension
        name = file.replace(".onnx", "").replace("_", "-")
        # Construct the dictionary for each voice
        voices.append({
            "name": name,
            "model": os.path.join(voices_folder, file)  # Full path to the .onnx file
        })

# Print the result
print("# Danh sách các giọng nói có sẵn")
print("voices =", voices)


@app.route('/')
def index():
    return render_template('index.html', voices=voices)

@app.route('/convert-text', methods=['POST'])
def convert_text():
    text = request.form['text']
    voice_choice = request.form['voice']
    
    # Kiểm tra nếu giọng chọn hợp lệ
    selected_voice = next((voice for voice in voices if voice['name'] == voice_choice), None)
    if not selected_voice:
        return jsonify({'error': 'Giọng không hợp lệ'}), 400

    model_path = selected_voice['model']
    audio_filename = f"{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)

    # Sử dụng Piper để chuyển văn bản thành giọng nói
    command = f"echo '{text}' | piper -m {model_path} --output_file {audio_path}"
    subprocess.run(command, shell=True)

    return jsonify({'audio_url': f'/static/audio/{audio_filename}'}), 200

@app.route('/upload-text', methods=['POST'])
def upload_text():
    uploaded_file = request.files['file']
    if uploaded_file.filename.endswith('.txt'):
        # Đọc nội dung file
        text = uploaded_file.read().decode('utf-8')
        return render_template('index.html', voices=voices, text=text)
    else:
        return jsonify({'error': 'File phải có định dạng .txt'}), 400

@app.route('/download-audio/<filename>', methods=['GET'])
def download_audio(filename):
    return send_file(os.path.join(AUDIO_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

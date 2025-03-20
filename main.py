from flask import Flask, request, jsonify
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_images'
GENERATED_VIDEOS = 'generated_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_VIDEOS, exist_ok=True)

@app.route('/generate-video', methods=['POST'])
def generate_video():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400

    image = request.files['image']
    prompt = request.form.get('prompt', '')

    if image.filename == '':
        return jsonify({'error': 'Nome de arquivo inválido'}), 400

    image_path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
    image.save(image_path)

    video_path = os.path.join(GENERATED_VIDEOS, f"{os.path.splitext(image.filename)[0]}.mp4")

    try:
        subprocess.run([
            "python", "-m", "inference.cli_demo",
            "--video_path", image_path,
            "--prompt", prompt,
            "--model_path", "NimVideo/cogvideox-2b-img2vid"
        ])
        return jsonify({'video_url': f"/videos/{os.path.basename(video_path)}"})
    except Exception as e:
        return jsonify({'error': f"Erro ao gerar vídeo: {str(e)}"}), 500

@app.route('/videos/<filename>', methods=['GET'])
def download_video(filename):
    return app.send_static_file(f'generated_videos/{filename}')

if __name__ == '__main__':
    app.run(debug=True, port=3000)

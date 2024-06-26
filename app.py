from flask import Flask, render_template, request, send_from_directory, redirect, url_for
# from moviepy.editor import VideoFileClip
from PIL import Image
# from pdf2image import convert_from_path
# from docx import Document
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'docx'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS).union(ALLOWED_DOC_EXTENSIONS)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image(input_path, output_path, output_format):
    with Image.open(input_path) as img:
        img.save(output_path, output_format.upper())

# def convert_video(input_path, output_path):
#     clip = VideoFileClip(input_path)
#     clip.write_videofile(output_path, codec='libx264')

# def convert_pdf_to_images(input_path, output_path):
#     pages = convert_from_path(input_path, 300)
#     for i, page in enumerate(pages):
#         page.save(f"{output_path}_page_{i+1}.png", 'PNG')

# def convert_docx_to_pdf(input_path, output_path):
#     document = Document(input_path)
#     document.save(output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Determine allowed output formats based on uploaded file type
            if input_path.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                allowed_output_formats = ALLOWED_IMAGE_EXTENSIONS
            elif input_path.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS:
                allowed_output_formats = ALLOWED_VIDEO_EXTENSIONS
            elif input_path.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS:
                allowed_output_formats = ALLOWED_DOC_EXTENSIONS
            else:
                allowed_output_formats = []

            return render_template('index.html', allowed_output_formats=allowed_output_formats)
    
    # Render the initial form with no specific options
    return render_template('index.html', allowed_output_formats=None)

@app.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        filename = request.form.get('filename')
        output_format = request.form.get('output_format').lower()

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = os.path.splitext(filename)[0] + '.' + output_format
        output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)

        if input_path.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
            convert_image(input_path, output_path, output_format)
        # elif input_path.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS:
        #     convert_video(input_path, output_path)
        # elif input_path.rsplit('.', 1)[1].lower() == 'pdf':
        #     convert_pdf_to_images(input_path, output_path)
        # elif input_path.rsplit('.', 1)[1].lower() == 'docx':
        #     convert_docx_to_pdf(input_path, output_path)

        return redirect(url_for('download_file', filename=output_filename))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pdf_operations import (
    merge_pdfs, remove_pages, convert_pdf_to_docx, set_pdf_permissions, password_protect_pdf
)
from config import Config
import os
from flask import jsonify

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_uploaded_files():
    """Return a list of all PDF filenames in the upload folder."""
    return [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith('.pdf')]

@app.route('/')
def index():
    uploaded_files = get_uploaded_files()
    return render_template('index.html', uploaded_files=uploaded_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['pdf_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    flash(f'{filename} uploaded successfully!')
    return redirect(url_for('index'))

@app.route('/merge', methods=['POST'])
def merge():
    # Get list of files selected for merge (from checkboxes)
    selected_files = request.form.getlist('merge_files')
    if not selected_files or len(selected_files) < 2:
        flash('Select at least 2 PDF files to merge.')
        return redirect(url_for('index'))

    # Prepare full file paths
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in selected_files]
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], "merged.pdf")
    
    merge_pdfs(file_paths, output_filename)
    return send_file(output_filename, as_attachment=True)

@app.route('/convert', methods=['POST'])
def convert():
    # Get the selected file to convert
    file = request.form.get('pdf_to_convert')
    if not file:
        flash('Select a PDF to convert.')
        return redirect(url_for('index'))

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    output_filename = os.path.splitext(pdf_path)[0] + ".docx"
    
    convert_pdf_to_docx(pdf_path, output_filename)
    return send_file(output_filename, as_attachment=True)

@app.route('/remove_pages', methods=['POST'])
def remove():
    # Get the file and pages to remove
    file = request.form.get('pdf_to_edit')
    pages_str = request.form.get('pages_to_remove')
    if not file or not pages_str:
        flash('Select a file and specify pages to remove.')
        return redirect(url_for('index'))

    try:
        pages = [int(p.strip()) for p in pages_str.split(',')]
    except ValueError:
        flash('Pages must be a comma-separated list of numbers.')
        return redirect(url_for('index'))

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(file)[0]}_edited.pdf")
    
    remove_pages(pdf_path, pages, output_filename)
    return send_file(output_filename, as_attachment=True)

@app.route('/set_permissions', methods=['POST'])
def set_permissions():
    file = request.form.get('pdf_permissions')
    restrictions = request.form.getlist('permissions')  # These are the things to RESTRICT
    
    if not file:
        flash('Select a file to set permissions.')
        return redirect(url_for('index'))

    # Start with all permissions allowed
    permission_flags = ["/Print", "/Copy", "/Modify", "/Annotate"]
    
    # Remove permissions based on checkboxes (which represent restrictions)
    if 'no_print' in restrictions:
        permission_flags.remove("/Print")
    if 'no_copy' in restrictions:
        permission_flags.remove("/Copy")
    if 'no_modify' in restrictions:
        permission_flags.remove("/Modify")
    if 'no_annotate' in restrictions:
        permission_flags.remove("/Annotate")
    
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(file)[0]}_restricted.pdf")
    
    # Use our updated function with the permissions that are ALLOWED
    set_pdf_permissions(pdf_path, permission_flags, output_filename)
    
    # Send the newly created file to the user
    return send_file(output_filename, as_attachment=True)

@app.route('/password_protect', methods=['POST'])
def password_protect():
    file = request.form.get('pdf_to_protect')
    password = request.form.get('password')
    if not file or not password:
        flash('Select a file and enter a password.')
        return redirect(url_for('index'))

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(file)[0]}_protected.pdf")
    
    password_protect_pdf(pdf_path, password, output_filename)
    return send_file(output_filename, as_attachment=True)

@app.route('/delete_all_pdfs', methods=['POST'])
def delete_all_pdfs():
    upload_folder = app.config['UPLOAD_FOLDER']
    
    try:
        # Print debug information
        print(f"Attempting to delete PDFs from: {upload_folder}")
        deleted_count = 0
        
        # Check if directory exists
        if not os.path.exists(upload_folder):
            return jsonify({"error": "Upload folder does not exist"}), 500
            
        for filename in os.listdir(upload_folder):
            if filename.lower().endswith(('.pdf', '.docx')):  # Only delete PDF files
                file_path = os.path.join(upload_folder, filename)
                if os.path.isfile(file_path):
                    print(f"Deleting: {file_path}")
                    os.remove(file_path)
                    deleted_count += 1
        
        print(f"Successfully deleted {deleted_count} PDF files")
        return jsonify({"message": f"All PDFs deleted successfully! ({deleted_count} files)"}), 200
    except Exception as e:
        print(f"Error deleting PDFs: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
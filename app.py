from flask import Flask, render_template, request, session, redirect, url_for
import os
from werkzeug.utils import secure_filename
import zipfile
import shutil
from chat_parser import parse_chat_file
from analyzer import analyze_directory

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXTRACTED_CONTENT_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_content')

# Ensure base directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXTRACTED_CONTENT_FOLDER'], exist_ok=True)

def get_extracted_files_info(extraction_path):
    files_info = []
    audio_extensions = ['.mp3', '.ogg', '.wav', '.m4a', '.aac', '.opus']
    if not os.path.exists(extraction_path):
        return files_info

    for item_name in os.listdir(extraction_path):
        item_path = os.path.join(extraction_path, item_name)
        if os.path.isfile(item_path):
            _, ext = os.path.splitext(item_name)
            file_type = ext.lower() if ext else 'unknown'
            is_audio = ext.lower() in audio_extensions
            files_info.append({
                'name': item_name,
                'type': file_type,
                'is_audio': is_audio
            })
    return files_info

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # **Cleanup for previous session's extracted data**
        previous_extraction_path = session.get('extraction_path')
        if previous_extraction_path and os.path.exists(previous_extraction_path):
            try:
                shutil.rmtree(previous_extraction_path)
                # print(f"Cleaned up old extraction path: {previous_extraction_path}") # For debugging
            except OSError as e:
                # Log this error, but don't let it stop the current upload
                print(f"Error cleaning up old extraction path {previous_extraction_path}: {e}")

        # Clear session data related to a previous upload
        session.pop('extraction_path', None)
        session.pop('original_zip_filename', None)
        session.pop('parsed_messages', None)
        session.pop('chat_file_name', None)
        session.pop('extracted_files_details', None)
        session.pop('analysis_results', None)
        session.pop('info_message', None) # Clear previous messages
        session.pop('error_message', None)


        if 'zipfile' not in request.files:
            session['error_message'] = 'No file part in request'
            return redirect(url_for('upload_file'))

        file = request.files['zipfile']
        if file.filename == '':
            session['error_message'] = 'No file selected'
            return redirect(url_for('upload_file'))

        if file and file.filename.endswith('.zip'):
            filename = secure_filename(file.filename)
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(zip_path)
            except Exception as e:
                session['error_message'] = f"Error saving file: {str(e)}"
                if os.path.exists(zip_path): # Clean up if save failed mid-way
                    os.remove(zip_path)
                return redirect(url_for('upload_file'))

            base_filename_no_ext = filename[:-4] if filename.endswith('.zip') else filename
            # New extraction path for the current file
            current_extraction_path = os.path.join(app.config['EXTRACTED_CONTENT_FOLDER'], f"{base_filename_no_ext}_extracted")

            # This cleanup is for the *current* file if it was uploaded before.
            # The cleanup for *previous different* files is handled at the start of POST.
            if os.path.exists(current_extraction_path):
                shutil.rmtree(current_extraction_path)
            os.makedirs(current_extraction_path, exist_ok=True)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(current_extraction_path)

                # **Delete original ZIP file after successful extraction**
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                        # print(f"Successfully deleted uploaded ZIP: {zip_path}") # For debugging
                    except OSError as e:
                        # Log this error, but processing can continue as extraction was successful
                        print(f"Error deleting uploaded ZIP {zip_path}: {e}")

                session['extraction_path'] = current_extraction_path # Store the new path
                session['original_zip_filename'] = filename
                # Initialize session keys that will be populated
                session['parsed_messages'] = []
                session['chat_file_name'] = None

                extracted_files_list_names = os.listdir(current_extraction_path)
                chat_file_name_found = None
                chat_file_path = None
                possible_chat_files = ['_chat.txt', 'chat.txt', 'whatsapp chat.txt']

                for fname in extracted_files_list_names:
                    if fname.lower() in [cn.lower() for cn in possible_chat_files]:
                        chat_file_name_found = fname
                        chat_file_path = os.path.join(current_extraction_path, fname)
                        break

                if chat_file_path:
                    try:
                        parsed_messages = parse_chat_file(chat_file_path)
                        session['parsed_messages'] = parsed_messages
                        session['chat_file_name'] = chat_file_name_found
                        if not parsed_messages:
                            session['info_message'] = f"Found chat file: '{chat_file_name_found}', but no messages were parsed. It might be empty or in an unrecognized format."
                    except Exception as e:
                        session['error_message'] = f"Error parsing chat file '{chat_file_name_found}': {str(e)}"
                else:
                    session['info_message'] = f"Chat file (e.g., '_chat.txt') not found in ZIP. Displaying extracted files only."

                session['extracted_files_details'] = get_extracted_files_info(current_extraction_path)

                # **Perform intelligent analysis on the extracted folder**
                analysis_results = analyze_directory(current_extraction_path)
                session['analysis_results'] = analysis_results

                return redirect(url_for('display_results'))

            except zipfile.BadZipFile:
                if os.path.exists(current_extraction_path): shutil.rmtree(current_extraction_path)
                if os.path.exists(zip_path): os.remove(zip_path) # Also remove bad zip file
                session['error_message'] = 'Error: Invalid or corrupted ZIP file.'
                return redirect(url_for('upload_file'))
            except Exception as e: # Catch any other errors during extraction/parsing
                if os.path.exists(current_extraction_path): shutil.rmtree(current_extraction_path)
                if os.path.exists(zip_path): os.remove(zip_path) # Clean up original zip on general error
                session['error_message'] = f"An unexpected error occurred: {str(e)}"
                return redirect(url_for('upload_file'))
        else:
            session['error_message'] = 'Invalid file type. Please upload a .zip file.'
            return redirect(url_for('upload_file'))

    # For GET request
    error_message = session.pop('error_message', None)
    info_message = session.pop('info_message', None)
    # If a user navigates back to '/', we don't want old results page info persisting visually
    # if they didn't re-upload, but session data for results page should remain until new POST.
    return render_template('index.html', error_message=error_message, info_message=info_message)

@app.route('/results')
def display_results():
    extraction_path = session.get('extraction_path')
    original_zip_filename = session.get('original_zip_filename', 'N/A')
    parsed_messages = session.get('parsed_messages', [])
    chat_file_name = session.get('chat_file_name', None)
    extracted_files_details = session.get('extracted_files_details', [])
    analysis_results = session.get('analysis_results', None)

    error_message = session.pop('error_message', None)
    info_message = session.pop('info_message', None)

    if not extraction_path:
        session['error_message'] = "No data to display. Please upload a chat file first."
        return redirect(url_for('upload_file'))

    return render_template('results.html',
                           original_zip_filename=original_zip_filename,
                           parsed_messages=parsed_messages,
                           chat_file_name=chat_file_name,
                           extracted_files_details=extracted_files_details,
                           analysis_results=analysis_results,
                           error_message=error_message,
                           info_message=info_message)

if __name__ == '__main__':
    app.run(debug=True)

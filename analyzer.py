# analyzer.py
import os
import mimetypes

def get_file_type_and_language(filename):
    """
    Determines the file type and programming language based on the file extension.
    """
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        return 'unknown', None

    # Source Code
    if ext in ['.py', '.pyw']: return 'code', 'Python'
    if ext in ['.js']: return 'code', 'JavaScript'
    if ext in ['.html', '.htm']: return 'code', 'HTML'
    if ext in ['.css']: return 'code', 'CSS'
    if ext in ['.java']: return 'code', 'Java'
    if ext in ['.c', '.h']: return 'code', 'C/C++'
    if ext in ['.cpp', '.hpp']: return 'code', 'C++'
    if ext in ['.cs']: return 'code', 'C#'
    if ext in ['.go']: return 'code', 'Go'
    if ext in ['.rb']: return 'code', 'Ruby'
    if ext in ['.php']: return 'code', 'PHP'
    if ext in ['.swift']: return 'code', 'Swift'
    if ext in ['.kt', '.kts']: return 'code', 'Kotlin'
    if ext in ['.ts']: return 'code', 'TypeScript'
    if ext in ['.sh']: return 'code', 'Shell'
    if ext in ['.json', '.xml', '.yaml', '.yml', '.toml']: return 'config', None

    # Images
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']: return 'image', None
    # Audio
    if ext in ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac']: return 'audio', None
    # Video
    if ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']: return 'video', None
    # Documents
    if ext in ['.pdf']: return 'document', 'PDF'
    if ext in ['.doc', '.docx']: return 'document', 'Word'
    if ext in ['.xls', '.xlsx']: return 'document', 'Excel'
    if ext in ['.ppt', '.pptx']: return 'document', 'PowerPoint'
    # Archives
    if ext in ['.zip', '.rar', '.7z', '.tar', '.gz']: return 'archive', None
    # Text
    if ext in ['.txt', '.md', '.log']: return 'text', None

    # Fallback to mimetype
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith('text/'): return 'text', None
        if mime_type.startswith('image/'): return 'image', None
        if mime_type.startswith('audio/'): return 'audio', None
        if mime_type.startswith('video/'): return 'video', None
        if mime_type.startswith('application/json'): return 'config', None
        if 'zip' in mime_type: return 'archive', None

    return 'other', None

def analyze_text_file(filepath):
    """
    Analyzes a text file and returns its line count and word count.
    Handles potential encoding errors.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            words = content.split()
            return len(lines), len(words)
    except (UnicodeDecodeError, IOError):
        # Could not read as text, so return 0 counts
        return 0, 0

def analyze_directory(directory_path):
    """
    Analyzes a directory and returns a detailed summary of its contents.
    """
    if not os.path.isdir(directory_path):
        return {"error": "The provided path is not a valid directory."}

    analysis = {
        'summary': {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'file_types': {},
            'languages': {}
        },
        'files': [],
        'directories': []
    }

    for root, dirs, files in os.walk(directory_path):
        # Update directory count (only for subdirectories)
        if root != directory_path:
            rel_path = os.path.relpath(root, directory_path)
            analysis['directories'].append(rel_path)
            analysis['summary']['total_dirs'] += len(dirs)

        for name in files:
            filepath = os.path.join(root, name)
            rel_filepath = os.path.relpath(filepath, directory_path)

            try:
                size = os.path.getsize(filepath)
                file_type, language = get_file_type_and_language(name)

                # Update summary
                analysis['summary']['total_files'] += 1
                analysis['summary']['total_size'] += size
                analysis['summary']['file_types'][file_type] = analysis['summary']['file_types'].get(file_type, 0) + 1
                if language:
                    analysis['summary']['languages'][language] = analysis['summary']['languages'].get(language, 0) + 1

                # File details
                file_info = {
                    'name': rel_filepath,
                    'size': size,
                    'type': file_type,
                    'language': language,
                }

                # If it's a text-based file, get more stats
                if file_type in ['text', 'code', 'config']:
                    line_count, word_count = analyze_text_file(filepath)
                    file_info['line_count'] = line_count
                    if file_type != 'code': # Word count is less relevant for code
                         file_info['word_count'] = word_count

                analysis['files'].append(file_info)

            except FileNotFoundError:
                # File might be a broken symlink, skip it
                continue

    # Correct total_dirs to be the count of directories found.
    analysis['summary']['total_dirs'] = len(analysis['directories'])

    return analysis

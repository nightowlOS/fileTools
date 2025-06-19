# Chat Log Viewer

## Project Purpose

This web application allows users to upload a ZIP file containing chat logs and other media. The application extracts the contents, parses a supported chat log file (such as WhatsApp chat exports), and displays the messages in a user-friendly format. It also lists all other files that were part of the uploaded ZIP archive.

## Features

-   **ZIP File Upload**: Accepts `.zip` files as input.
-   **Automatic Extraction**: Extracts the contents of the uploaded ZIP file into a temporary server location.
-   **Chat File Identification**: Automatically searches for common chat log filenames within the extracted files, such as:
    -   `_chat.txt`
    -   `chat.txt`
    -   `whatsapp chat.txt`
-   **Chat Parsing**: Parses the identified chat file to extract:
    -   Timestamp of each message
    -   Sender of the message
    -   Message content
-   **Message Display**: Shows the parsed chat messages on a results page.
-   **Extracted Files Listing**: Displays a list of all files and their types found within the ZIP archive, highlighting audio files.
-   **Timestamp Flexibility**: Supports various common date and time formats found in chat logs.
-   **Handles Special Messages**: Correctly processes multi-line messages and system-generated messages (e.g., "You created this group").
-   **Session Management**: Uses sessions to keep track of uploaded data for the user.
-   **Automatic Cleanup**: Deletes the uploaded ZIP file after successful extraction and cleans up extracted files from previous sessions or uploads to save server space.

## Project Structure

-   `app.py`: The main Flask application file. It handles routing, file uploads, ZIP extraction, session management, and interaction with the chat parser.
-   `chat_parser.py`: Contains the logic for parsing chat log files, using regular expressions to identify and extract message details.
-   `templates/`: Directory containing HTML templates for the application's web pages.
    -   `index.html`: The main page with the file upload form.
    -   `results.html`: The page that displays parsed chat messages and other extracted files.
-   `static/`: Directory for static files.
    -   `style.css`: Contains basic styling for the HTML pages.
-   `uploads/`: Default directory where uploaded ZIP files are temporarily stored (and then deleted after processing).
-   `uploads/extracted_content/`: Default directory where ZIP contents are extracted. Each ZIP gets its own subdirectory here.

## Setup and Running

1.  **Prerequisites**:
    *   Python 3.x
    *   pip (Python package installer)

2.  **Installation**:
    *   Clone this repository or download the source code.
    *   Navigate to the project directory in your terminal.
    *   It's recommended to create a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```
        (Note: `requirements.txt` will be created in a subsequent step. For now, you would need Flask: `pip install Flask`)

3.  **Running the Application**:
    *   Ensure you are in the project's root directory.
    *   Run the Flask application:
        ```bash
        python app.py
        ```
    *   The application will typically be available at `http://127.0.0.1:5000/` in your web browser.

## How It Works

1.  The user visits the homepage and uploads a `.zip` file.
2.  `app.py` receives the file, saves it to the `uploads/` directory.
3.  The application creates a unique directory within `uploads/extracted_content/` for the contents of this specific ZIP file.
4.  It then extracts all files from the ZIP into this unique directory.
5.  The original uploaded ZIP file is deleted from `uploads/` to save space.
6.  `app.py` searches for a chat file (e.g., `_chat.txt`) in the extracted contents.
7.  If found, `chat_parser.py` is invoked to parse the chat messages.
8.  The parsed messages and a list of all other extracted files are then displayed on the results page.
9.  If a user uploads a new ZIP file, the application first cleans up the extracted files associated with their previous upload before processing the new one.

## Known Limitations / Future Improvements

-   **Chat Format Support**: Currently tailored to a common WhatsApp chat export format. Other formats might not parse correctly.
    -   *Improvement*: Add parsers for other chat services (Telegram, Signal, etc.) or allow user to specify format.
-   **Error Handling**: Basic error handling is in place, but could be made more robust for edge cases in ZIP files or chat content.
-   **Scalability**: For very large chat files or many concurrent users, performance might degrade. This is a simple Flask development server setup.
    -   *Improvement*: Implement pagination for long chats and deploy with a production-grade WSGI server (e.g., Gunicorn).
-   **Security**: File uploads always carry some risk. While `secure_filename` is used, further security hardening might be needed for a public-facing application.
    -   *Improvement*: Add stricter file type validation post-extraction, resource limits, etc.
-   **No Database**: Chat data is processed in memory and stored in session. No persistent storage of chats.
    -   *Improvement*: Add a database to store and query chat history if needed for more advanced features.
-   **Frontend**: The UI is basic HTML and CSS.
    -   *Improvement*: Enhance the user interface with a modern JavaScript framework for better interactivity and presentation.
```

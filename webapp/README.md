# Codemeta Generator Web Application

A user-friendly web interface for generating and editing codemeta.json metadata files from GitHub repositories.

## Features

- **GitHub Repository Input**: Simply paste a GitHub repository URL
- **Real-time Terminal Output**: Watch the generation process in real-time
- **JSON Viewer**: View the generated codemeta.json with syntax highlighting
- **Metadata Editor**: Edit and correct metadata values through an intuitive form
- **Export Functionality**: Download the generated or edited codemeta.json file

## Installation

1. Ensure you have Python 3.8+ installed
2. Install Flask:
   ```bash
   pip install flask
   ```

3. Navigate to the webapp directory:
   ```bash
   cd webapp
   ```

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Enter a GitHub repository URL (e.g., `https://github.com/owner/repository`)
3. Click "Generate Codemeta"
4. Watch the terminal output as the metadata is generated
5. Review the JSON result in the "JSON Result" tab
6. Edit any values in the "Edit Metadata" tab
7. Save your changes and download the final codemeta.json file

## Project Structure

```
webapp/
├── app.py                 # Flask application and API endpoints
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript logic
└── README.md             # This file
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/generate` - Generate codemeta from GitHub URL (Server-Sent Events)
- `POST /api/export` - Export edited codemeta JSON

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Streaming**: Server-Sent Events (SSE)
- **Design**: Clean, functional developer tool aesthetic

## Development

The application uses Server-Sent Events (SSE) to stream terminal output in real-time as the Python codemeta generator script executes. This provides immediate feedback to users during the generation process.

## License

This web application is part of the sshoc-nl-codemeta-generator project.

# PDB-Engine

A web-based interface for protein structure analysis using UniDesign. This project provides a FastAPI backend and an Astro + React frontend to execute molecular structure processing commands.

## Prerequisites

- **Python 3.14+**
- **Node.js 24+**
- **UniDesign Binary** - For installation instructions, visit: [https://github.com/tommyhuangthu/UniDesign](https://github.com/tommyhuangthu/UniDesign)

## Project Structure

```
PDB-Engine/
├── API/                    # FastAPI Backend
│   ├── core/              # Core configuration and commands
│   ├── errors/            # Exception handling
│   ├── models/            # Pydantic models
│   ├── router/            # API endpoints
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
│
└── UI/                     # Astro + React Frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── data/          # Configuration and option files
    │   ├── hooks/         # Custom React hooks
    │   ├── layouts/       # Astro layouts
    │   ├── pages/         # Application pages
    │   ├── services/      # API client services
    │   ├── styles/        # Global styles and CSS
    │   ├── types/         # TypeScript type definitions
    │   └── utils/         # Utility functions
    ├── public/            # Static assets
    └── package.json       # Node dependencies
```

## Installation & Setup

### Backend (API)

1. Navigate to the API directory:
   ```bash
   cd API
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and set the path to your UniDesign binary:
   ```env
   PDBENGINE_BINARY_PATH=/path/to/UniDesign
   ```

6. Run the API server:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   
   API documentation (Swagger): `http://localhost:8000/docs`

### Frontend (UI)

1. Navigate to the UI directory:
   ```bash
   cd UI
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` if your API is running on a different URL:
   ```env
   PUBLIC_API_URL=http://localhost:8000
   ```

5. Run the development server:
   ```bash
   npm run dev
   ```

   The UI will be available at `http://localhost:4321`

## Usage

1. Start the API server (Backend)
2. Start the UI development server (Frontend)
3. Open your browser at `http://localhost:4321`
4. Upload PDB files and execute commands through the web interface

## Configuration

### API Configuration (`.env`)

Key configuration options:

- `PDBENGINE_BINARY_PATH`: Path to the UniDesign binary
- `PDBENGINE_TIMEOUT`: Maximum execution time in seconds (default: 600)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 104857600 - 100MB)
- `PORT`: API server port (default: 8000)
- `CORS_ORIGINS`: Allowed origins for CORS
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### UI Configuration (`.env`)

- `PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Building for Production

### Backend
The FastAPI application can be deployed using any ASGI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
Build the static assets:
```bash
cd UI
npm run build
```

Preview the production build:
```bash
npm run preview
```



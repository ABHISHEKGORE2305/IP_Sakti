import os
import uvicorn
from src.api import app

# Hugging Face Gradio SDK automatically runs `python app.py`.
# It expects a web server to start on port 7860.
if __name__ == "__main__":
    # Force the port to 7860 as required by Hugging Face
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

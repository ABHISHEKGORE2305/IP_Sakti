# FastAPI Backend — Docker & Hugging Face Deployment Plan

This plan walks you through containerizing your Python backend with Docker and deploying it to Hugging Face Spaces. By the end, your FastAPI server will be live on the internet, accessible via a public URL.

---

## Prerequisites

Before starting, make sure these one-time setup steps are done.

### PR-1: Ensure `.dockerignore` Exists
**What:** A `.dockerignore` file tells Docker which files to skip when building the container image.
**Where:** The `.dockerignore` file at the root of the repository.
**Why:** Without it, Docker would copy everything into the container — including your `.env` file (which contains your Gemini API Key), the 14 MB of raw PDF files that aren't used at runtime, the frontend folders, and the local Qdrant database. This makes the image bloated and insecure.
**How:** This has already been done. The `.dockerignore` now excludes `.env`, `data/raw/`, `frontend/`, `sih_frontend_antigrav/`, `qdrant_storage/`, `__pycache__/`, and documentation files.

### PR-2: Ensure Qdrant Cloud Migration is Complete
**What:** Your backend won't be useful if there's no data in the cloud database.
**Why:** The backend calls Qdrant to search for legal documents. If the cloud database is empty, every query will return zero results.
**How:** Complete all tasks in the Qdrant deployment plan first, especially Task 4 (Data Migration).

---

## Task 1: Create the Dockerfile

**What:** We are writing a "recipe" that tells Docker exactly how to build and run our backend server.
**Where:** A new file called `Dockerfile` (no file extension) at the root of the repository.
**Why:** Docker containers are like portable, self-contained computers. This Dockerfile instructs Docker to: install the right version of Python, install all your Python libraries, copy your code, and start the web server. Hugging Face Spaces reads this file to automatically build and deploy your backend.

### Subtask 1.1: Choose the Base Image
- The first line of the Dockerfile specifies which operating system and Python version to start from.
- Use `python:3.10-slim`. The `slim` variant is a lightweight version of Linux with Python 3.10 pre-installed. It keeps the image small (about 150 MB vs 900 MB for the full version).

### Subtask 1.2: Set the Working Directory
- Tell Docker that all subsequent commands should run inside a folder called `/app` inside the container.
- This is like telling Docker "create a folder called `/app` and `cd` into it."

### Subtask 1.3: Install Python Dependencies
- Copy `requirements.txt` into the container first (before copying the rest of the code).
- Run `pip install` with the `--no-cache-dir` flag. This flag tells pip not to save downloaded packages for future use, which saves about 200-500 MB of space in the image.
- **Why copy `requirements.txt` separately?** Docker caches each step. If your code changes but `requirements.txt` doesn't, Docker will skip the slow `pip install` step and reuse the cached version. This makes subsequent builds much faster.

### Subtask 1.4: Copy Your Source Code
- Copy the `src/` folder into the container. This contains all your Python backend code.
- Copy the `data/` folder into the container. Thanks to `.dockerignore`, only the `data/processed/` subfolder (containing `chunks.json`) will be copied. The raw PDFs are automatically excluded.

### Subtask 1.5: Set the Python Path
- Set the `PYTHONPATH` environment variable to `/app/src`.
- **Why:** Your Python files use `import config`, `import llm`, etc. without specifying the full path. Python needs to know where to look for these files. Setting `PYTHONPATH` to the `src` directory tells Python "look in this folder when importing modules."

### Subtask 1.6: Expose the Port
- Tell Docker that the container will listen on port **7860**.
- **Why 7860?** Hugging Face Spaces requires all web applications to serve traffic on this specific port. If you use any other port, Hugging Face won't be able to route traffic to your app.

### Subtask 1.7: Define the Startup Command
- The final line tells Docker what command to run when the container starts.
- It should run `uvicorn` (the web server), pointing it to your FastAPI application object, listening on host `0.0.0.0` (meaning "accept connections from anywhere") and port `7860`.

---

## Task 2: Fix Backend Port Configuration

**What:** Make the API port configurable via environment variables.
**Where:** `src/config.py` and `src/api.py`.
**Why:** Right now, `config.py` hardcodes `API_PORT = 8000`. But Hugging Face needs port 7860. If someone starts the server using `python src/api.py` (which reads `API_PORT` from the config), it would start on the wrong port. Making this an environment variable avoids the mismatch.

### Subtask 2.1: Update `src/config.py`
- Make `API_PORT` read from an environment variable called `PORT`, falling back to `8000` as the default.
- This way, the Dockerfile can set `PORT=7860` and the code will respect it. On your local machine, it will still default to 8000.

---

## Task 3: Configure CORS (Cross-Origin Resource Sharing)

**What:** Update the backend to accept requests from your Vercel frontend.
**Where:** `src/config.py` and `src/api.py`.
**Why:** When your frontend (on `your-app.vercel.app`) tries to call your backend (on `your-space.hf.space`), the browser blocks it by default. This is a security feature called CORS. We need to explicitly tell the backend "it's okay to accept requests from this specific frontend URL."

### Subtask 3.1: Make CORS Origins Configurable
- In `src/config.py`, modify `CORS_ALLOW_ORIGINS` to read from an environment variable called `FRONTEND_URL`.
- If `FRONTEND_URL` is set, use it as the single allowed origin.
- If it's not set, fall back to `["*"]` (allow all origins) for local development convenience.

### Subtask 3.2: Verify the Middleware
- Open `src/api.py` and confirm that the `CORSMiddleware` on lines 86-90 reads from `config.CORS_ALLOW_ORIGINS`. It already does, so no change is needed here — just verify.

---

## Task 4: Handle the Legacy Frontend Folder

**What:** Decide what to do with the old `frontend/` folder.
**Where:** The `frontend/` directory at the root of the repository.
**Why:** Your project has two frontends:
1. `sih_frontend_antigrav/` — the modern React/Vite app (this is what we're deploying).
2. `frontend/` — an older, static HTML/JS frontend.

The legacy `frontend/app.js` and `frontend/landing.js` contain the same broken `API_BASE` origin-detection logic that was identified in the audit. Since this frontend is NOT being deployed, the simplest fix is to make sure it never gets into the Docker image.

### Subtask 4.1: Verify Docker Exclusion
- Confirm that `.dockerignore` contains `frontend/`. It does — the legacy frontend will not be copied into the container.

### Subtask 4.2: Verify Vite Plugin is Dev-Only
- Open `sih_frontend_antigrav/vite.config.js`. Lines 33-48 contain a `serve-legacy-frontend` plugin that serves files from `../frontend/` during local development. On Vercel, the `../frontend/` folder won't exist, so this plugin will silently do nothing. No changes are strictly necessary, but if you want to be clean, you can wrap it in a check that only activates during development mode.

---

## Task 5: Set Up the Hugging Face Space

**What:** We are creating a cloud environment on Hugging Face that will build and host our Docker container.
**Where:** The Hugging Face website.
**Why:** Hugging Face Spaces is the only free platform that offers enough RAM (16 GB) to load your large AI models (`BAAI/bge-m3` embedding model and `BAAI/bge-reranker-v2-m3` cross-encoder).

### Subtask 5.1: Create a Hugging Face Account
1. Go to **https://huggingface.co/** and click **"Sign Up"**.
2. Create an account using your email, Google, or GitHub.

### Subtask 5.2: Create a New Space
1. After logging in, click your profile picture in the top-right corner.
2. Click **"New Space"**.
3. Fill in the form:
   - **Space name:** Choose something descriptive, like `ip-sakti-backend`.
   - **License:** Choose any (e.g., MIT).
   - **Space SDK:** Select **"Docker"**. This is critical — do NOT select Gradio or Streamlit.
   - **Space hardware:** Select **"CPU basic (Free)"**. This gives you 16 GB of RAM.
   - **Visibility:** Choose "Public" (free tier requires public spaces).
4. Click **"Create Space"**.

### Subtask 5.3: Add Your Secrets
1. In your new Space, click the **"Settings"** tab at the top.
2. Scroll down to the **"Variables and secrets"** section.
3. Click **"New secret"** and add each of the following. Secrets are encrypted and never visible in logs or code:

| Secret Name | Value | Where It Comes From |
|-------------|-------|---------------------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Your `.env` file |
| `QDRANT_URL` | Your Qdrant Cloud cluster URL | Qdrant Cloud dashboard (Task 1.3 of the Qdrant plan) |
| `QDRANT_API_KEY` | Your Qdrant Cloud API key | Qdrant Cloud dashboard (Task 1.3 of the Qdrant plan) |
| `FRONTEND_URL` | Your Vercel URL (add after frontend is deployed) | Vercel dashboard (after completing the Frontend plan) |
| `PORT` | `7860` | Required by Hugging Face |

### Subtask 5.4: Upload Your Code
Hugging Face Spaces work like Git repositories. You push code to them.
1. In your Space page, click the **"Files"** tab. You'll see instructions for cloning the Space repository.
2. Clone the Space repo to your local machine using the provided Git URL.
3. Copy your project files into the cloned folder: the `Dockerfile`, `requirements.txt`, `src/` folder, and `data/` folder.
4. Commit and push the files.

---

## Task 6: Deploy and Verify

**What:** We are triggering the build and making sure everything starts correctly.
**Where:** The Hugging Face Spaces dashboard.
**Why:** The first build will take 10-15 minutes because Docker needs to download Python, install all your libraries (including PyTorch and Sentence Transformers), and then the app needs to download and load the AI models into memory.

### Subtask 6.1: Monitor the Build
1. After pushing your code, go to your Space page on Hugging Face.
2. Click on the **"Logs"** button (usually at the bottom or in a "Factory" tab).
3. Watch the build logs. You should see:
   - `pip install` running through your requirements.
   - The container being built successfully.
   - Then the app starting and printing messages like "Loading embedding model: BAAI/bge-m3" and "RAG system ready!"
4. If the build fails, the logs will show you exactly which step failed and why.

### Subtask 6.2: Test the Health Endpoint
1. Once the Space shows a green "Running" status, you'll see a URL at the top of the page (something like `https://your-username-ip-sakti-backend.hf.space`).
2. Open a new browser tab and go to: `https://your-username-ip-sakti-backend.hf.space/health`
3. You should see a JSON response containing `"status": "ok"` and `"rag_ready": true`. If `rag_ready` is `false`, it means the RAG pipeline failed to initialize — check the logs for error messages.

### Subtask 6.3: Save Your Backend URL
- Copy the Space URL. You will need it for the Frontend deployment plan (it goes into the `VITE_API_URL` environment variable).

---

## Important: Hugging Face Sleep Behavior

Free Hugging Face Spaces automatically go to sleep after approximately 48 hours of inactivity (no incoming requests). When asleep:
- The first request after sleeping will take **30-60 seconds** while the Space wakes up and reloads the AI models.
- All subsequent requests will be fast (< 5 seconds).

**How to prevent sleeping:** Use a free uptime monitoring service like **UptimeRobot** (https://uptimerobot.com/). Create a free account and set up a monitor that pings your `/health` endpoint every 30 minutes. This keeps the Space awake indefinitely.

---

## Troubleshooting

| Problem | Likely Cause | How to Fix |
|---------|-------------|------------|
| Build fails with "no space left on device" | Docker image is too large | Make sure `.dockerignore` is present and excludes `data/raw/`, `frontend/`, etc. |
| Build succeeds but app crashes immediately | Missing environment variable | Check that all secrets in Subtask 5.3 are correctly set |
| App starts but prints "GEMINI_API_KEY not found" | The secret name is misspelled | Go to Settings → Secrets and verify the exact name is `GEMINI_API_KEY` |
| App starts but "RAG initialization failed" | Qdrant Cloud connection issue | Verify `QDRANT_URL` and `QDRANT_API_KEY` secrets are correct |
| App works but frontend gets CORS errors | `FRONTEND_URL` secret not set | Add your Vercel URL as the `FRONTEND_URL` secret |
| App responds with empty results | Cloud database has no data | Complete Task 4 of the Qdrant plan (Data Migration) |

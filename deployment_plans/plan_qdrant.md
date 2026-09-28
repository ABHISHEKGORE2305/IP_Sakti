# Qdrant Vector Database — Cloud Migration Plan

This plan walks you through moving your vector database from a local instance to Qdrant Cloud. By the end, your backend will securely connect to a managed cloud database instead of relying on a local Qdrant server.

---

## Prerequisites

Before starting, make sure you have completed these one-time setup steps.

### PR-1: Secure Your Repository
**What:** Populate the root `.gitignore` file so secrets and junk files are never committed to GitHub.
**Where:** The `.gitignore` file at the root of the repository.
**Why:** Your root `.gitignore` was previously empty. Without it, your `.env` file (which contains your Gemini API Key) and the local `qdrant_storage/` folder could accidentally be pushed to a public GitHub repository, exposing your credentials to the world.
**How:** This has already been done — the `.gitignore` now excludes `.env`, `__pycache__/`, `qdrant_storage/`, `data/raw/`, and OS junk files like `.DS_Store`.

---

## Task 1: Create a Free Qdrant Cloud Account and Database

**What:** We are setting up a fully managed vector database in the cloud.
**Why:** Currently, Qdrant runs on your local machine. When we deploy the backend to the cloud, there won't be a local Qdrant instance available. Qdrant Cloud gives us a database that's accessible from anywhere on the internet.

### Subtask 1.1: Sign Up
1. Open your web browser and go to **https://cloud.qdrant.io/**.
2. Click "Sign Up" and create a free account. You can use your Google or GitHub account to sign up quickly.

### Subtask 1.2: Create a Cluster
1. After logging in, you'll see a dashboard. Click the **"Create Cluster"** button.
2. Select the **"Free"** tier. This gives you 1 GB of storage and 1 GB of RAM, which is more than enough for this project.
3. Choose a **region** closest to where your users will be (e.g., `us-east-1` for the US or `eu-west-1` for Europe).
4. Give your cluster a name (e.g., `ip-sakti-prod`).
5. Click **"Create"** and wait about 30 seconds for the cluster to spin up.

### Subtask 1.3: Get Your Connection Credentials
1. Once the cluster shows a green "Active" status, click on it.
2. You will see a **Cluster URL** that looks something like: `https://abc123-xyz.aws.cloud.qdrant.io:6333`. Copy this URL and save it somewhere safe (e.g., a notes app). You will need it later.
3. Click on **"API Keys"** (or a similar section). Click **"Create API Key"**.
4. Give the key a name like `backend-key`.
5. Copy the generated API key and save it alongside the Cluster URL. **You will not be able to see this key again after you leave this page**, so make sure you have it saved.

---

## Task 2: Update the Backend Configuration File

**What:** We are making the configuration file flexible so it can connect to either the local Qdrant (for development on your laptop) or the cloud Qdrant (for production).
**Where:** `src/config.py`
**Why:** Right now, `QDRANT_URL` on line 11 is hardcoded to `"http://localhost:6333"` and there is no variable for an API key at all. We need to:
- Make the URL read from an environment variable so we can change it without editing code.
- Add a brand new `QDRANT_API_KEY` variable.
- Keep the local fallback so your app still works on your laptop without any extra setup.

### Subtask 2.1: Add the `os` Import
- At the very top of `src/config.py`, add a line to import Python's `os` module. This module lets Python read environment variables from the system.

### Subtask 2.2: Make `QDRANT_URL` Dynamic
- Find the line that says `QDRANT_URL = "http://localhost:6333"`.
- Change it to read from an environment variable called `QDRANT_URL`, with the old localhost value as the fallback default. This means: if the environment variable is set (as it will be in the cloud), use it; otherwise, fall back to localhost (for local development).

### Subtask 2.3: Add a New `QDRANT_API_KEY` Variable
- Right below the `QDRANT_URL` line, add a new variable called `QDRANT_API_KEY`.
- Make it read from an environment variable called `QDRANT_API_KEY`, with a fallback default of `None`. Local Qdrant doesn't need a key, but Qdrant Cloud does.

---

## Task 3: Update ALL Qdrant Client Connections

**What:** We are updating every place in the code that creates a connection to Qdrant, so that it passes the API key.
**Why:** Even though we added the API key to the config file, the actual code that connects to Qdrant doesn't know about it yet. Without the key, Qdrant Cloud will reject the connection and your entire search pipeline will crash.

> **⚠️ This is the most commonly missed step.** There are THREE separate files that create Qdrant connections, not just one.

### Subtask 3.1: Update `src/qdrant_setup.py`
**Where:** Line 18-20, where `QdrantClient(url=QDRANT_URL)` is called.
**How:** Add the `api_key` parameter to the `QdrantClient` constructor, pulling it from the config.

### Subtask 3.2: Update `src/vector_store.py`
**Where:** Inside the `QdrantVectorStore.__init__` method (lines 15-27), where `QdrantClient(url=url)` is called.
**How:**
1. Add a new parameter `api_key` to the `__init__` method signature, defaulting to the config value.
2. Pass that `api_key` into the `QdrantClient` constructor.

### Subtask 3.3: Update `src/retriever.py`
**Where:** Inside the `AyurvedicRetriever.__init__` method (lines 9-17), where `QdrantClient(url=qdrant_url)` is called.
**How:**
1. Add a new parameter `api_key` to the `__init__` method signature, defaulting to the config value.
2. Pass that `api_key` into the `QdrantClient` constructor.

### Subtask 3.4: Fix the Hardcoded Error Message in `src/rag_pipeline.py`
**Where:** Line 81, which contains the string `"Qdrant is running on http://localhost:6333"`.
**Why:** This error message tells users to check localhost, which won't make sense once deployed to the cloud. It's a small detail but will confuse anyone debugging a production issue.
**How:** Change the message to something generic like `"the Qdrant vector database is reachable"`.

---

## Task 4: Migrate Your Data to the Cloud Database

**What:** We are uploading all your document embeddings from the local database into the new cloud database.
**Why:** The Qdrant Cloud cluster you just created is completely empty. It has the infrastructure ready, but none of your legal documents, chunks, or embeddings are in it. Without this step, your app will start up fine but return zero search results for every query.

### Subtask 4.1: Set Environment Variables Locally
Before running the migration, you need to temporarily tell your local machine to use the cloud database.
1. Open a terminal.
2. Set the environment variables:
   - On **Windows PowerShell**: Use `$env:QDRANT_URL = "your-cluster-url"` and `$env:QDRANT_API_KEY = "your-api-key"`.
   - On **Mac/Linux**: Use `export QDRANT_URL="your-cluster-url"` and `export QDRANT_API_KEY="your-api-key"`.

### Subtask 4.2: Run the Ingestion Script
1. From the repository root, run the ingestion pipeline. This is likely `python src/ingest.py` (with `PYTHONPATH=src`).
2. This script will read `data/processed/chunks.json`, generate embeddings using the `BAAI/bge-m3` model, and upload them to your new Qdrant Cloud cluster.
3. This process may take several minutes depending on your internet speed, as the 51 MB of chunks need to be embedded and uploaded.

### Subtask 4.3: Verify the Migration
1. Go back to the Qdrant Cloud dashboard.
2. Click on your cluster and then on the collection name (should be `medical_documents`).
3. Verify that the "Points count" is greater than zero. This confirms your embeddings were uploaded successfully.

---

## Task 5: Clean Up Local Artifacts

**What:** Remove the local Qdrant storage folder from your repo.
**Where:** The `qdrant_storage/` folder at the root of the repository.
**Why:** Now that all data lives in the cloud, this folder is dead weight. It's already excluded by the new `.gitignore`, but you can also delete it locally to free up disk space.

### Subtask 5.1: Delete the Folder
- Delete the `qdrant_storage/` folder from your local machine. It is no longer needed.

---

## Troubleshooting

| Problem | Likely Cause | How to Fix |
|---------|-------------|------------|
| `Connection refused` when starting the app | The `QDRANT_URL` environment variable is not set, so the code falls back to localhost | Double-check that your Hugging Face Space has the `QDRANT_URL` secret set correctly |
| `Unauthorized` or `403 Forbidden` | The `QDRANT_API_KEY` is missing or wrong | Regenerate the API key on Qdrant Cloud and update the secret |
| App starts but returns zero results | The cloud database is empty — data was never migrated | Run Task 4 (Data Migration) |
| `Collection not found` error | The collection name in `config.py` doesn't match what was created in the cloud | Run `src/qdrant_setup.py` with cloud credentials to auto-create the collection, then re-run ingestion |

# React/Vite Frontend — Vercel Deployment Plan

This plan walks you through configuring your React frontend to talk to the cloud backend and deploying it to Vercel. By the end, your frontend will be live on the internet with a public `.vercel.app` URL.

---

## Prerequisites

Before starting, make sure:
1. The **Backend deployment plan** is complete and your Hugging Face Space is live. You will need the Space URL.
2. Your code is pushed to a **GitHub repository** (Vercel pulls code from GitHub).

---

## Task 1: Set Up the Environment Variable for the Backend URL

**What:** We are creating a configuration file that tells the frontend where the backend lives.
**Where:** Inside the `sih_frontend_antigrav/` folder.
**Why:** Right now, your frontend code has logic that tries to automatically detect the backend URL based on the current page's address. This worked when the frontend and backend lived on the same server behind nginx, but in our new setup they are on completely different servers (Vercel and Hugging Face). We need to explicitly tell the frontend the backend's address.

### Subtask 1.1: Create the Environment File
1. Navigate to the `sih_frontend_antigrav/` folder.
2. Create a new file called `.env`.
3. Inside this file, add a single line defining the backend URL. The variable name **must** start with `VITE_` — this is a Vite requirement. Any variable without the `VITE_` prefix will be invisible to your React code for security reasons.
4. Set `VITE_API_URL` to your Hugging Face Space URL (e.g., `https://your-username-ip-sakti-backend.hf.space`).
5. **Do NOT include a trailing slash** at the end of the URL. Your code appends paths like `/api/agent` directly after it, so a trailing slash would result in a double slash (`//api/agent`), which may cause errors.

### Subtask 1.2: Verify `.gitignore` Excludes the `.env` File
- Open `sih_frontend_antigrav/.gitignore`.
- Confirm it contains the line `*.local`. Vite `.env` files with the `.local` suffix are automatically ignored.
- However, a plain `.env` file is **not** excluded by the current `.gitignore`. You have two options:
  - **Option A (Recommended):** Rename the file to `.env.local` instead of `.env`. Vite loads `.env.local` automatically and it's already in the `.gitignore`.
  - **Option B:** Add `.env` to the `sih_frontend_antigrav/.gitignore` file.

---

## Task 2: Fix the API Base URL Logic (Critical)

**What:** We are replacing the broken origin-detection logic with a clean environment variable lookup.
**Where:** `sih_frontend_antigrav/src/lib/api.js`, specifically lines 6-14.
**Why:** This is the most critical change in the entire frontend deployment. Here's what the current code does:

1. It checks `window.location.origin` (the URL of the current page).
2. If the page is **not** on localhost, it assumes the backend is at the same URL as the frontend.
3. If the page **is** on localhost, it falls back to `http://127.0.0.1:8000`.

**The problem:** When deployed to Vercel, the page URL will be `https://your-app.vercel.app`. The code will see that this is NOT localhost, and will assume the backend is also at `https://your-app.vercel.app`. But the backend is on Hugging Face, not Vercel! Every single API call will fail with a 404 error.

### Subtask 2.1: Locate the `API_BASE` Declaration
- Open `sih_frontend_antigrav/src/lib/api.js`.
- Find the `API_BASE` constant (lines 6-14). It's an immediately-invoked function expression (IIFE) with the `window.location.origin` logic.

### Subtask 2.2: Replace with Environment Variable
- Delete the entire IIFE (the arrow function and all the origin-detection logic).
- Replace it with a simple assignment that reads from `import.meta.env.VITE_API_URL`.
- Add a fallback to `'http://127.0.0.1:8000'` using the `||` operator, so local development still works without a `.env` file.
- The result should be a single, clean line instead of the current 9-line block.

### Subtask 2.3: Verify the Rest of the File
- Scroll through the rest of `api.js`. All the API functions (`postJson`, `checkHealth`, `runAgent`, `translateText`) use `${API_BASE}` to build their URLs. These don't need any changes — they will automatically use the new value.

---

## Task 3: Audit for Any Other Hardcoded URLs

**What:** We are searching the entire frontend codebase for any other places that might have hardcoded localhost references.
**Where:** All files inside `sih_frontend_antigrav/src/`.
**Why:** If even one component makes a direct fetch call to `localhost:8000` instead of using the shared `API_BASE` from `api.js`, that feature will silently break in production.

### Subtask 3.1: Search for Hardcoded Addresses
- Search the `sih_frontend_antigrav/src/` folder for strings like `localhost`, `127.0.0.1`, and `:8000`.
- Based on the codebase review, `api.js` is the only file that contains these. All other components correctly import and use the functions from `api.js`. But verify this yourself to be safe.

---

## Task 4: Push Your Code to GitHub

**What:** We are uploading the latest version of your code to GitHub so Vercel can access it.
**Where:** Your local terminal.
**Why:** Vercel deploys code by pulling it directly from your GitHub repository. Every time you push a new commit to GitHub, Vercel will automatically rebuild and redeploy your site (this is called "continuous deployment").

### Subtask 4.1: Stage Your Changes
1. Open a terminal at the root of your repository.
2. Stage the modified files. The key changes are:
   - `sih_frontend_antigrav/src/lib/api.js` (the fixed `API_BASE` logic).
   - `.gitignore` (the populated ignore rules).
   - `.dockerignore` (the Docker exclusions).
   - Any backend code changes from the other plans.
3. **Do NOT stage** the `.env` or `.env.local` file. It contains your backend URL and should not be in the repository (Vercel will inject it separately).

### Subtask 4.2: Commit and Push
1. Commit with a descriptive message (e.g., "Prepare for cloud deployment").
2. Push to your GitHub remote. If you haven't set up a GitHub remote yet:
   - Create a new repository on GitHub.
   - Follow GitHub's instructions to add the remote and push.

---

## Task 5: Deploy to Vercel

**What:** We are connecting Vercel to your GitHub repository and configuring it to build only the frontend.
**Where:** The Vercel website.
**Why:** Vercel is a free hosting platform that specializes in frontend apps. It will take your React code, run the Vite build process (which converts your JSX/React code into plain HTML, CSS, and JavaScript files), and serve those files on a global CDN (Content Delivery Network) — meaning your site loads fast no matter where in the world the user is.

### Subtask 5.1: Create a Vercel Account
1. Go to **https://vercel.com/**.
2. Click **"Sign Up"** and sign in with your **GitHub account**. This is the easiest option because it automatically connects Vercel to your GitHub repositories.

### Subtask 5.2: Import Your Repository
1. After logging in, click **"Add New..."** → **"Project"**.
2. You'll see a list of your GitHub repositories. Find your IP-Sakti repository and click **"Import"**.

### Subtask 5.3: Configure the Build Settings (Very Important)
This is where most first-time users make mistakes. Pay close attention:

1. **Root Directory:**
   - Click **"Edit"** next to Root Directory.
   - Type: `sih_frontend_antigrav`
   - **Why:** Your repository has Python backend code, data files, and other folders at the root. Vercel needs to know that only the `sih_frontend_antigrav` folder is the frontend. Without this, Vercel will try to build the entire repo and fail because it doesn't know how to handle Python files.

2. **Framework Preset:**
   - Vercel should auto-detect **"Vite"**. If it doesn't, select it manually from the dropdown.

3. **Build Command:**
   - Should be automatically set to `npm run build`. If not, type it in.

4. **Output Directory:**
   - Should be automatically set to `dist`. If not, type it in.
   - **Why:** When Vite builds your React app, it puts the final HTML/CSS/JS files into a folder called `dist`. Vercel needs to know this is where the deployable files are.

### Subtask 5.4: Add the Environment Variable
1. On the same configuration page, scroll down to the **"Environment Variables"** section.
2. Add a new variable:
   - **Key:** `VITE_API_URL`
   - **Value:** Your Hugging Face Space URL (e.g., `https://your-username-ip-sakti-backend.hf.space`)
3. **Why this matters:** When Vercel runs `npm run build`, Vite reads this environment variable and embeds it directly into your JavaScript code. This is how your production frontend knows to send requests to the Hugging Face backend instead of localhost.

### Subtask 5.5: Deploy
1. Click the **"Deploy"** button.
2. Vercel will:
   - Clone your GitHub repo.
   - Navigate to the `sih_frontend_antigrav` folder.
   - Run `npm install` to install all JavaScript dependencies.
   - Run `npm run build` to compile your React app.
   - Upload the built files to their global CDN.
3. This process takes about 1-2 minutes.

### Subtask 5.6: Verify the Deployment
1. Once the deployment is complete, Vercel will show you a URL (e.g., `https://ip-sakti.vercel.app`).
2. Open this URL in your browser. You should see your React app.
3. Open your browser's **Developer Tools** (press F12), go to the **Console** tab, and check for any red error messages. Common issues at this stage are CORS errors (means the backend's `FRONTEND_URL` needs to be updated).

### Subtask 5.7: Update the Backend's CORS Setting
1. Copy your new Vercel URL.
2. Go back to your Hugging Face Space settings.
3. Add or update the `FRONTEND_URL` secret with your Vercel URL.
4. Restart the Space (or wait for it to restart automatically).
5. This tells the backend "requests from this Vercel URL are allowed."

---

## Troubleshooting

| Problem | Likely Cause | How to Fix |
|---------|-------------|------------|
| Vercel build fails with "Cannot find module" | `node_modules` not installed | Make sure `package.json` exists in `sih_frontend_antigrav/` and the root directory is set correctly |
| Site loads but shows a blank white page | JavaScript error during rendering | Open Developer Tools (F12) → Console tab, and look for red error messages |
| API calls fail with "CORS error" in Console | Backend doesn't allow this frontend URL | Add your Vercel URL as `FRONTEND_URL` in the Hugging Face Space secrets |
| API calls fail with "Failed to fetch" or "Network error" | Backend URL is wrong or Space is asleep | Check that `VITE_API_URL` is correct in Vercel's environment variables. Visit the HF Space URL directly to wake it up |
| API calls go to `your-app.vercel.app` instead of HF | The old `API_BASE` logic was not replaced | Go back to Task 2 and make sure the origin-detection code was fully replaced |
| Site works locally but not on Vercel | `.env` file not committed (this is correct!) but Vercel doesn't have the variable | Add `VITE_API_URL` in Vercel's dashboard under Settings → Environment Variables |

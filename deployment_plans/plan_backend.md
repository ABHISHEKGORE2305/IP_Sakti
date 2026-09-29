# FastAPI Backend — AWS App Runner Deployment Plan

This plan walks you through containerizing your Python backend with Docker and deploying it to **AWS App Runner**. By the end, your FastAPI server will be live on the internet with a secure HTTPS URL, zero cold starts, and fully covered by your AWS credits.

---

## The Cost Estimate (Using your $100 Credits)
AWS App Runner is incredibly cost-efficient because it "pauses" your CPU when no one is using the app, but keeps your RAM warm so there are **no cold starts**.
* **Memory (8GB kept warm 24/7):** ~$40.00 / month
* **CPU (2 vCPUs charged only during active requests):** ~$1.00 / month
* **Total Estimate:** **~$41.00 / month**. 
Your $100 credits will easily keep this online for nearly **5 months**!

---

## Prerequisites

### PR-1: Ensure `.dockerignore` Exists
**What:** A `.dockerignore` file tells Docker which files to skip when building the container image.
**How:** This is already done. It excludes `.env` and large unused folders to keep your AWS uploads small.

### PR-2: Install AWS CLI
1. Ensure **Docker Desktop** is open and running on your Windows machine.
2. Download and install the **AWS CLI** for Windows from [aws.amazon.com/cli](https://aws.amazon.com/cli/).

---

## Task 1: Create the Dockerfile
*(This is already completed in your repository!)*

**What:** We wrote an optimized `Dockerfile` that tells AWS exactly how to build and run your backend server.
- It uses `python:3.10-slim` to keep the image small.
- It **pre-downloads your 3GB AI models** directly into the image (Stage 3). This guarantees that when AWS scales your app, it starts in seconds instead of minutes.
- It exposes port `7860` (which we will configure App Runner to listen to).

---

## Task 2: Configure AWS CLI

**What:** We need to link your computer to your AWS account so you can upload the Docker image.
1. Log into your AWS Console in the browser.
2. In the top-right corner, click your username -> **Security Credentials**.
3. Scroll down to **Access keys** and click **Create access key**. Save the Access Key ID and Secret Access Key.
4. Open your computer's terminal (PowerShell) and run:
   ```bash
   aws configure
   ```
5. Paste your Access Key ID, then your Secret Access Key.
6. For Default region name, type `us-east-1` (N. Virginia, matching your Qdrant cluster for low latency).
7. For Default output format, press Enter to leave it blank.

---

## Task 3: Create an Amazon ECR Repository

**What:** ECR (Elastic Container Registry) is a private storage locker on AWS for your Docker images.
1. In the AWS Console search bar, type **ECR** and click **Elastic Container Registry**.
2. Click **Create repository**.
3. Visibility settings: **Private**.
4. Repository name: `ip-sakti-backend`.
5. Scroll to the bottom and click **Create repository**.
6. Click on your newly created `ip-sakti-backend` repository. In the top right, click the **"View push commands"** button. Keep this popup open; you will copy-paste these commands in the next step.

---

## Task 4: Push Your Code to AWS

**What:** We are going to build the Docker image locally and upload it to your ECR locker.
1. Open your terminal and ensure you are in your project folder (`C:\Users\Lenovo\Desktop\IP-Sakti\IP_Sakti`).
2. Copy **Command 1** from the AWS "View push commands" popup and paste it into your terminal. (This logs Docker into AWS).
3. Build the image locally (this will take 5-10 minutes as it downloads your AI models):
   ```bash
   docker build -t ip-sakti-backend .
   ```
4. Copy **Command 3** from AWS to tag your image.
5. Copy **Command 4** from AWS to push your image. (This will take a few minutes to upload to the cloud).

---

## Task 5: Deploy to AWS App Runner

**What:** We will tell App Runner to take your uploaded image and turn it into a live web server.
1. In the AWS Console search bar, type **App Runner** and click it.
2. Click **Create an App Runner service**.
3. **Source:** Select **Container registry**, then **Amazon ECR**.
4. Click **Browse** and select the `ip-sakti-backend` image you just uploaded. 
5. **Deployment trigger:** Select **Manual**.
6. **ECR access role:** Select "Create new service role". Click **Next**.

### Subtask 5.1: Configure the Service
1. **Service name:** `ip-sakti-backend-api`
2. **Virtual CPU & memory:** Select **2 vCPU and 8 GB**. *(Crucial: This provides enough RAM for your massive PyTorch AI models so they don't crash!).*
3. **Auto-scaling:** Click "Custom auto-scaling configuration". Click "Add new". Set **Maximum concurrency** to 100, and **Maximum instances** to **1**. *(Crucial: This physically prevents AWS from cloning your server and doubling your bill if you get hit with heavy traffic).*
4. **Port:** Type `7860` (This matches our Dockerfile configuration).

### Subtask 5.2: Add Environment Variables
Scroll down to "Environment variables" and add the following keys. *(Do not skip these, or the app will crash!)*:
| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your Google Gemini API key from `.env` |
| `QDRANT_URL` | Your Qdrant Cloud URL |
| `QDRANT_API_KEY` | Your Qdrant Cloud API key |
| `FRONTEND_URL` | *(Leave blank for now, you will update this after deploying the Vercel frontend)* |

### Subtask 5.3: Launch!
1. Scroll to the bottom and click **Next**, review your settings, and click **Create and deploy**.
2. AWS will take about 5 minutes to provision the server and start your container.
3. Once the status turns green (**Running**), you will see a **Default domain** URL (e.g., `https://xyz123.us-east-1.awsapprunner.com`). 
4. Click it and add `/health` to the end of the URL to verify your backend is alive and the AI models loaded successfully!

---

## Task 6: Set Up an AWS Billing Alarm (Optional but Recommended)

**What:** We are telling AWS to email you if your account ever spends more than $30 of your credits.
**Why:** To guarantee you never accidentally get charged on your actual card if you forget to shut this down next month!

1. In the AWS Console search bar, type **Budgets** and click **AWS Budgets**.
2. Click **Create budget** -> **Use a template (simplified)** -> **Zero spend budget** (or create a custom one for $30).
3. Enter your email address and click **Create budget**.
4. You will now get an instant email alert if AWS ever tries to charge you beyond your free credits!

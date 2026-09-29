# FastAPI Backend — AWS ECS Deployment Plan

This plan walks you through containerizing your Python backend with Docker and deploying it to **AWS Elastic Container Service (ECS)**. By the end, your FastAPI server will be live on the internet with zero cold starts, and fully covered by your AWS credits.

---

## The Cost Estimate (Using your $100 Credits)
AWS ECS (Fargate) is highly cost-efficient because we are going to run a single, small container instance to prevent cold starts without breaking the bank.
* **Memory (8GB) & CPU (2 vCPUs) kept warm 24/7:** ~$30-40 / month
* **Total Estimate:** **~$40.00 / month**. 
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

## Task 5: Deploy to AWS ECS Express Mode

**What:** We will tell Amazon ECS to take your uploaded image and turn it into a live web server. (Note: Because App Runner was retired by AWS, ECS Express Mode is the modern replacement).
**CRITICAL:** Make sure your AWS Console region in the top right is set to **Europe (Stockholm)**, since that is where you pushed your image!

1. In the AWS Console search bar, type **ECS** and click **Elastic Container Service**.
2. Look for the button or banner for **ECS Express Mode** (or "Create Cluster").
3. Follow the UI prompts to deploy a web application. 

### Subtask 5.1: Key Configuration Settings
When filling out the ECS deployment form, you must ensure these specific settings are chosen:
* **Compute:** 2 vCPU and 8 GB RAM (Crucial to prevent PyTorch crashes).
* **Port:** 7860 (Matches your Dockerfile).
* **Auto-Scaling:** Set Maximum Instances to **1** (Crucial to prevent your bill from multiplying).

### Subtask 5.2: Add Environment Variables
You must add the following environment variables during setup so the container doesn't crash on startup:
| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your Google Gemini API key from `.env` |
| `QDRANT_URL` | Your Qdrant Cloud URL |
| `QDRANT_API_KEY` | Your Qdrant Cloud API key |
| `FRONTEND_URL` | *(Leave blank for now)* |

### Subtask 5.3: Launch!
1. Click Deploy/Create.
2. AWS will take about 5-10 minutes to provision the ECS Fargate server and start your container.
3. Once running, find the **URL** or **Public IP** provided by the service. 
4. Click it and add `/health` to the end of the URL to verify your backend is alive!

---

## Task 6: Set Up an AWS Billing Alarm (Optional but Recommended)

**What:** We are telling AWS to email you if your account ever spends more than $30 of your credits.
**Why:** To guarantee you never accidentally get charged on your actual card if you forget to shut this down next month!

1. In the AWS Console search bar, type **Budgets** and click **AWS Budgets**.
2. Click **Create budget** -> **Use a template (simplified)** -> **Zero spend budget** (or create a custom one for $30).
3. Enter your email address and click **Create budget**.
4. You will now get an instant email alert if AWS ever tries to charge you beyond your free credits!

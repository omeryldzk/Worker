

# Football API Worker

This project is a Flask application that fetches league information from a Cloud Run API and uploads it to Google Cloud Storage. The application is containerized using Docker and can be deployed to Google Cloud Run.

## Features

- Fetches league information from a Cloud Run API.
- Uploads league fixtures and standings to Google Cloud Storage.
- Can be triggered via an HTTP request.

## Prerequisites

- Python 3.11
- Google Cloud SDK
- Docker
- A Google Cloud project with billing enabled
- A service account with the necessary permissions

## Setup

### 1. Clone the repository

```sh
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Set up Google Cloud credentials

- Create a service account in your Google Cloud project.
- Download the service account key file (`service_account.json`).
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the service account key file.

### 4. Run the application locally

```sh
export GCP_SA_KEY='YOUR_SERVICE_ACCOUNT_JSON_CONTENT'
python cloud.py
```

### 5. Build and run the Docker container

```sh
docker build --build-arg GOOGLE_APPLICATION_CREDENTIALS="$(cat /path/to/service_account.json)" -t my-flask-app .
docker run -p 8080:8080 my-flask-app
```

## Deployment

### 1. Store your Google Cloud service account key as a secret in GitHub

- Go to your GitHub repository.
- Click on `Settings`.
- Click on `Secrets and variables` > `Actions`.
- Click on `New repository secret`.
- Add a new secret with the name `GCP_SA_KEY` and paste the contents of your `service_account.json` file.

### 2. Create a GitHub Actions workflow

Create a `.github/workflows/cloudrun.yml` file in your repository with the following content:

```yaml
name: Build || Push || Deploy Cloud

on:
  push:
    branches: [ "deploy" ]
    # Build and push image to Google Container Registry

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: us-central1
  SERVICE_NAME: worker-api

jobs:
  build:
    name: Build && Push && Deploy
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repo
        uses: actions/checkout@main

     # Step 2: Set up Python
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # Step 3: Install dependencies
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Step 5: Package the application
            # Step 5: Package the application
      - name: Package Application
        run: |
          mkdir -p build
          # Copy all files except the 'build' directory into 'build/'
          rsync -av --exclude build/ . build/

      # Step 6: Archive the artifact
      - name: Archive Production Artifact
        uses: actions/upload-artifact@v4
        with:
          name: flask-build
          path: build/
      
  deploy-gcr:
    name: Deploy to GCR
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repo
        uses: actions/checkout@main

      - name: Download Artifact
        uses: actions/download-artifact@main
        with:
          name: flask-build
          path: .

      - name: Setup GCloud Auth
        id: auth
        uses: google-github-actions/auth@v0.4.0
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      # Authenticate Docker to use Artifact Registry
      - name: Authenticate Docker to GCP Artifact Registry
        run: |
          gcloud auth configure-docker us-central1-docker.pkg.dev

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v0.2.1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      # Build and push image to Google Container Registry
      - name: Build & Push
        run: |-
          gcloud builds submit \
            --quiet \
            --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA"

      # Deploy image to Cloud Run
      - name: Deploy GCR
        run: |-
          gcloud run deploy "$SERVICE_NAME" \
            --quiet \
            --region "$REGION" \
            --image "gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA" \
            --platform "managed" \

```
### 3. Change your Default Google Cloud service account role
Roles = 
- Artifact Registry Writer
- Cloud Build Editor
- Cloud Run Admin
- Storage Admin
  
## Usage

### Trigger the worker

Send a POST request to the `/trigger-worker` endpoint to trigger the worker:

```sh
curl -X POST https://<cloudrunurl>.us-central1.run.app/trigger-worker
```
## Discussion
Dont forget to change default google cloud service account role.Beacuse the service account you provided only responsible for deploying the container default service account will build the project from the artifact registry

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Explanation

- **Setup**: Instructions for cloning the repository, installing dependencies, setting up Google Cloud credentials, and running the application locally.
- **Deployment**: Steps to store the service account key as a GitHub secret and create a GitHub Actions workflow for building, pushing, and deploying the Docker image to Google Cloud Run.
- **Usage**: Instructions for triggering the worker via an HTTP request.

Make sure to replace `your-username` and `your-repo` with your actual GitHub username and repository name. This `README.md` file provides an overview of the project, setup instructions, deployment steps, and usage information.

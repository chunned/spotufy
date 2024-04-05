# SpOTUfy  [![CI/CD Pipeline](https://github.com/Ontario-Tech-NITS/final-project-group-1/actions/workflows/pipeline.yml/badge.svg)](https://github.com/Ontario-Tech-NITS/final-project-group-1/actions/workflows/pipeline.yml)

SpOTUfy is an application for the purpose of providing greater value to the everyday Spotify user who wants to get more out of their experience. 

Public deployment available [here](https://spotufy.chunned.ca).

![](static/homepage.gif)

# Local Deployment
There are two options for deployment:
- Clone this branch (main), place the `.env` file we submitted to Canvas in the repository directory, install the required packages with Pip, then simply `python3 app.py`
- Alternatively, use the `docker-compose.yml` we submitted to Canvas. `docker compose up`

Deploying locally will simply involve running the Flask application, and uses the Flask server. The Docker image is meant to be the "production" deployment and uses Gunicorn as the web server, with Nginx added to proxy incoming connections.

Either way, visit `http://localhost:9191` to access the application.

# Self-Hosting
Self-hosting requires a Spotify account (no subscription required), a Genius.com account. The easiest way to self-host is by using our [docker-compose.yml](https://github.com/Ontario-Tech-NITS/final-project-group-1/blob/main/docker-compose.yml) and [nginx.conf](https://github.com/Ontario-Tech-NITS/final-project-group-1/blob/main/nginx.conf) files.

Put both files in the same directory and set the following values:
- nginx.conf: `server_name` on line 9
- docker-compose.yml: `environment` section starting on line 9
  - `CLIENT_ID` and `CLIENT_SECRET` are obtained from the Spotify Developer console (steps shown below)
  - `GENIUS_TOKEN` is obtained from Genius.com (steps below)
  - `SECRET_KEY` can be generated by running `python` or `python3` (depending on your system) like so: `python -c "import os; print(os.urandom(12).hex())"`
  - `CALLBACK_URL` should be set to `https://your.domain/callback`
  
## Obtaining Spotify Client ID & Secret
- Sign into [Spotify for Developers](https://developer.spotify.com/dashboard)
- On the dashboard, click `Create app`
- Choose an app name and fill the decription with anything. 
- Set the redirect URI to the same as `CALLBACK_URL`
- In the "Which API/SDKs are you planning to use?" section, select **Web API**
- Agree with the terms and press Save
- The app will now be created; click settings and you will be shown your client ID and secret.

## Obtaining Genius.com API token
Generating a Genius API access token is a similar process to Spotify but slightly less involved. Visit the [API Client management page](http://genius.com/api-clients), create a new API client, set the name and website to anything, then click **Generate Access Token**.

Disclaimer: if you intend to use the GitHub Actions workflow for a public deployment, be aware that the LyricsGenius library for the Genius API is [only functional locally](https://github.com/johnwmillr/LyricsGenius/issues/220).

# Features 
## Backlog
- Get artist new/upcoming releases
- On demand "Daily Mixes"
- Graph visualization of artist relations

## Available
- Search artist information
- Get list of artist's top tracks and optionally create playlist with those songs
- Search song details
- Get recommendations based on a song and optionally create playlist with those songs
- Get recommended songs based on your listening activity
- Get artists related to a given input artist
- Get song lyrics
- Search artist discography


# CI/CD Pipeline 
The pipeline used for this project can be found at [.github/workflows/pipeline.yml](.github/workflows/pipeline.yml). The pipeline contains three jobs: `test-code`, `publish-docker`, and `deploy` and is triggered on any pull request or push (except for the `docker` branch itself, more info below) and can also be manually dispatched. 

- `test-code` runs `test_unittests.py` on `main.py` using `pytest`. See `test_unittests.py` for more information on how each unit test works
- `publish-docker` builds and publishes a new Docker image to GitHub Container Registry through the below steps
  - Merges the `main` branch into the `docker` branch
    - This step is why the `docker` branch is excluded from triggering the workflow on push. Without that exclusion, a duplicate job would be run. Apart from being a waste, this can also cause issues with the deployment if both jobs are executing simultaneously. 
  - Logs into ghcr.io
  - Builds the new Docker image 
  - Pushes it to ghcr.io 
- `deploy-image` first installs the predefined SSH keys to the Ubuntu runner, then creates an SSH session to the VPS that hosts [the public deployment](https://spotufy.chunned.ca), pulls the newly created Docker image, and runs `docker compose up` to (re)start the application.

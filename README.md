# DeeJay.AI

This is a Flask based web application that combines Google's Generative AI, the YouTube Data API, and the Spotify API to create uniquely customized playlists for any occasion. Just as one would prompt any GPT model, the user can specify a name and description for the desired playlist. For example, "Give me a playlist for a sunny day", or "Make me a playlist that feels like jogging in New York with some light rain". Essentially, the user can ask for a playlist based on mood, color, imagery, etc.; anything the user can imagine. 

Current Deployment Options:

[Test Link](https://djai-411603.uc.r.appspot.com/)

*For testing and viewing purposes, the above link is a working development version hosted on Google App Engine that has not been pushed to production. A playlist response can be generated by the GenAI but the respective APIs cannot be accessed to create the playlist. 

Deploying to a local server:
1. Clone the repository
2. Download the required packages: `pip install --user --requirement requirements.txt`
3. Make sure the redirect uris for your respective Google Cloud and Spotify Developers projects match with those in the config.json and main.py files. 
4. Start the web app by running the main.py python script. 

Deploying to Google Cloud Platform:
1. To deploy a new instance of the appliation:
    1. Deploy with `gcloud app deploy {path to project}`
    2. Delete old instance using Google Cloud console
1. To check out the latest deployment:
    1. Browse with `gcloud app browse`

    *Note: Other users must be added as testers to the Google Cloud project in order to use the YouTube Data API features. 

Deploying to Docker Container:
1. Clone the repository
2. Download Docker
3. Deploy to docker image and container
    1. Run `docker init` to setup config files
    2. Make sure Flask app is running in "0.0.0.0" to allow access from localhost
    3. Run `docker compose watch` (must have latest version of Docker to use compose watch) to deploy to a container
    4. Using `compose watch` will allow the user to make changes locally and have the container update and rebuild automatically
4. Run `docker compose down` to stop the application

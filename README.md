# DeeJay.AI

This is a Flask based web application that combines Google's Generative AI, the YouTube Data API, and the Spotify API to create uniquely customized playlsits for any occasion. Just as one would prompt any GPT model, the user can specify a name and description for the desired playlist. For example, "Give me a playlist for a sunny day", or "Make me a playlist that feels like jogging in New York with some light rain". Essentially, the user can ask for a playlist based on mood, color, imagery, etc.; anything the user can imagine. 

Current Deployment Options:

Deploying to a local server:
1. Clone the repository
2. Download the required packages: `pip install --user --requirement requirements.txt`
3. Make sure the redirect uris for your respective Google Cloud and Spotify Developers projects match with those in the config.json and main.py files. 
4. Start the web app by running the main.py python script. 

Deploying to Google Cloud Platform:
1. To deploy a new instance of the appliation:
    -i. Deploy with `gcloud app deploy {path to project}`
    -ii. Delete old instance using Google Cloud console
2. To check out the latest deployment:
    -i. Browse with `gcloud app browse`

    *Note: Other users must be added as testers to the Google Cloud project in order to use the YouTube Data API features. 
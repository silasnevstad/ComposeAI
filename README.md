# ComposeAI

This is a Flask app for an AI writing assistant that uses OpenAI's GPT-4 to provide suggestions and context-appropriate phrases for a human partner writing text. The app is deployed on Heroku, and it listens for HTTP GET requests on the '/buddy' endpoint. The app expects a 'text' query parameter with the human partner's input.

## Installation

To run the app locally, you'll need to have Python 3 and pip installed on your system. Clone the repository and navigate to the project directory in your terminal. Then, run the following commands to install the required dependencies:
```pip install -r requirements.txt```

You'll also need to set the OPENAI_API_KEY environment variable to your OpenAI API key. You can either set this variable in your system environment or create a .env file in the project directory with the following contents:
```OPENAI_API_KEY=<your_api_key_here>```


## Usage

To run the app locally, simply run the following command in your terminal:

```python app.py```
This will start a local server running the Flask app. You can then send a GET request to the /buddy endpoint with the text query parameter to get a response from the AI writing assistant.

To deploy the app on Heroku, you'll need to have a Heroku account and the Heroku CLI installed on your system. Follow these steps to deploy the app:


## Contributing

Contributions to this project are welcome! To get started, fork the repository and create a new branch for your changes. Then, submit a pull request with your changes.

This project is licensed under the MIT License. See the LICENSE file for details.

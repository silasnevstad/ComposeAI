# Buddy

This is an api for an AI writing assistant that leverages GPT-4 to provide auto complete suggestions, refinements, and context-appropriate phrases for a human partner writing text. It also features text manipulation endpoints and a simple ask endpoint. The app is deployed on Heroku, and it listens for HTTP POST requests on the '/v1/buddy' endpoint. The app expects a 'text' query parameter with the human partner's input.

## Usage

/v1/buddy
/v1/formalize
/v1/niceify
/v1/ask


Request body (required)
```
{
  "text": "string"
}
```

Response
```
{
  "response": "string",
}
```

## Installation

To run the app locally, you'll need to have Python 3 and pip installed on your system. Clone the repository and navigate to the project directory in your terminal. Then, run the following commands to install the required dependencies:
```
pip install -r requirements.txt
```

You'll also need to set the OPENAI_API_KEY environment variable to your OpenAI API key. You can either set this variable in your system environment or create a .env file in the project directory with the following contents:
```
OPENAI_API_KEY=<your_api_key_here>
```


## Contributing

Contributions to this project are welcome! To get started, fork the repository and create a new branch for your changes. Then, submit a pull request with your changes.

This project is licensed under the MIT License. See the LICENSE file for details.

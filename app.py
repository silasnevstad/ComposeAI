# AI Writing Assistant - @SilasNevstad
import openai
import requests
import tiktoken
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
encoding = tiktoken.get_encoding("cl100k_base")

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

preset_messages = [
    {"role": "system", "content": "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a the tone. Always aim to understand the user\'s intention. Try to match the human\'s tone so far and remember, your goal is to make writing easier by working together."},
    {"role": "system", "content": "In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. You can return anywhere from a single word to max a sentence. Note that you should only return the continuation you thought of, not any of the already written text."},
]

preset_message = "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a the tone. Always aim to understand the user's intention. Try to match the human's tone so far and remember, your goal is to make writing easier by working together. \n\n In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. Note that you should only return the continuation you thought of, not any of the already written text.\n\nNow, your partner is writing: \""

formalize_message = "Please formalize the following text.\n"

niceify_message = "Please make the following text sound and flow better, write it as well as you can.\n"

style_modes = {
    0: "Your style should be casual and laid-back.",
    1: "Your style should be friendly and approachable.",
    2: "",
    3: "Your style should be formal and professional",
    4: "Your style should be very formal and sophisticated."
}


def calculate_tokens(text):
    return len(encoding.encode(text))

def limit_tokens(text, limit):
    tokens = calculate_tokens(text)
    if tokens < limit:
        return text
    
    sentences = text.split(".")
    sentences.pop(0)
    text = ".".join(sentences)
    return limit_tokens(text, limit)

def prompt_gpt(prompt, model):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages = prompt)
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        if model == 'gpt-4':
            try:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages = prompt)
                return response.choices[0].message.content
            except openai.OpenAIError as e:
                print(e)
                return None
        else:
            print(e)
            return None
    
def ai_assist(text, style, user_prompt):
    style_prompt = style_modes.get(style, "")
    # prompt = "Now, your partner is writing: \"" + text + "\"\n\n" + style_prompt
    # if there is a user prompt (a prompt detailing what the writing is writing about), add it to the prompt
    if user_prompt:
        prompt = "Here is what your partner is writing about: \"" + user_prompt + "\"\n\n" + style_prompt + "\n\nNow, your partner is writing: \"" + text + "\"\n\n"
    else:
        prompt = style_prompt + "\n\nNow, your partner is writing: \"" + text + "\"\n\n"
    messages = preset_messages + [{"role": "system", "content": prompt}]
    response = prompt_gpt(messages, "gpt-4")
    return response

def gpt_from_preset_and_prompt_and_style(preset, text, style, user_prompt):
    style_prompt = style_modes.get(style, "")
    if user_prompt:
        user_prompt = "Here is what you are writing about: \"" + user_prompt + "\"\n\n"
    else:
        user_prompt = ""
    prompt = preset + user_prompt  + "Here is the text: \"" + text + "\"\n\n" + style_prompt + "\n\n"
    response = prompt_gpt([{"role": "system", "content": prompt}], "gpt-4")
    return response

def formalize_text(text, style, user_prompt):
    return gpt_from_preset_and_prompt_and_style(formalize_message, text, style, user_prompt)

def niceify_text(text, style, user_prompt):
    return gpt_from_preset_and_prompt_and_style(niceify_message, text, style, user_prompt)
    
@app.route('/v1/buddy', methods=['POST', 'OPTIONS'])
@cross_origin()
def writing_assistant():
    data = request.get_json()
    text = data.get('text')
    style = data.get('style', 2)  # default to balanced style if not provided
    user_prompt = data.get('prompt', None)
    
    if text == None:
        return jsonify({
            'error': 'No text provided'
        }), 400
        
    text = limit_tokens(text, (8192 - 190)) # 185 is the tokens from the preset message
        
    continuation = ai_assist(text, style, user_prompt)
    
    return jsonify({
        'suggestion': continuation
    }), 200

@app.route('/v1/formalize', methods=['POST', 'OPTIONS'])
@cross_origin()
def formalize():
    data = request.get_json()
    text = data.get('text')
    style = data.get('style', 2)  # default to balanced style if not provided
    user_prompt = data.get('prompt', None)
    
    if text == None:
        return jsonify({
            'error': 'No text provided'
        }), 400
        
        
    text = limit_tokens(text, (8192 - 190))
    
    formalized = formalize_text(text, style, user_prompt)
    
    return jsonify({
        'response': formalized
    }), 200

@app.route('/v1/niceify', methods=['POST', 'OPTIONS'])
@cross_origin()
def niceify():
    data = request.get_json()
    text = data.get('text')
    style = data.get('style', 2)  # default to balanced style if not provided
    user_prompt = data.get('prompt', None)
    
    if text == None:
        return jsonify({
            'error': 'No text provided'
        }), 400
        
        
    text = limit_tokens(text, (8192 - 190))
    
    niceified = niceify_text(text, style, user_prompt)
    
    return jsonify({
        'response': niceified
    }), 200
    
@app.route('/v1/ask', methods=['POST', 'OPTIONS'])
@cross_origin()
def auto():
    data = request.get_json()
    text = data.get('text')
    style = data.get('style', 2)  # default to balanced style if not provided
    
    if text == None:
        return jsonify({
            'error': 'No text provided'
        }), 400
    
    text = limit_tokens(text, (8192 - 190))
    style_prompt = style_modes.get(style, "")
    prompt = text + "\"\n\n" + style_prompt
    
    gpt_response = prompt_gpt([{"role": "system", "content": prompt}], "gpt-3.5-turbo")
    
    return jsonify({
        'response': gpt_response
    }), 200

if __name__ == '__main__':
    app.run(debug=True)

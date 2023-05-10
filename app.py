# AI Writing Assistant
# @SilasNevstad
import openai
import requests
import tiktoken
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
encoding = tiktoken.get_encoding("cl100k_base")

app = Flask(__name__)

preset_messages = [
    {"role": "system", "content": "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by suggesting ideas, completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a conversational tone. Always aim to understand the user\'s intention and provide relevant, helpful, and creative input. Try to match the human\'s tone so far and remember, your goal is to make writing easier by working together."},
    {"role": "system", "content": "In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. Note that you should only return the continuation you thought of, not any of the already written text."},
]

preset_message = "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by suggesting ideas, completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a conversational tone. Always aim to understand the user's intention and provide relevant, helpful, and creative input. Try to match the human's tone so far and remember, your goal is to make writing easier by working together. \n\n In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. Note that you should only return the continuation you thought of, not any of the already written text.\n\nNow, your partner is writing: \""

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
        return None
    
def ai_assist(text):
    prompt = "Now, your partner is writing: \"" + text + "\"\n\n"
    messages = preset_messages + [{"role": "system", "content": prompt}]
    response = prompt_gpt(messages, "gpt-4")
    
    return response
    
@app.route('/buddy', methods=['GET'])
def writing_assistant():
    text = request.args.get('text')
    
    if text == None:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
        
    text = limit_tokens(text, (8192 - 190)) # 185 is the tokens from the preset message
        
    continuation = ai_assist(text)
    
    return jsonify({
        'success': True,
        'response': continuation
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
# AI Writing Assistant - @SilasNevstad
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import openai
import requests
import tiktoken
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import uuid

load_dotenv()

class Source(BaseModel):
    title: str
    text: str

class Data(BaseModel):
    text: str
    prompt: str = None
    sources: Optional[List[Source]] = None

class WordData(BaseModel):
    word: str
    
# A Pydantic model to handle API key in headers
class TokenData(BaseModel):
    api_key: str = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
encoding = tiktoken.get_encoding("cl100k_base")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
VALID_API_KEYS = os.environ['VALID_API_KEYS'].split(',')

# app = Flask(__name__)
# CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

preset_messages = [
    {"role": "system", "content": "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a the tone. Always aim to understand the user\'s intention. Try to match the human\'s tone so far and remember, your goal is to make writing easier by working together."},
    {"role": "system", "content": "In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. You can return anywhere from a single word to max a sentence. Note that you should only return the continuation you thought of, not any of the already written text."},
]

preset_messages_v2 = [
    {"role": "system", "content": "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by improving their text, completing their sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a the tone. Always aim to understand the user\'s intention. Try to match the human\'s tone so far and remember, your goal is to make writing easier by working together."},
    {"role": "system", "content": "In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, first improve the entire text and then do your best to guess what the human wants to write and provide a suitable continuation. You can return anywhere from a single word to max a sentence. Note that you should return the entire improved text, so your suggestion plus what was given."},
]

preset_message = "You are Writing Assistant GPT-4. Your job is to collaborate with a human partner in writing text, making their experience more efficient. Assist them by completing sentences, and providing context-appropriate phrases. Be mindful of grammar and coherence while maintaining a the tone. Always aim to understand the user's intention. Try to match the human's tone so far and remember, your goal is to make writing easier by working together. \n\n In the next message, you will be given a part of the text the human is writing. It could be a sentence, a word, or even just a single letter. Based on that input, do your best to guess what the human wants to write and provide a suitable continuation. Note that you should only return the continuation you thought of, not any of the already written text.\n\nNow, your partner is writing: \""

formalize_message = "Please formalize the following text.\n"

niceify_message = "Please make the following text sound and flow better, write it as well as you can.\n"

BASE_GPT_MODEL = "gpt-4"
FAST_GPT_MODEL = "gpt-3.5-turbo"
BASE_TOKEN_LIMIT = 8192 # 8192 is the max tokens for the base model (gpt-4)
PROMPT_TOKEN_COUNT = 190 # 185 is the tokens from the preset message

# A function that checks if the API key is valid
def verify_api_key(api_key: str = Depends(oauth2_scheme)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

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

def prompt_gpt(messages, model):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages = messages)
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        if model == 'gpt-4':
            try:
                response = openai.ChatCompletion.create(
                    model=FAST_GPT_MODEL,
                    messages = messages)
                return response.choices[0].message.content
            except openai.OpenAIError as e:
                print(e)
                return None
        else:
            print(e)
            return None

def get_source_prompt(sources):
    source_prompt = ""
    if sources:
        source_prompt = "Here are some sources provided by the user (cite when necessary): " + "\n"
        for source in sources:
            source_prompt += source.title + " - " + source.text + "\n"
    return source_prompt

def ai_assist(text, user_prompt, sources):
    source_prompt = get_source_prompt(sources)
            
    if user_prompt:
        prompt = source_prompt + "Here is what your partner is writing about: \"" + user_prompt + "\"\n" + "\n\nNow, your partner is writing: \"" + text + "\"\n"
    else:
        prompt = source_prompt + "\nNow, your partner is writing: \"" + text + "\"\n"
    messages = preset_messages + [{"role": "system", "content": prompt}]
    response = prompt_gpt(messages, BASE_GPT_MODEL)
    return response

def ai_assist_v2(text, user_prompt, sources):
    source_prompt = get_source_prompt(sources)
            
    if user_prompt:
        prompt = source_prompt + "Here is what your partner is writing about: \"" + user_prompt + "\"\n" + "\n\nNow, your partner is writing: \"" + text + "\"\n"
    else:
        prompt = source_prompt + "\nNow, your partner is writing: \"" + text + "\"\n"
    messages = preset_messages_v2 + [{"role": "system", "content": prompt}]
    response = prompt_gpt(messages, BASE_GPT_MODEL)
    return response

def gpt_from_preset_and_prompt(preset, text, user_prompt, sources):
    source_prompt = get_source_prompt(sources)
    if user_prompt:
        user_prompt = source_prompt + "Here is what you are writing about: \"" + user_prompt + "\"\n\n"
    else:
        user_prompt = source_prompt
    prompt = preset + user_prompt  + "Here is the text: \"" + text + "\"\n\n"  + "\n\n"
    response = prompt_gpt([{"role": "system", "content": prompt}], BASE_GPT_MODEL)
    return response

def formalize_text(text, user_prompt, sources):
    return gpt_from_preset_and_prompt(formalize_message, text, user_prompt, sources)

def niceify_text(text, user_prompt, sources):
    return gpt_from_preset_and_prompt(niceify_message, text, user_prompt, sources)
    
@app.post("/v1/buddy")
async def writing_assistant(data: Data, api_key: str = Depends(verify_api_key)):
    text = data.text
    user_prompt = data.prompt
    sources = data.sources
    
    if text is None:
        raise HTTPException(status_code=400, detail="No text provided")
    
    # skip limiting tokens if text is short enough
    if len(text) > 1000:
        text = limit_tokens(text, (BASE_TOKEN_LIMIT - PROMPT_TOKEN_COUNT))
        
    continuation = ai_assist(text, user_prompt, sources)
    
    if continuation == None:
        raise HTTPException(status_code=400, detail="OpenAI API error")
    
    return {
        'suggestion': continuation
    }
    
@app.post("/v2/buddy")
async def writing_assistant(data: Data, api_key: str = Depends(verify_api_key)):
    text = data.text
    user_prompt = data.prompt
    sources = data.sources
    
    if text is None:
        raise HTTPException(status_code=400, detail="No text provided")
    
    # skip limiting tokens if text is short enough
    if len(text) > 1000:
        text = limit_tokens(text, (BASE_TOKEN_LIMIT - PROMPT_TOKEN_COUNT))
        
    continuation = ai_assist_v2(text, user_prompt, sources)
    
    if continuation == None:
        raise HTTPException(status_code=400, detail="OpenAI API error")
    
    return {
        'text': continuation
    }

@app.post("/v1/formalize")
async def formalize(data: Data, api_key: str = Depends(verify_api_key)):
    text = data.text
    user_prompt = data.prompt
    sources = data.sources
    
    if text is None:
        raise HTTPException(status_code=400, detail="No text provided")
        
    # skip limiting tokens if text is short enough
    if len(text) > 1000:
        text = limit_tokens(text, (BASE_TOKEN_LIMIT - PROMPT_TOKEN_COUNT))
         
    formalized = formalize_text(text, user_prompt, sources)
    
    if formalized == None:
        raise HTTPException(status_code=400, detail="OpenAI API error")
    
    return {
        'response': formalized
    }

@app.post("/v1/improve")
async def niceify(data: Data, api_key: str = Depends(verify_api_key)):
    text = data.text
    user_prompt = data.prompt
    sources = data.sources
    
    if text is None:
        raise HTTPException(status_code=400, detail="No text provided")
        
    # skip limiting tokens if text is short enough
    if len(text) > 1000:
        text = limit_tokens(text, (BASE_TOKEN_LIMIT - PROMPT_TOKEN_COUNT))
        
    niceified = niceify_text(text, user_prompt, sources)
    
    if niceified == None:
        raise HTTPException(status_code=400, detail="OpenAI API error")
    
    return {
        'response': niceified
    }
    
@app.post("/v1/ask")
async def auto(data: Data, api_key: str = Depends(verify_api_key)):
    text = data.text
    
    if text is None:
        raise HTTPException(status_code=400, detail="No text provided")
    
    # skip limiting tokens if text is short enough
    if len(text) > 1000:
        text = limit_tokens(text, (BASE_TOKEN_LIMIT - PROMPT_TOKEN_COUNT)) 
    
    prompt = text + "\"\n\n"
    
    gpt_response = prompt_gpt([{"role": "system", "content": prompt}], FAST_GPT_MODEL)
    
    if gpt_response == None:
        raise HTTPException(status_code=400, detail="OpenAI API error")
    
    return {
        'response': gpt_response
    }
    
@app.post("/v1/synonym")
async def synonym(data: WordData, api_key: str = Depends(verify_api_key)):
    word = data.word
    
    if word is None:
        raise HTTPException(status_code=400, detail="No word provided")
        
    if not word.isalpha(): # check if the word is only letters
        raise HTTPException(status_code=400, detail="Word must only contain letters")
    
    
    response = requests.get("https://api.datamuse.com/words?ml=" + word + "&syn&max=10")
    response = response.json()
    
    if len(response) == 0:
        raise HTTPException(status_code=400, detail="No synonyms found")
        
    # get the 10 most common synonyms
    response = sorted(response, key=lambda x: x['score'], reverse=True)[:10]
    
    # get the words from the response
    response = [x['word'] for x in response]
    
    return {
        'synonyms': response
    }

@app.post("/v1/create_api_key")
async def create_api_key(api_key: str = Depends(verify_api_key)):
    new_key = str(uuid.uuid4())
    VALID_API_KEYS.append(new_key)
    return {
        'api_key': new_key
    }

if __name__ == '__main__':
    app.run(debug=True)

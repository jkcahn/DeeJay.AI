
import google.generativeai as genai

class Genai:
    def __init__(self, GOOGLE_API_KEY):
        
        """GOOGLE GENAI"""

        genai.configure(api_key=GOOGLE_API_KEY)

        # Set up the model
        generation_config = {
        "temperature": 0.5,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        }

        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
        ]

        self.model = genai.GenerativeModel(model_name="gemini-pro",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)
    
    def playlist_request(self):
        prompt_parts = [
        "Can you make a playlist for reading a book on the couch on a rainy day? \
        Limit it to 2 songs and format it like this:\
        1. (Song title) - (Artist name) \
        2. (Song title) - (Artist name) \
        *",
        ]

        response = self.model.generate_content(prompt_parts)
        # print(response.text)

        # Formatting response
        response_list = response.text.strip().split('\n')
        songlist = []
        for string in response_list:
            if string:
                string = string[string.find(next(filter(str.isalpha, string))):]
                if '\"' in string:
                    string = string.replace('\"', '')
                songlist.append(string)
        
        return songlist

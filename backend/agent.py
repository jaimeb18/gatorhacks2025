from pathlib import Path
import google.generativeai as genai
import re

class Agent:
    # API Key, remove later
    google_api_key = "AIzaSyAdCvnxTFuXUCBLK3KX6rtzlyto1qaBA_U"

    # Gemini Model
    model_name = "gemini-2.5-flash"
    def __init__(self, media_type, name: str = ""):
        if media_type == "artwork":
            self.__artwork = name

            #Gathering files
            current_file = Path(__file__)
            current_directory = current_file.parent
            prompts = current_directory / "Prompts"
            self.__artworks_extracting_themes_prompt = (prompts / "Artworks_Get_Details_Prompt.txt").read_text(
                encoding="utf-8")

        # Configure the API key
        genai.configure(api_key=Agent.google_api_key)
        self.__model = genai.GenerativeModel('gemini-2.5-flash')

    def add_artwork_to_prompt(self):
        lines = self.__artworks_extracting_themes_prompt.splitlines()
        lines[1] += f" {self.__artwork}"
        self.__artworks_extracting_themes_prompt = "\n".join(lines)

    def get_details(self):
        response = self.__model.generate_content(self.__artworks_extracting_themes_prompt)
        return response.text

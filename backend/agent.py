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
            self.__artworks_extracting_themes_prompt = (prompts / "Artworks_Extracting_Themes_Prompt.txt").read_text(
                encoding="utf-8")
            self.__artworks_get_suggestions_prompt = (prompts/ "Artworks_Get_Suggestions_Prompt.txt").read_text(
                encoding="utf-8")
            self.__artworks_get_details_prompt = (prompts/"Artworks_Get_Details_Prompt.txt").read_text(
                encoding="utf-8")


        # Configure the API key
        genai.configure(api_key=Agent.google_api_key)
        self.__model = genai.GenerativeModel(Agent.model_name)

    def add_artwork_to_prompt(self):
        lines = self.__artworks_extracting_themes_prompt.splitlines()
        lines[1] += f" {self.__artwork}"
        self.__artworks_extracting_themes_prompt = "\n".join(lines)
        lines = self.__artworks_get_details_prompt.splitlines()
        lines[0] += f" {self.__artwork}"
        self.__artworks_get_details_prompt = "\n".join(lines)
        lines = self.__artworks_get_suggestions_prompt.splitlines()
        lines[0] = lines[0].replace("{artwork}", self.__artwork)
        self.__artworks_get_suggestions_prompt = "\n".join(lines)

    def get_themes(self):
        response = self.__model.generate_content(self.__artworks_extracting_themes_prompt)
        return response.text

    def get_details(self):
        response = self.__model.generate_content(self.__artworks_get_details_prompt)
        return response.text

    def suggestions(self):
        response = self.__model.generate_content(self.__artworks_get_suggestions_prompt)
        gemini_list = eval(re.sub(r'```python\n?|```\n?', '', response.text.strip()))
        suggestion_list = []
        for innerList in gemini_list:
            if type(innerList) is list:
                suggestion_list.append(
                    {"Name": innerList[0], "Artist": innerList[1], "Year": innerList[2],
                     "Current Location": innerList[3], "Wikipedia": innerList[4]
                     })
        return suggestion_list


    my_agent = Agent("artwork", "Mona Lisa")
    print(my_agent.artwork_suggestions())

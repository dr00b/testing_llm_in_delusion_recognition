"""
Create a class called Classifier.
In the init function, load environment variables and save them to self.
Read davinci_base_prompt.txt and save to self.base_prompt.
"""

import dotenv
import os
import openai
dotenv.load_dotenv()


class Classifier:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.sqlite_db_path = os.path.join("data", os.getenv('SQLITE_DB_NAME'))
        self.base_prompt = open('davinci_base_prompt.txt', 'r').read()

    def classify(self, text):
        """
        Use the OpenAI API davinci model to classify the text.
        """
        # TODO: consider top_p to see alternatives considered
        # TODO: tinker w/ frequency_penalty / precense penalty

        openai.api_key = self.api_key
        prompt = self.base_prompt.replace("{text}", text)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            n=1,
            temperature=0,
            top_p=1.0,
            max_tokens=400,
            frequency_penalty=-0.5,
            presence_penalty=-0.5,
        )
        return response.choices[0].text


if __name__ == "__main__":
    classifier = Classifier()
    print(classifier.classify(os.getenv("TEST_TEXT")))
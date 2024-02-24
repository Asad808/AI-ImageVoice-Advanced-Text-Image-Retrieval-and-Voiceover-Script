import os
from openai import OpenAI
import downloader, bing 
import warnings
import base64
import requests

warnings.filterwarnings("ignore") # Ignore warnings

class Image_to_speech:

    """
    This class provides functionality to process images based on user input, 
    describe them using OpenAI's API, and convert the descriptions to speech.
    """

    def __init__(self, user_input, api_key, image_output_dir):
        
        """
        Initializes the Image_to_speech class with user input, API key, and image output directory.
        
        Parameters:
        user_input (str): The user input to process.
        api_key (str): The API key for OpenAI.
        image_output_dir (str): Directory path to save output images.
        """
        
        self.user_input = user_input
        self.api_key = api_key
        self.image_output_dir = image_output_dir

    # Function to get response from OpenAI based on user input
    def get_openai_response(self, user_input):
        
        """
        Gets a response from OpenAI based on user input.

        Parameters:
        user_input (str): The user input to send to OpenAI.

        Returns:
        str: A string of keywords extracted from the OpenAI response.
        """

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You will be provided with a block of text, and your task is to extract a list of keywords from it."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.9,
            max_tokens=64,
            top_p=1
        )

        # Extracting and returning the message content from the response
        response_content =  response.choices[0].message.content
        # Split the string by commas, remove any leading/trailing whitespace, and then join them into a single string
        string = ' '.join([word.strip() for word in response_content.split(',')])
        return f"{string} scientific educational" 
        


    def image_retrieval(self, image_output_dir, keywords_string):
        
        """
        Retrieves and downloads images based on a string of keywords.

        Parameters:
        image_output_dir (str): The directory where images will be saved.
        keywords_string (str): The string of keywords to search for images.

        Returns:
        None: Images are downloaded to the specified directory.
        """

        if "sorry" in keywords_string.lower() or "apologize" in keywords_string.lower():
            print("I'm sorry but I need the block of text in order to extract the keywords. Please provide the text so I can assist you further.")
            return
        else:
            # Download images for each keyword
            urls = downloader.download(keywords_string, limit=5, output_dir=image_output_dir, verbose=True, filter="photo") # Download images based on the keywords
            for index, url in enumerate(urls):
                print(f"Image {index+1} is downloaded from: {url}")


    # Function to encode the image
    def encode_image(self, image_path):
        
        """
        Encodes an image to a base64 string.

        Parameters:
        image_path (str): Path to the image file.

        Returns:
        str: The base64 encoded string of the image.
        """

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8') # Return the base64 encoded string of the image

    def describe_image(self, image_path, user_input):
        
        """
        Sends an image to OpenAI's API and gets a description of the image.

        Parameters:
        image_path (str): Path to the image file.
        user_input (str): Additional user input to assist in image description.

        Returns:
        str: Description of the image as returned by OpenAI's API.
        """

        # Getting the base64 string
        base64_image = self.encode_image(image_path)

        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
        "model": "gpt-4-vision-preview",  # Make sure you have access to this model
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"What’s in this image? {user_input} "
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'] # Return the description of the image
        else:
            return f"Error: {response.status_code} - {response.json()}"
        
    def text_to_speech(self, text_input, image_path, output_dir):

        """
        Converts text input to speech and saves it as an audio file.

        Parameters:
        text_input (str): The text to convert to speech.
        image_path (str): Path to the associated image file.
        output_dir (str): Directory to save the output audio file.

        Returns:
        None: The audio file is saved to the specified directory.
        """

        # Get the basename (filename with extension)
        basename_with_extension = os.path.basename(image_path) # Get the basename of the image path
        # Split the basename and its extension, and return only the basename
        speech_file, _ = os.path.splitext(basename_with_extension) 
        speech_file_path = f"{output_dir}/{speech_file}.mp3"
        print(f"\nSpeech file path: {speech_file_path}")
        client = OpenAI(api_key=self.api_key) # Initialize the OpenAI client
        response = client.audio.speech.create(
            model = "tts-1",
            voice = "nova",
                input = text_input
                )
        response.stream_to_file(speech_file_path) # Save the audio file to the specified directory
 
    def process_images(self, user_input):
        
        """
        Processes images based on user input, describes them, and converts the descriptions to speech.

        Parameters:
        user_input (str): The user input to guide image processing.

        Returns:
        None: Processes images and generates speech files.
        """

        keywords_string = self.get_openai_response(user_input) # Get keywords from OpenAI based on user input
        output_dir = f"{self.image_output_dir}/{keywords_string}" # Create a new directory based on the keywords
        self.image_retrieval(self.image_output_dir, keywords_string) # Retrieve and download images based on keywords

        for filename in os.listdir(output_dir):
            if filename.lower().endswith(('.jpg', '.png')):
                image_path = os.path.join(output_dir, filename) # Get the path of the image
                description = self.describe_image(image_path, user_input) # Get the description of the image
                self.text_to_speech(description, image_path, output_dir) # Convert the description to speech
                print(f"\nDescription of {filename} is: {description} \n\n")

        print(f"Images are be searched on: '{keywords_string}' words. \n")


if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")

    image_output_dir = "C:/Users/SYSTEM/Desktop" # Replace with your desired directory path
    user_input = input("Enter the Specific Topic for Implementation: \t") # User input to guide image processing

    image_to_speech = Image_to_speech(user_input, api_key, image_output_dir) # Initialize the Image_to_speech class
    image_to_speech.process_images(user_input) # Process images based on user input

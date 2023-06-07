import openai
import json
import os
from urllib import request
import whisper
import subprocess

subject = "ENGR301"
download = False
transcribe = True
summarize = True

# step 1 Get user to paste in url
def find_ios_video_urls(data, key):
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                results.append(v)
            elif isinstance(v, (dict, list)):
                results.extend(find_ios_video_urls(v, key))
    elif isinstance(data, list):
        for item in data:
            results.extend(find_ios_video_urls(item, key))
    return results

# Download all the videos to folder on pc, user will prompt name
def download_files(urls, subject):
    # Create the subfolder if it doesn't exist
    if not os.path.exists(subject):
        os.makedirs(subject)
    
    total = len(urls)

    for url in urls:
        # Extract the filename from the URL
        filename = subject + "-Lecture-" + str(total)
        total -= 1

        # Download the file
        file_path = os.path.join(subject, filename)
        request.urlretrieve(url, file_path)

        print(f"Downloaded: {filename}")

# For each video in the folder, send it to whisper.ai to process it
def transcribe_videos(subject):
    model = whisper.load_model("base")
    for video in os.listdir(subject):
        result = model.transcribe(os.path.join(subject, video), verbose=True)
        text = result["text"]
        with open(os.path.join(subject, video + ".txt"), "w") as f:
            f.write(text)
            print(f"Transcribed: {video}")

    # for video in os.listdir(subject):
    #     text = model.transcribe(os.path.join(subject, video))
    #     # save the text in a file with the name of the video
    #     with open(os.path.join(subject, video + ".txt"), "w") as f:
    #         f.write(text)
    #     print(f"Transcribed: {video}")

        

# Save Transcript in seperate transcript folder within the video directory.

# F0r each transcript, make a request to openai
def get_response(instructions, transcript, question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    messages.append({ "role": "user", "content": "This is the transcript" + transcript })
    # # add the previous questions and answers
    # for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
    #     messages.append({ "role": "user", "content": question })
    #     messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=1024,
        top_p=1,
    )
    return completion.choices[0].message.content

def get_cheatsheet(transcript, questions):


    # Summarize
    system_role = "You are a helpful study assistant that summarizes lecture transcripts."
    print(get_response(system_role, transcript, "Generate me a summary of this lecture."))
    # Generate Exam Questions
    system_role = "You are a helpful study assistant that generates potential exam questions."
    # Generate notes
    system_role = "You are a helpful study assistnat that generates notes in __ format."

def main():
    # get json data from file
    if download:
        json_data = open("requests.json").read()

        parsed_data = json.loads(json_data)
        ios_video_urls = find_ios_video_urls(parsed_data, "IosVideoUrl")
        download_files(ios_video_urls, subject)

    if transcribe:
        transcribe_videos(subject)

main()
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64
from PIL import Image
import os
from openai import OpenAI
import requests

st.set_page_config(
    page_title="Talking Talita",
    page_icon="🎙️",
    layout="centered"
)

client2 = OpenAI(
    base_url = '', # Ollama Server
    api_key='ollama', # required, but unused
    )

#initialize openai client
def setup_openai_client(api_key):

    return openai.OpenAI(api_key=api_key)
    
#function to transcribe audio to text
def transcribe_audio(client, audio_path):

    with open(audio_path, "rb") as audio_file:
        transcript= client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

# taking response from Openai
def fetch_ai_response(client2, input_text, model):
    system_prompt = """You are a helpful assistant called Talita. You are working at Lintasarta an ICT company. You're able to reply with a perfect sentences in the same language that the humans address you. You should answer questions in maximum 50 words.
    
    Lintasarta is an Information and Communication Technology company that offers end-to-end solutions established in 1988.
    
    Jajaran Direksi Lintasarta saat ini adalah:
    1. President Director and CEO : Bayu Hanantasena
    2. Director and Chief Solution Officer : Zulfi Hadi
    3. Director and Chief Commercial Officer : Fitrah Muhammad
    4. Director and Chief Delivery Operation Officer : Ginandjar
    5. Director and Chief Financial Officer : Hariyadi Ramelan

    Noble Purpose : Empower Indonesia to accelerate unleashing the nation’s digital potential.
    Vision : To be the leader in business information and communications solutions in Indonesia.
    Mission : To make business easier and add value for customers through innovative information and communication technology solutions.
    Our Value : "I CARE", Innovation, Collaboration, Agility, Resilience and Ethics.
    """

    # All IT systems in Lintasarta including AI and Machine Learning development are managed by the Corporate IT team, which is led by Feby Ferdinan Syah, the General Manager of Corporate IT.
    
    # messages = [{"role": "user", "content": input_text}]
    messages = [{"role": "system", "content": system_prompt}, 
                {"role": "user", "content": input_text}]
    # response = client2.chat.completions.create(model="mixtral", messages=messages)
    response = client2.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content

# convert text to audio
def text_to_audio(client2, text, audio_path):
    response=client2.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(audio_path)

# text cards function
def create_text_card(text, title="Response"):
    card_html = f"""
    <style>
        .card {{
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            border-radius: 5px;
            padding: 15px;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }}
        .container {{
            padding: 2px 16px;
        }}
    </style>
    <div class="card">
        <div class="container">
            <h4><b>{title}</b></h4>
            <p>{text}</p>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# auto-play audio function
    
def auto_play_audio(audio_file):

    with open(audio_file, "rb") as audio_file:
        audio_bytes=audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

def main():

    # st.sidebar.image(Image.open('talita.png'), caption='', width=100)
    # st.sidebar.title("API KEY CONFIGURATION")
    # api_key = st.sidebar.text_input("Enter your API key", type="password")
    api_key = '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'

    # st.image(Image.open('/Users/febyferdinansyah/Library/CloudStorage/OneDrive-Personal/6-My-Projects/AI/Streamlit Apps/AI Voice Assistant/talita.png'), caption='', width=100)
    st.header("🎙️ Talking Talita", anchor=False, divider="orange")
    st.markdown("Powered by **:blue[Lintasarta GPU Cloud].**")
    st.write("")
    # st.write("Hi there! Click on the mic icon to interact with me. How can I assist you today?")
    
    # mic_col, transcription_col = st.columns([2, 3])
    blank_col, mic_col, transcription_col = st.columns([1, 1, 1])

    blank_col.write("Hi there! Click on the mic icon to interact with me. How can I assist you today?")

    #check if api key is there
    if api_key:
        model_choice = st.sidebar.selectbox("Select model",["llama3"])

        client = setup_openai_client(api_key)
        with mic_col:
            recorded_audio = audio_recorder(
                                        text="",
                                        recording_color="#e8b62c",
                                        neutral_color="#6aa36f",
                                        icon_name="microphone-lines",
                                        icon_size="10x",
                                    )
        print("get api key success...")
        print(api_key)
        try: #add2
            #check if recording is done and available
            if recorded_audio:
                print("Attempting to write the audio file...")
                # Specify file path
                audio_dir = '/home/talita/ai-voice-assistant/'
                if not os.path.exists(audio_dir):
                    print(f"Directory does not exist, creating now at {audio_dir}")
                    os.makedirs(audio_dir)

                audio_file = os.path.join(audio_dir, "audio.mp3")

                try:
                    with open(audio_file, "wb") as f:
                        f.write(recorded_audio)
                        f.close()
                    print(f"Successfully written audio file at: {audio_file}")
                except Exception as e:
                    print(f"Failed to write audio file at: {audio_file}")
                    print(f"Error was: {str(e)}")

                print("Finished attempting to write the audio file.")

                # with transcription_col:
                #     transcribed_text=transcribe_audio(client, audio_file)
                #     create_text_card(transcribed_text, "Audio Transcription")

                transcription_col.write("")

                transcribed_text=transcribe_audio(client, audio_file)
                create_text_card(transcribed_text, "Audio Transcription")
                
                st.write("")
                
                if model_choice:
                    ai_response = fetch_ai_response(client2, transcribed_text, model_choice)
                    data = {"message": ai_response}

                    # Make the POST request to the server
                    response = requests.post("http://localhost:3000/send-data", json=data)
                    if response.status_code == 200:
                        print("Data sent successfully!")
                    else:
                        print(f"Failed to send data. Status code: {response.status_code}")

                    # response_audio_file = "audio_response.mp3"
                    # text_to_audio(client, ai_response, response_audio_file)
                    # auto_play_audio(response_audio_file)
                    # # create_text_card(ai_response, "AI Response")
                    # st.subheader("AI Response")
                    # st.markdown(ai_response)
        except Exception as e:
            if 'Error code: 400' in str(e):
                st.error('Audio is too short')
            else:
                st.error('Terjadi kesalahan lain: {}'.format(str(e)))



if __name__ == "__main__":
    main()


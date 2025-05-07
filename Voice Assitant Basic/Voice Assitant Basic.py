import tkinter as tk
from tkinter import scrolledtext, ttk
import speech_recognition as sr
import pyttsx3
import datetime
import pywhatkit
import wikipedia
import threading
import time
import requests

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Echo Voice Assistant")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Initialize voice engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', self.engine.getProperty('voices')[1].id)
        self.engine.setProperty('rate', 150)
        
        # Configuration
        self.ASSISTANT_NAME = "echo"
        self.WAKE_WORDS = ["wake up"]
        self.STOP_COMMANDS = ["bye", "exit", "stop", "thank you"]
        
        # User settings
        self.USER_PROFILE = {
            "name": "User",
            "city": "New York"
        }
        
        # API Keys
        self.WEATHER_API_KEY = "your_weather_api_key"
        self.NEWS_API_KEY = "your_news_api_key"
        
        # GUI Elements
        self.setup_gui()
        
        # Start assistant thread
        self.listening = False
        self.assistant_thread = threading.Thread(target=self.assistant_loop, daemon=True)
        self.assistant_thread.start()
    
    def setup_gui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Echo Voice Assistant", 
            font=('Helvetica', 18, 'bold'), 
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Conversation Display
        self.conversation = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=70, 
            height=20,
            font=('Arial', 10),
            bg='white',
            fg='#333333'
        )
        self.conversation.pack(padx=20, pady=10)
        self.conversation.insert(tk.END, "Echo: Hello! Say 'wake up' to start.\n")
        self.conversation.config(state=tk.DISABLED)
        
        # Controls Frame
        controls_frame = tk.Frame(self.root, bg='#f0f0f0')
        controls_frame.pack(pady=10)
        
        # Microphone Button
        self.mic_button = ttk.Button(
            controls_frame,
            text="🎤",  # Using emoji as icon
            command=self.toggle_listening,
            style='Toolbutton'
        )
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Status Indicator
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(
            controls_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Style Configuration
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('Toolbutton', background='#3498db')
        style.map('Listening.TButton', background=[('active', 'red')])
        
        # Add some color to the conversation tags
        self.conversation.tag_config('assistant', foreground='#2980b9')
        self.conversation.tag_config('user', foreground='#27ae60')
        self.conversation.tag_config('system', foreground='#7f8c8d')
    
    def toggle_listening(self):
        self.listening = not self.listening
        if self.listening:
            self.status_var.set("Listening...")
            self.mic_button.config(style='Listening.TButton')
            self.update_conversation("System: Listening activated\n", 'system')
        else:
            self.status_var.set("Ready")
            self.mic_button.config(style='TButton')
            self.update_conversation("System: Listening deactivated\n", 'system')
    
    def update_conversation(self, text, tag=None):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.insert(tk.END, text, tag)
        self.conversation.see(tk.END)
        self.conversation.config(state=tk.DISABLED)
    
    def talk(self, text):
        self.update_conversation(f"Echo: {text}\n", 'assistant')
        self.engine.say(text)
        self.engine.runAndWait()
    
    def take_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_var.set("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                self.update_conversation(f"You: {command}\n", 'user')
                return command
            except sr.UnknownValueError:
                self.update_conversation("System: Could not understand audio\n", 'system')
            except sr.RequestError as e:
                self.update_conversation(f"System: Could not request results; {e}\n", 'system')
            finally:
                if not self.listening:
                    self.status_var.set("Ready")
        return None
    
    def get_weather(self, city=None):
        city = city or self.USER_PROFILE["city"]
        try:
            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.WEATHER_API_KEY}&units=imperial"
            )
            data = response.json()
            if response.status_code == 200:
                return {
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
        except Exception as e:
            self.update_conversation(f"System: Weather API error - {e}\n", 'system')
        return None
    
    def get_news(self, category="general"):
        try:
            response = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={self.NEWS_API_KEY}"
            )
            data = response.json()
            if data['status'] == 'ok':
                return [article['title'] for article in data['articles'][:3]]
        except Exception as e:
            self.update_conversation(f"System: News API error - {e}\n", 'system')
        return None
    
    def process_command(self, command):
        if not command:
            return
        
        if any(wake_word in command for wake_word in self.WAKE_WORDS):
            self.talk("Yes, I'm listening!")
            return True
        
        if any(stop_cmd in command for stop_cmd in self.STOP_COMMANDS):
            self.talk("Goodbye! Let me know if you need anything else.")
            return False
        
        if 'weather' in command:
            city = None
            if 'in' in command:
                city = command.split('in')[-1].strip()
            weather = self.get_weather(city)
            if weather:
                response = (f"Weather in {city or self.USER_PROFILE['city']}: "
                           f"{weather['description']}, {weather['temperature']}°F, "
                           f"Humidity: {weather['humidity']}%, Wind: {weather['wind_speed']} mph")
                self.talk(response)
            else:
                self.talk("Sorry, I couldn't fetch the weather information.")
        
        elif 'news' in command:
            category = "general"
            if 'sports' in command:
                category = "sports"
            elif 'technology' in command:
                category = "technology"
            news = self.get_news(category)
            if news:
                self.talk(f"Here are the latest {category} news headlines:")
                for i, headline in enumerate(news, 1):
                    self.talk(f"{i}. {headline}")
            else:
                self.talk("Sorry, I couldn't fetch the news right now.")
        
        elif 'time' in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            self.talk(f"The current time is {current_time}")
        
        elif 'date' in command:
            today = datetime.datetime.now().strftime('%B %d, %Y')
            self.talk(f"Today's date is {today}")
        
        elif any(cmd in command for cmd in ['search for', 'search', 'look up']):
            query = command.replace('search for', '').replace('search', '').replace('look up', '').strip()
            self.talk(f"Searching for {query}")
            pywhatkit.search(query)
        
        elif any(cmd in command for cmd in ['who is', 'what is', 'tell me about']):
            query = command.replace('who is', '').replace('what is', '').replace('tell me about', '').strip()
            try:
                summary = wikipedia.summary(query, sentences=2)
                self.talk(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                self.talk(f"There are multiple options. Did you mean: {e.options[0]}?")
            except wikipedia.exceptions.PageError:
                self.talk("I couldn't find any information about that topic.")
        
        else:
            self.talk("I'm not sure how to help with that. Could you try rephrasing?")
        
        return True
    
    def assistant_loop(self):
        while True:
            if self.listening:
                command = self.take_command()
                if command:
                    if not self.process_command(command):
                        self.listening = False
                        self.mic_button.config(style='TButton')
                        self.status_var.set("Ready")
            time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()
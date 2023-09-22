from termcolor import colored
from .constants import TIME_FILTERS, URL_OPTIONS
import requests

def get_url_option():
    print(colored('Choose a URL option:', 'cyan'))
    print('1: Search Query')
    print('2: Trending Videos')
    print('3: Gaming Videos')

    choice = input('Enter your choice (1-3): ').strip()
    return URL_OPTIONS.get(choice, '1')

def get_time_filter():
    print(colored('Choose a time filter:', 'cyan'))
    print('1: Last Hour')
    print('2: Today')
    print('3: This Week')
    print('4: This Month')
    print('5: This Year')
    print('6: No Filter (default)')

    choice = input('Enter your choice (1-6): ').strip()
    return TIME_FILTERS.get(choice, '')

def get_platform_option():
    print(colored('Choose a platform option:', 'cyan'))
    print('1: YouTube Search')
    print('2: YouTube Video')
    print('3: Title Video Scraper')
    print('4: Random Title Video Scraper')
    print('5: Train Model')
    print('6: Generate YouTube Title')

    choice = input('Enter your choice (1-6): ').strip()
    return choice


def get_video_option():
    print(colored('Choose a video option:', 'cyan'))
    print('1: YouTube Like Count')
    print('2: Description')
    print('3: Download')

    choice = input('Enter your choice (1-3): ').strip()
    return choice

def send_discord_message(content):
    WEBHOOK_URL = 'WebHookHere'  # Replace this with your webhook URL
    data = {"content": content}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print("Failed to send message to Discord:", response.text)
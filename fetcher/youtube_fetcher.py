# youtube_fetcher.py

import re
import requests
from termcolor import colored
from helper.constants import TIME_FILTERS, URL_OPTIONS
import youtube_dl
import dateparser
import aiohttp
import asyncio
from aiohttp import ClientSession

def fetch_youtube_titles(url, time_filter=''):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url + time_filter, headers=headers)
    
    if response.status_code != 200:
        print(colored('Error fetching YouTube titles!', 'red'))
        return []

    patterns = re.findall(r'{"label":"([^"]+ by [^"]+ views [^"]+ ago [^"]+ minutes?[^"]+)".+?"videoId":"([^"]+)"', response.text)

    videos = []
    for pat in patterns:
        try:
            title = re.search(r'^(.+?) by', pat[0]).group(1)
            views = int(re.search(r'([\d,]+) views', pat[0]).group(1).replace(',', ''))
            link = f"https://www.youtube.com/watch?v={pat[1]}"
            videos.append((title, views, link))
        except AttributeError:
            # Skip this entry and move on to the next
            continue

    return videos
async def async_fetch_youtube_titles(session, url, time_filter=''):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    async with session.get(url + time_filter, headers=headers) as response:
        if response.status != 200:
            print(colored('Error fetching YouTube titles!', 'red'))
            return []

        text = await response.text()
        patterns = re.findall(r'{"label":"([^"]+ by [^"]+ views [^"]+ ago [^"]+ minutes?[^"]+)".+?"videoId":"([^"]+)"', text)

        videos = []
        for pat in patterns:
            try:
                title = re.search(r'^(.+?) by', pat[0]).group(1)
                views = int(re.search(r'([\d,]+) views', pat[0]).group(1).replace(',', ''))
                link = f"https://www.youtube.com/watch?v={pat[1]}"
                videos.append((title, views, link))
            except AttributeError:
                continue

        return videos

def fetch_video_content(video_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    response = requests.get(video_url, headers=headers)
    
    if response.status_code != 200:
        print(colored('Error fetching YouTube video content!', 'red'))
        return

    with open('video_content.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)

    print(colored('Video content saved to video_content.txt', 'green'))
    
def extract_likes_from_content():
    with open('video_content.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'{"simpleText":"Likes"},"accessibilityText":"([\d\.K]+) likes"}', content)
    if match:
        return match.group(1)
    return None

def extract_description_from_content():
    with open('video_content.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'attributedDescription":{"content":"(.*?)",', content, re.DOTALL)
    if match:
        return match.group(1).replace('\n', ' ').strip()
    return None

def download_video(video_url):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        


from termcolor import colored
import random
from tqdm import tqdm
import aiohttp
import asyncio
from aiohttp import ClientSession
from helper.constants import TIME_FILTERS, URL_OPTIONS, RANDOM_TERMS
from helper.utils import get_url_option, get_time_filter, get_platform_option, get_video_option, send_discord_message
from fetcher.youtube_fetcher import (fetch_youtube_titles, fetch_video_content, 
                                     extract_likes_from_content, extract_description_from_content, 
                                     download_video, async_fetch_youtube_titles)
from model.model import YouTubeTitleGenerator


def get_multiple_search_queries():
    queries = []
    while True:
        query = input(colored('Enter a YouTube search query or hit ENTER to start scraping: ', 'cyan')).strip()
        if not query:
            break
        queries.append(query)
    return queries

def main():
    platform_option = get_platform_option()

    if platform_option == '1':
        url_option = get_url_option()
        if url_option == URL_OPTIONS['1']:
            query = input(colored('Enter your YouTube search query: ', 'cyan'))
            time_filter = get_time_filter()
            videos = fetch_youtube_titles(URL_OPTIONS['1'] + query, time_filter)
        else:
            videos = fetch_youtube_titles(url_option)

        sorted_videos = sorted(videos, key=lambda x: x[1], reverse=True)[:10]

        print(colored('Top 10 YouTube Videos by Views:', 'blue'))
        for idx, (title, views, link) in enumerate(sorted_videos, 1):
            print(colored(f'{idx}. Title: {title}', 'green'))
            print(colored(f'   Views: {views:,}', 'yellow'))
            print(colored(f'   Link: {link}', 'cyan'))

    elif platform_option == '2':
        video_url = input(colored('Enter the YouTube video link: ', 'cyan'))
        video_option = get_video_option()
        
        # Fetch and save content of the provided video URL
        fetch_video_content(video_url)

        if video_option == '1':
            likes = extract_likes_from_content()
            print(colored(f'Likes: {likes}', 'green'))
        elif video_option == '2':
            description = extract_description_from_content()
            print(colored(f'Description: {description}', 'green'))
        elif video_option == '3':
            download_video(video_url)

    elif platform_option == '3':
        queries = get_multiple_search_queries()
        with open('scraped_titles.txt', 'a', encoding='utf-8') as file:
            for query in queries:
                videos = fetch_youtube_titles(URL_OPTIONS['1'] + query)
                for title, _, _ in videos:
                    file.write(title + '\n')
    elif platform_option == '4':
        titles_to_write = []

        async def fetch_all_titles():
            async with ClientSession() as session:
                tasks = []
                for query in RANDOM_TERMS:
                    for time_key, time_filter in TIME_FILTERS.items():
                        tasks.append(async_fetch_youtube_titles(session, URL_OPTIONS['1'] + query + time_filter))
                return await asyncio.gather(*tasks)

        loop = asyncio.get_event_loop()
        all_videos = loop.run_until_complete(fetch_all_titles())

        for videos in all_videos:
            for title, _, _ in videos:
                titles_to_write.append(title)

        with open('scraped_titles.txt', 'a', encoding='utf-8') as file:
            for title in titles_to_write:
                file.write(title + '\n')
        send_discord_message("Finished scraping titles!")
    elif platform_option == '5':
        title_generator = YouTubeTitleGenerator()
        with open("scraped_titles.txt", 'r', encoding='utf-8') as file:
            titles = file.readlines()
        title_generator.train(titles)
        title_generator.save_model("model/youtube_title_generator_model.h5")
        send_discord_message("Finished training model!")

        print("Model trained and saved!")

    elif platform_option == '6':
        title_generator = YouTubeTitleGenerator()
        max_sequence_len, total_words = title_generator.load_model("model/youtube_title_generator_model.h5", titles)
        prompt = input("Enter a prompt: ")
        generated_title = title_generator.generate_title(prompt, max_sequence_len, total_words)
        print("Generated Title:", generated_title)
        
if __name__ == "__main__":
    main()

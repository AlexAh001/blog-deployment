import requests


NEWS_API_KEY = "pub_27338d0060f78fb7c6769177e1b5fc67d6599"
NEWS_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology"


tech_news_page_1 = requests.get(NEWS_ENDPOINT).json()
PAGE_2_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_1['nextPage']}"
tech_news_page_2 = requests.get(PAGE_2_ENDPOINT).json()
PAGE_3_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_2['nextPage']}"
tech_news_page_3 = requests.get(PAGE_3_ENDPOINT).json()
PAGE_4_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_3['nextPage']}"
tech_news_page_4 = requests.get(PAGE_4_ENDPOINT).json()
PAGE_5_ENDPOINT = f" https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=be,fr,de,nl,gb&language=nl,en&category=technology&page={tech_news_page_4['nextPage']}"
tech_news_page_5 = requests.get(PAGE_5_ENDPOINT).json()

print(tech_news_page_3)
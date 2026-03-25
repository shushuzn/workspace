import feedparser

feeds = [
    'https://aws.amazon.com/blogs/architecture/feed/',
    'https://blog.google/technology/ai/rss.xml',
    'https://openai.com/blog/rss.xml',
    'https://news.ycombinator.com/rss',
]

for f in feeds:
    feed = feedparser.parse(f)
    domain = f.split('/')[2]
    print(f'{domain}: {len(feed.entries)} articles')
    if feed.entries:
        print(f'  Latest: {feed.entries[0].title[:50]}')

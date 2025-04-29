import feedparser
from datetime import datetime

def parse_rss(feed_url: str) -> dict | None:
    """
    Parses an RSS feed and extracts its information and entries.

    Args:
        feed_url: The URL of the RSS feed.

    Returns:
        A dictionary containing the parsed feed information,
        or None if parsing fails or the feed is empty.
        The dictionary structure is:
        {
            'feed': {
                'title': str,
                'link': str,
                'description': str
            },
            'entries': [
                {
                    'title': str,
                    'link': str,
                    'published': datetime | None,
                    'summary': str
                },
                ...
            ]
        }
    """
    parsed_feed = feedparser.parse(feed_url)

    if parsed_feed.bozo:
        print(f"Error parsing feed {feed_url}: {parsed_feed.bozo_exception}")
        # Depending on the error, you might want to return None or raise an exception
        # For now, we'll proceed but log the error.

    if not parsed_feed.feed and not parsed_feed.entries:
        print(f"Feed {feed_url} seems empty or couldn't be fetched properly.")
        return None

    feed_info = {
        'title': parsed_feed.feed.get('title', ''),
        'link': parsed_feed.feed.get('link', ''),
        'description': parsed_feed.feed.get('description', '')
    }

    entries_list = []
    for entry in parsed_feed.entries:
        published_time = None
        if 'published_parsed' in entry and entry.published_parsed:
            try:
                # feedparser returns time.struct_time, convert to datetime
                published_time = datetime(*entry.published_parsed[:6])
            except ValueError:
                print(f"Could not parse date for entry: {entry.get('title', 'N/A')}")
                published_time = None # Keep as None if parsing fails
        elif 'updated_parsed' in entry and entry.updated_parsed:
             try:
                # Fallback to updated time if published time is not available
                published_time = datetime(*entry.updated_parsed[:6])
             except ValueError:
                print(f"Could not parse updated date for entry: {entry.get('title', 'N/A')}")
                published_time = None

        entry_data = {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': published_time,
            'summary': entry.get('summary', entry.get('description', '')) # Use description as fallback for summary
        }
        entries_list.append(entry_data)

    return {
        'feed': feed_info,
        'entries': entries_list
    }

# Example usage (optional):
if __name__ == '__main__':
    # Replace with a real RSS feed URL for testing
    test_url = "http://www.example.com/rss.xml" # Replace with a valid RSS feed
    # Example: test_url = "http://feeds.bbci.co.uk/news/rss.xml"
    
    # Note: Running this example requires a valid feed URL.
    # If using the placeholder, it will likely print an error or return None.
    parsed_data = parse_rss(test_url)

    if parsed_data:
        print("Feed Title:", parsed_data['feed']['title'])
        print("Feed Link:", parsed_data['feed']['link'])
        print("-" * 20)
        for item in parsed_data['entries']:
            print("Entry Title:", item['title'])
            print("Entry Link:", item['link'])
            print("Entry Published:", item['published'])
            print("Entry Summary:", item['summary'][:100] + "..." if item['summary'] else "") # Print first 100 chars
            print("-" * 10)
    else:
        print(f"Could not parse feed: {test_url}")

# Source: https://github.com/eugeneyan/eugeneyan/

import feedparser
import pathlib
import re
from datetime import datetime

root = pathlib.Path(__file__).parent.resolve()

# Find the search trigger in readme
# This is done by searching for comment blocks for "Blogpost"
# e.g. "Blogpost starts" "Blogpost ends" in readme
def replace_writing(content, marker, chunk, inline=False):
    r = re.compile(
        r'<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->'.format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = '\n{}\n'.format(chunk)
    chunk = '<!-- {} starts -->{}<!-- {} ends -->'.format(marker, chunk, marker)
    return r.sub(chunk, content)

# Fetch the lastest 5 posts by feedparser

def fetch_writing():
    urls = [
        'https://asterhu.com/post/index.xml',
        'https://asterhu.com/thoughts/index.xml'
    ]
    
    all_entries = []
    total_entry_count = 0
    
    for url in urls:
        feed = feedparser.parse(url)
        entries = feed['entries']
        total_entry_count += len(entries)
        all_entries.extend(entries[:5])
    
    # Sort by published date (assuming RSS feed provides a valid format)
    all_entries.sort(key=lambda entry: datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %Z'), reverse=True)
    
    return [
        {
            'title': entry['title'],
            'url': entry['link'].split('#')[0],
            'published': datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d') #Convert date format to YYYY-MM-dd
        }
        for entry in all_entries[:5]  # Keep only the top 5 most recent entries
    ], total_entry_count
    

# Execution the code
if __name__ == '__main__':
    readme_path = root / 'README.md'
    readme = readme_path.open().read()
    entries, entry_count = fetch_writing()
    print(f'Recent 5: {entries}, Total count: {entry_count}')
    entries_md = '\n'.join(
        ['* [{title}]({url}) - {published}'.format(**entry) for entry in entries]
    )

    # Update entries
    rewritten_entries = replace_writing(readme, 'Blogpost', entries_md)
    readme_path.open('w').write(rewritten_entries)

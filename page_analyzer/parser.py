from bs4 import BeautifulSoup


def parse_html(html_content):
    """Извлекает h1, title и description из HTML-контента"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    h1_tag = soup.find('h1')
    title_tag = soup.find('title')
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    
    return {
        'h1': h1_tag.string if h1_tag else '',
        'title': title_tag.string if title_tag else '',
        'description': desc_tag.get('content', '') if desc_tag else ''
    }
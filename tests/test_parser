from page_analyzer.parser import parse_html

def test_parse_html():
    """Проверка извлечения h1, title и description из HTML."""
    html_content = """
    <html>
        <head>
            <title>Test Title</title>
            <meta name="description" content="Test Description">
        </head>
        <body>
            <h1>Test H1</h1>
        </body>
    </html>
    """
    result = parse_html(html_content)
    
    assert result['h1'] == "Test H1"
    assert result['title'] == "Test Title"
    assert result['description'] == "Test Description"

def test_parse_html_missing_tags():
    """Проверка обработки отсутствующих тегов."""
    html_content = """
    <html>
        <head></head>
        <body></body>
    </html>
    """
    result = parse_html(html_content)
    
    assert result['h1'] == ""
    assert result['title'] == ""
    assert result['description'] == ""

def test_parse_html_partial_tags():
    """Проверка обработки частично заполненных тегов."""
    html_content = """
    <html>
        <head>
            <title>Only Title</title>
        </head>
        <body>
            <h1>Only H1</h1>
        </body>
    </html>
    """
    result = parse_html(html_content)
    
    assert result['h1'] == "Only H1"
    assert result['title'] == "Only Title"
    assert result['description'] == ""

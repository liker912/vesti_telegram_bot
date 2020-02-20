import urllib.request
import ssl
import json
import bs4
import datetime
import helpers


# get data from
# return string xml body
def get_rss_xml(url):
    try:
        response = urllib.request.urlopen(url)
        return response.read()
    except Exception as e:
        helpers.write_to_log("Catch from parser.get_rss_xml()\n" + str(e))


# get all news links
# return xml nodes of articles links from xml string
def get_links(xml):
    try:
        soup = bs4.BeautifulSoup(xml, features='xml')
        links = []
        for item in soup.find_all('item'):
            pub_date = datetime.datetime.strptime(item.pubDate.text, '%a, %d %b %Y %H:%M:%S %z')
            links.append({"link": item.link.text,
                          "pub_date": pub_date})
        links = sorted(links, key=lambda k: k['pub_date'], reverse=False)

        return [link['link'] for link in links if 'link' in link]
    except Exception as e:
        helpers.write_to_log("Catch from parser.get_links()\n" + str(e))


# start parse content from news links
# return article dict
def run_parse(link):
    try:
        article = {'title': '', 'description': '', 'body': '', 'keywords': '', 'video': [], 'publisher': '',
                   'original_link': '', 'images': []}
        get_json_content(get_html_content_by_link(link), article)
        is_correct_structure = parse_html_content(get_html_content_by_link(link), article)

        if is_correct_structure is False:
            return False
        else:
            return article
    except Exception as e:
        helpers.write_to_log("Catch from parser.run_parse()\n" + str(e))


# get html content from ynet news link
# return html body string
def get_html_content_by_link(link):
    print("HERE", link)
    try:
        response = urllib.request.urlopen(link)
        return response.read()
    except Exception as e:
        helpers.write_to_log("Catch from parser.get_html_content_by_link()\n" + str(e))


# get news information from ynet js tag in json format
def get_json_content(html, article):
    try:
        soup = bs4.BeautifulSoup(html, features='lxml')
        all_jsons = soup.find_all('script', type='application/ld+json')

        for item in all_jsons:
            # convert data from string to json
            item = json.loads(item.text)

            # NewsArticle contain title, description, author image list,
            if item['@type'] == "NewsArticle":
                article['title'] = item['headline']
                article['description'] = item['description']
                article['keywords'] = item['keywords']
                article['publisher'] = item['publisher']['name']
                article['original_link'] = item['mainEntityOfPage']['@id']
                article['images'] = item['image'].copy()

            elif item['@type'] == "VideoObject":
                if article['video'] is None:
                    article['video'] = []

                if item['uploadDate'] is not None and item['uploadDate'] != "":
                    article['video'].append(
                        {'url': get_video_link(item['contentUrl'], item['embedUrl']),
                         'upload_date': datetime.datetime.strptime(item['uploadDate'],
                                                                   '%Y-%m-%dT%H:%M:%SZ')})
                else:
                    article['video'].append(
                        {'url': get_video_link(item['contentUrl'], item['embedUrl']),
                         'upload_date': datetime.datetime.today()})
            else:
                continue

        # if video more than one needs to sort it by upload date
        if len(article['video']) > 1:
            # create helper list with sort video
            article['sort_video'] = sorted(article['video'], key=lambda k: k['upload_date'], reverse=False)
            # replace unsort video to sort
            article['video'] = article['sort_video'].copy()
            # remove helper list
            del article['sort_video']
    except Exception as e:
        helpers.write_to_log("Catch from parser.get_json_content()\n" + str(e))


# prepare article content for post in telegraph
def parse_html_content(html, article):
    try:
        first_soup = bs4.BeautifulSoup(html, features='lxml')
        soup = bs4.BeautifulSoup(str(first_soup), 'html.parser')

        # if soup is None exit from method

        div = soup.find('div', class_="text14")

        if div is None:
            return False

        span = div.find('span')

        # remove all comments from span
        for element in span(text=lambda text: isinstance(text, bs4.Comment)):
            element.extract()

        # find naked text and put it to time tag
        for node in span:
            if isinstance(node, bs4.element.NavigableString):
                # temporary tag
                tag = soup.new_tag('time')
                tag.append(str(node))
                node.replace_with(tag)

        # find tags with text and images
        all_nodes = span.find_all()

        article['body'] += '<p>' + article["keywords"] + '</p>'
        article['body'] += '<p>' + article["description"] + '</p>'

        for node in all_nodes:
            # remove some not use tags
            for not_use_tag in node.find_all(['script', 'link', 'form', 'label', 'input', 'iframe', 'img']):
                if not_use_tag.name == 'img':
                    if not_use_tag['src'] not in article['images']:
                        not_use_tag.extract()
                else:
                    not_use_tag.extract()

            # checking if current node is paragraph
            if node.name == 'p':
                if node.a:
                    article['body'] += str(node)
                    children = node.findChildren('a')
                    for child in children:
                        child.decompose()
                elif node.font:
                    article['body'] += '<b>' + node.font.text + '</b>'
                else:
                    if str(node) != '<p>Подключайтесь к Telegram-каналу "Вестей"</p>':
                        article['body'] += str(node)

            if node.name == 'ul':
                article['body'] += str(node)

            # checking if current node is headers
            elif node.name == 'h1' or node.name == 'h2' or node.name == 'h3':
                if check_title_classes('sf_', node.get_attribute_list('class')) is False and len(
                        node.findChildren()) == 0:
                    article['body'] += '<h3>' + node.text + '</h3>'

            elif node.name == 'h4' or node.name == 'h5' or node.name == 'h6':
                if check_title_classes('sf_', node.get_attribute_list('class')) is False and len(
                        node.findChildren()) == 0:
                    article['body'] += '<h4>' + node.text + '</h4>'

            # checking if current node is img and get images from article with full link
            elif node.name == 'img' and 'https://' in node['src'] and node.has_attr('title'):
                # and node['src'] in article['images']:
                img = '<img style="display: block; margin: 10px 0 0 0" src="' + node["src"] + '" title="' \
                      + node['title'] + '"' + 'width="450"/><br>'
                article['body'] += img
                article['body'] += '<b style="display: block; margin: 0 0 10px 0">' + node["title"] + '</b><br>'

            # checking if current node time (temporary tag for not wrapper text from original html)
            elif node.name == 'time':
                if node.string != u'\xa0':
                    article['body'] += node.text

            # checking if current node a
            elif node.name == 'a':
                if 'bluelink' in node.get_attribute_list('class'):
                    if 'https://t.me/vestyisrael' not in node.get_attribute_list('href'):
                        article['body'] += str(node)

            # checking if current node div
            elif node.name == 'div':
                if 'art_video' in node.get_attribute_list('class'):
                    # put video iframe
                    if article['video'] is not None:
                        content = article['video'].pop()
                        if 'youtube' in content['url']:
                            article['body'] += '<iframe width="450" height="450" frameborder="0" src="' + content[
                                'url'] + '"></iframe>'
                        else:
                            article['body'] += '<video width="450" height="450" frameborder="0" controls>'
                            article['body'] += '<source src="' + content['url'] + '" type="video/mp4"></video>'
            else:
                continue

        # bottom link to original source
        link = 'Ссылка на источник '
        article['body'] += '<a href="' + article["original_link"] + '">' + link + article[
            'publisher'] + '</a>'

    except Exception as e:
        helpers.write_to_log("Catch from parser.parse_html_content()\n" + str(e), False)


# helper function for creating youtube embed link
def get_video_link(original, embed):
    if 'youtube' in embed:
        return "https://www.youtube.com/embed/" + embed[embed.find('?v=') + 3:]
    else:
        return original


# checking headers if class substring exists in its class
def check_title_classes(substring, class_list):
    for class_item in class_list:
        if class_item is not None:
            if substring in class_item:
                return True
    return False

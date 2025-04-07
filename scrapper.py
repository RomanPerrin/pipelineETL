import os
import json
import requests
import regex
from bs4 import BeautifulSoup

def main(linkPrefix = 'https://en.wikipedia.org', pages = ['glycemia', 'estrogen', 'testosterone'], dir = "", save=False):
    if type(pages) != list:
        pages = [pages]
    data = getWikiData(linkPrefix, pages)

    if save:
        if not dir:
            dir = os.path.dirname(os.path.normpath(__file__))
        file = os.path.join(dir, "data.json")
        try:
            with open(file, "w") as f:
                f.write(json.dumps(data, indent=4))
        except IOError:
            print("couldn't open file")
        except json.decoder.JSONDecodeError:
            print("not a Json")

    return data

def readData(file=""):
    if not file:
        dir = os.path.dirname(os.path.normpath(__file__))
        file = os.path.join(dir, "data.json")

    try:
        with open(file, "r") as f:
            data = json.loads(f.read())
    except IOError:
        print("couldn't open file")
    except json.decoder.JSONDecodeError:
        print("not a Json")
    
    return data

def getWikiData(linkPrefix = 'https://en.wikipedia.org', pages = ['glycemia']):
    data = {}
    for page in pages:
        print(f'Processing: {page}')
        r = requests.get(f'{linkPrefix}/wiki/{page.title()}')
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html5lib')
            data[page] = cleanWikiData(soup, linkPrefix=linkPrefix)

    return data

def cleanWikiData(data: BeautifulSoup, linkPrefix: str=''):
    outData = {}
    searchElements = ['p', 'ul']
    excludeElements = [
        ['p', {'class':'mw-empty-elt'}],
        ['style', {}],
        ['sup', {}]
        ]
    suffixEcludeLink = ['.svg']

    contentDiv = data.find('div', attrs={'class':'mw-content-ltr mw-parser-output'})
    
    contentDivs = contentDiv.find_all(searchElements, recursive=False)[:10]
    newContentDiv = []
    for div in range(len(contentDivs)):
        for element in excludeElements:
            match = contentDivs[div].find_all(element[0], attrs=element[1])
            if match:
                for element in match:
                    element.decompose()
        else:
            newContentDiv.append(contentDivs[div])

    contentDivs = contentDivs[:2]

    text = ''
    for element in contentDivs:
        text += element.text
    while text.startswith('\n'):
        text = text[1:]
    while text.endswith('\n'):
        text = text[:-1]

    links = {}
    for contentDiv in contentDivs:
        links.update(getLinkData(contentDiv, linkPrefix, suffixEcludeLink))

    outData['text'] = text
    outData['links'] = links
    return outData

def getLinkData(html, linkPrefix: str='', suffixEcludeLink = ['']):
    links = {}

    linkDivs = html.find_all('a')
    for linkDiv in linkDivs:
        try:
            title = linkDiv.text
            href = linkDiv['href']
            if not href.startswith(linkPrefix):
                href = linkPrefix + href
            for suffix in suffixEcludeLink:
                if href.endswith(suffix):
                    break
            else:
                links[title] = href
        except:
            print(f'Error with {linkDiv}')

    return links

if __name__ == "__main__":
    main()


# Deprecated
def previousScrapper(data: str):
    divToExclude = ['style', 'div']
    htmlElement = ['p', 'li', 'b', 'ul']
    startIndex = data.find('<div class="mw-content-ltr mw-parser-output"')
    clampedData = data[startIndex:]
    subDiv :str = regex.findall(pattern='.+</.+>', string=clampedData)

    parsedHtml :list[str] = []
    for div in subDiv:
        if div.startswith('<') and not div.startswith('<!') and not div.startswith('</'):
            for j in divToExclude:
                if div.startswith('<'+j):
                    break
            else:
                parsedHtml.append(div)
        else:
            break
    
    for div in parsedHtml:
        if div.startswith('<{linkElement}>'):
            print(div+'\n')
        else:
            for j in htmlElement:
                div = div.replace(f'<{j}>', '').replace(f'</{j}>', '')
            text += div

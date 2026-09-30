"""Step 1 - the crawler.

Start from a seed page, download it, pull out every link, and keep going
breadth-first until we have enough pages. Pages go to data/pages.jsonl.

    python crawl.py                      # 500 English Wikipedia pages
    python crawl.py --max 2000 --seed https://en.wikipedia.org/wiki/Physics
"""
import argparse, json, os, time
import urllib.request, urllib.robotparser
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag, urlparse

AGENT = 'tinysearch-tutorial/1.0 (educational crawler)'


class PageParser(HTMLParser):
    """Keeps a page's title, its main text, and its links."""
    # code and menus are not content
    SKIP = {'script', 'style', 'noscript', 'nav', 'header', 'footer'}

    def __init__(self):
        super().__init__()
        self.title, self.text, self.main_text = '', [], []
        self.links, self.canonical = [], None
        self.skipping, self.in_title, self.in_main = 0, False, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP: self.skipping += 1
        if tag == 'main': self.in_main += 1
        if tag == 'title': self.in_title = True
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href')     # the page's true address

    def handle_endtag(self, tag):
        if tag in self.SKIP: self.skipping = max(0, self.skipping - 1)
        if tag == 'main': self.in_main -= 1
        if tag == 'title': self.in_title = False

    def handle_data(self, data):
        if self.in_title: self.title += data
        elif not self.skipping:
            self.text.append(data)
            if self.in_main: self.main_text.append(data)


def fetch(url, html_only=True):
    """Download a URL. Returns (address after redirects, text)."""
    req = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(req, timeout=10) as r:
        kind = r.headers.get('Content-Type', '')
        if html_only and 'text/html' not in kind: return r.geturl(), None
        return r.geturl(), r.read().decode('utf-8', errors='replace')


robots = {}                                   # one robots.txt per site

def polite(url):
    """Does the site's robots.txt allow us to fetch this URL?"""
    site = '{0.scheme}://{0.netloc}'.format(urlparse(url))
    if site not in robots:
        robots[site] = rp = urllib.robotparser.RobotFileParser()
        try: rp.parse(fetch(site + '/robots.txt', False)[1].splitlines())
        except Exception: rp.parse([])        # no robots.txt: all allowed
    return robots[site].can_fetch(AGENT, url)


def wiki_article(url):
    """Stay on English Wikipedia articles (no Talk:, File:, ... pages)."""
    u = urlparse(url)
    return (u.netloc == 'en.wikipedia.org' and u.path.startswith('/wiki/')
            and ':' not in u.path[6:] and u.path != '/wiki/Main_Page')


def crawl(seeds, max_pages=500, delay=0.5, allowed=wiki_article,
          out='data/pages.jsonl'):
    frontier = deque(seeds)      # pages we know about but have not visited
    seen = set(seeds)            # every URL we ever queued
    done = set()                 # true addresses of the pages we saved
    saved, t0 = 0, time.time()
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w') as f:
        while frontier and saved < max_pages:
            url = frontier.popleft()          # breadth first: oldest first
            if not polite(url): continue
            try: final, html = fetch(url)
            except Exception as e: print('  skip', url, e); continue
            if html is None: continue
            p = PageParser(); p.feed(html)
            final = urldefrag(urljoin(final, p.canonical or final))[0]
            if final in done: continue        # a redirect to a saved page
            done.add(final); seen.add(final)
            links = []
            for href in p.links:
                link = urldefrag(urljoin(final, href))[0]   # absolute, no #
                if not allowed(link): continue
                links.append(link)
                if link not in seen:
                    seen.add(link); frontier.append(link)
            text = ' '.join(' '.join(p.main_text or p.text).split())
            page = {'url': final, 'title': p.title.strip(), 'text': text,
                    'aliases': [url] if url != final else [],
                    'links': sorted(set(links))}
            f.write(json.dumps(page) + '\n')
            saved += 1
            print(f'{saved:4d}  queue {len(frontier):6d}  {url}')
            time.sleep(delay)            # be polite: never hammer a server
    took = time.time() - t0
    print(f'crawled {saved} pages in {took:.0f} s, '
          f'discovered {len(seen)} URLs')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', action='append', default=None)
    ap.add_argument('--max', type=int, default=500)
    ap.add_argument('--delay', type=float, default=0.5)
    ap.add_argument('--out', default='data/pages.jsonl')
    a = ap.parse_args()
    seeds = a.seed or ['https://en.wikipedia.org/wiki/Search_engine']
    crawl(seeds, a.max, a.delay, out=a.out)

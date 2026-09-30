"""Step 6 - a search page in your browser.

    python server.py            # then open http://localhost:8000
"""
import html, re, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from search import Engine

STYLE = '''body { font: 16px/1.5 Georgia, serif; max-width: 720px;
  margin: 40px auto; padding: 0 16px; background: #f7f3ea; color: #222 }
h1 { font-size: 44px; margin: 0 0 16px } h1 a { color: #222 }
input { font: inherit; width: 70%; padding: 8px 12px; border-radius: 22px }
.r { margin: 22px 0 } .r a { font-size: 19px } .u { color: #3b7a3b }
.s { color: #444; font-size: 14px } .t { color: #888; font-size: 13px }'''
FORM = '<form><input name="q" value="{}" autofocus> <button>Search</button>'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query).get('q', [''])[0]
        out = [f'<title>tinysearch</title><style>{STYLE}</style>',
               '<h1><a href="/">tinysearch</a></h1>',
               FORM.format(html.escape(q))]
        if q:
            t0 = time.time()
            results = engine.search(q)
            ms = (time.time() - t0) * 1000
            out.append(f'<p class=t>{len(results)} results in {ms:.0f} ms')
            for score, page, snip in results:
                url = html.escape(page['url'])
                title = html.escape(page['title'].split(' - ')[0])
                snip = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>',
                              html.escape(snip))       # **word** -> bold
                out.append(f'<div class=r><a href="{url}">{title}</a>'
                           f'<div class=u>{url}</div>'
                           f'<div class=s>...{snip}...</div></div>')
        body = '\n'.join(out).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass     # keep the terminal quiet


if __name__ == '__main__':
    engine = Engine()
    print('open http://localhost:8000')
    HTTPServer(('localhost', 8000), Handler).serve_forever()

"""Step 5 - the search engine: index, rank, and show snippets.

    python search.py "web crawler" "pagerank"
"""
import math, string, sys, time
from index import build_index, load_pages, tokenize
from rank import bm25, link_graph, pagerank

IMPORTANCE = 0.25      # how much PageRank counts next to BM25 (tuned by hand)


class Engine:
    def __init__(self, path='data/pages.jsonl'):
        t0 = time.time()
        self.pages = load_pages(path)
        self.index, self.lengths = build_index(self.pages)
        self.pr = pagerank(link_graph(self.pages))
        print(f'ready: {len(self.pages)} pages, {len(self.index):,} words '
              f'in {time.time() - t0:.1f} s')

    def search(self, query, k=10):
        words = tokenize(query)
        if not words: return []
        # AND: only pages that contain every word (shortest list first)
        lists = sorted((set(self.index.get(w, {})) for w in words), key=len)
        hits = set.intersection(*lists)
        scores = bm25(words, self.index, self.lengths)
        n = len(self.pages)
        # relevance + a little importance
        final = {d: scores[d] + IMPORTANCE * math.log(self.pr[d] * n)
                 for d in hits}
        top = sorted(final, key=final.get, reverse=True)[:k]
        return [(final[d], self.pages[d], self.snippet(d, words))
                for d in top]

    def snippet(self, doc, words, width=30):
        """The 30-word window with the most query words in it."""
        text = self.pages[doc]['text'].split()
        low = [t.strip(string.punctuation).lower() for t in text]
        hit = [t in words for t in low]
        run = best_run = sum(hit[:width]); best = 0
        for i in range(1, max(1, len(text) - width)):   # slide one word
            run += hit[i + width - 1] - hit[i - 1]
            if run > best_run: best, best_run = i, run
        return ' '.join(f'**{t}**' if low[best + j] in words else t
                        for j, t in enumerate(text[best:best + width]))


if __name__ == '__main__':
    engine = Engine()
    for q in sys.argv[1:] or ['web crawler']:
        t0 = time.time()
        results = engine.search(q)
        ms = (time.time() - t0) * 1000
        print(f'\n"{q}": {len(results)} results in {ms:.1f} ms')
        for score, page, snip in results[:5]:
            print(f'  {score:6.2f}  {page["title"].split(" - ")[0]}')
            print(f'          {page["url"]}\n          ...{snip}...')

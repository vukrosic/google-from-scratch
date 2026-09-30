"""Steps 3 and 4 - ranking.

BM25 answers "how well does this page match the words I typed?"
PageRank answers "how important is this page, judging by its links?"
"""
import math


def bm25(query_words, index, lengths, k1=1.5, b=0.75):
    """Score every page that contains at least one query word."""
    N, avg = len(lengths), sum(lengths) / len(lengths)
    scores = {}
    for word in query_words:
        pages = index.get(word, {})
        if not pages: continue
        # 1. rare words are worth more
        idf = math.log(1 + (N - len(pages) + 0.5) / (len(pages) + 0.5))
        for doc, tf in pages.items():
            # 3. long pages need more hits
            norm = 1 - b + b * lengths[doc] / avg
            # 2. repeats saturate
            s = idf * tf * (k1 + 1) / (tf + k1 * norm)
            scores[doc] = scores.get(doc, 0) + s
    return scores


def link_graph(pages):
    """page id -> ids of the crawled pages it links to."""
    id_of = {}
    for i, p in enumerate(pages):
        for url in [p['url']] + p.get('aliases', []): id_of[url] = i
    # links to pages we never crawled are dropped
    return [sorted({id_of[u] for u in p['links'] if u in id_of} - {i})
            for i, p in enumerate(pages)]


def pagerank(graph, d=0.85, iters=50):
    """The random surfer: follow a link with probability d,
    jump to a random page otherwise."""
    n = len(graph)
    pr = [1 / n] * n                  # start: every page equally important
    for _ in range(iters):
        new = [(1 - d) / n] * n       # random jumps land everywhere
        # pages with no links out: the surfer is stuck and jumps anywhere
        stuck = sum(pr[i] for i in range(n) if not graph[i])
        for i, outs in enumerate(graph):
            for j in outs:
                new[j] += d * pr[i] / len(outs)   # split the vote
        pr = [x + d * stuck / n for x in new]
    return pr


if __name__ == '__main__':
    import time
    from index import load_pages
    pages = load_pages()
    graph = link_graph(pages)
    t0 = time.time()
    pr = pagerank(graph)
    took = time.time() - t0
    print(f'{sum(map(len, graph)):,} links between {len(pages)} pages, '
          f'PageRank in {took:.2f} s, sum = {sum(pr):.4f}')
    for i in sorted(range(len(pages)), key=lambda i: -pr[i])[:10]:
        print(f'{pr[i]:.4f}  {pages[i]["title"].split(" - ")[0]}')

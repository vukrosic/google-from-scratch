# Build Google From Scratch

A working web search engine in 286 lines of plain Python (349 with comments and blank lines) (standard library only, no `pip install`).
It crawls 400 Wikipedia pages, builds an inverted index, ranks results with BM25 and PageRank,
and serves a search page in your browser. Queries take 4–15 ms on a laptop.

Companion code for the video: **Build Google From Scratch** (link coming soon).

## Run it

```bash
python crawl.py --max 400      # ~7 minutes, polite: 0.5 s between requests, obeys robots.txt
python index.py                # index stats
python rank.py                 # PageRank top 10
python search.py "web crawler" "pagerank"
python server.py               # open http://localhost:8000
```

Python 3.8+. The crawl writes `data/pages.jsonl` (~19 MB). Crawl a different topic with
`python crawl.py --seed https://en.wikipedia.org/wiki/Physics`.

## The course, file by file

| Step | File | What it does |
| --- | --- | --- |
| 1. Crawler | `crawl.py` | Breadth-first crawl from a seed page: a frontier queue, a `seen` set, robots.txt, a politeness delay, redirects and canonical URLs, main-content text extraction. |
| 2. Inverted index | `index.py` | Tokenize (lowercase, split, drop stopwords) and map every word to `{page: count}`. Title words count 3×. |
| 3. BM25 | `rank.py` | Relevance: rare words are worth more (idf), repeats saturate (k1 = 1.5), long pages are normalized (b = 0.75). |
| 4. PageRank | `rank.py` | Importance from links: the random-surfer model, power iteration, damping 0.85, pages with no links out. |
| 5. Search | `search.py` | AND the posting lists, score = BM25 + 0.25 · ln(PageRank · N), best 30-word snippet. |
| 6. Web page | `server.py` | A search box and results page with `http.server`. |

## What we measured (400 pages)

- Crawl: 400 pages in 447 s, 53,947 URLs discovered.
- Index: 1,489,000 words, 79,985 unique words, 525,178 postings, built in 0.43 s.
- PageRank: 12,505 links, 50 iterations in 0.02 s.
- Looking up a word: scanning every page takes 237 ms; the index takes 0.03 microseconds.

## What real search engines add

Billions of pages spread across thousands of machines, index compression, spam and duplicate detection,
spelling correction, phrase and proximity matching, freshness, and learned ranking models trained on clicks.
The core ideas here — crawl, invert, score relevance, score importance — are the same ones in the
1998 paper *The Anatomy of a Large-Scale Hypertextual Web Search Engine* (Brin & Page).

MIT License, see `LICENSE`.

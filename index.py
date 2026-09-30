"""Step 2 - the inverted index.

A book index maps a word to the pages it appears on. We build exactly that
for every word on every crawled page:  word -> {page_id: times it appears}
"""
import json, re
from collections import Counter, defaultdict

# words so common they tell us nothing about a page
STOP = set('''a an and are as at be but by for from had has have he her
his i if in into is it its of on or she so than that the their them then
there these they this to was we were which who will with you your not no
can also'''.split())


def tokenize(text):
    """'The Web Crawler, 1994!' -> ['web', 'crawler', '1994']"""
    return [w for w in re.findall(r'[a-z0-9]+', text.lower())
            if w not in STOP]


def load_pages(path='data/pages.jsonl'):
    return [json.loads(line) for line in open(path)]


def build_index(pages, title_weight=3):
    """Returns the inverted index and the length of every page."""
    index = defaultdict(dict)                 # word -> {page_id: count}
    lengths = []
    for doc_id, page in enumerate(pages):
        words = tokenize(page['text'])
        words += tokenize(page['title']) * title_weight   # titles count 3x
        for word, count in Counter(words).items():
            index[word][doc_id] = count
        lengths.append(len(words))
    return index, lengths


if __name__ == '__main__':
    import time
    pages = load_pages()
    t0 = time.time()
    index, lengths = build_index(pages)
    took = time.time() - t0
    postings = sum(len(p) for p in index.values())
    print(f'{len(pages)} pages, {sum(lengths):,} words, '
          f'{len(index):,} unique words, {postings:,} postings, '
          f'built in {took:.2f} s')
    for w in ['pagerank', 'crawler', 'google']:
        top = sorted(index[w].items(), key=lambda x: -x[1])[:3]
        names = ', '.join(f'{pages[d]["title"].split(" - ")[0]} ({c})'
                          for d, c in top)
        print(f'{w!r}: in {len(index[w])} pages; most: {names}')

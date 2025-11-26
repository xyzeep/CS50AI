import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
                link for link in pages[filename]
                if link in pages
                )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # total no. of pages in corpus
    N = len(corpus)

    # number of outgoing links from given page
    outgoing_links = corpus[page]
    L = len(outgoing_links)

    prob_distribution = {}


    # if the page has outgoing links
    if L != 0:

        # set the initial probability the same for all pages
        prob_distribution = {key: (1 - damping_factor) / N for key in corpus}

        # calculating link based amount and adding to initial prov_distribution
        link_based_amount = damping_factor / L

        for each in outgoing_links:
            prob_distribution[each] += link_based_amount

    # if it doesn't link to any pages
    else:
        prob_distribution = {key: (1) / N for key in corpus}
            
    return prob_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    first_sample = random.choice(list(corpus.keys()))
    
    sample = first_sample

    all_samples = [sample,]

    for i in range(n - 1):
        trans_possibilities = transition_model(corpus, sample, damping_factor)
        sample = random.choices(population = list(trans_possibilities.keys()), weights = list(trans_possibilities.values()), k = 1)[0]

        all_samples.append(sample)
    
    # count how many time each page appears in the samples
    counts = {}
    for page in all_samples:
        if page in counts:
            counts[page] += 1
        else:
            counts[page] = 1

    pages_rank = {key: value / n for key, value in counts.items()}

    return pages_rank


def iterate_pagerank(corpus, damping_factor):
    """
    return pagerank values for each page by iteratively updating
pagerank values until convergence.

    return a dictionary where keys are page names, and values are
their estimated pagerank value (a value between 0 and 1). all
    pagerank values should sum to 1.
    """
    # total no. of pages in corpus
    N = len(corpus)
    pages_rank = {} 
    
    # assigning each page a rank of 1 / n
    pages_rank = {page: 1 / N for page in list(corpus.keys())}

    new_ranks = {}

    converged = False
    while not converged:
        converged = True
        for p in list(corpus.keys()):
            new_ranks[p] = (1 - damping_factor) / N
            for q in list(corpus.keys()):
                pages_linked_in_q = list(corpus[q])

                # if q links to p
                if p in pages_linked_in_q:
                    new_ranks[p] += damping_factor * (pages_rank[q] / len(corpus[q]))
                
                # if q links to no pages, we assume it links to all pages (including p)
                elif len(pages_linked_in_q) == 0:
                    new_ranks[p] += damping_factor * (pages_rank[q] / N)
                
            # abs difference between new rank ond old rank
            difference = abs(new_ranks[p] - pages_rank[p])

            if difference > 0.001:
                converged = False

        # update pages_rank to new ranks of the pages
        pages_rank = new_ranks.copy()

    return pages_rank

if __name__ == "__main__":
    main()

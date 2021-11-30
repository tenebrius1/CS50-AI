import os
import random
import re
import sys
import copy

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
    probability = dict()

    # If page has no outgoing links, returns a probability distribution that chooses randomly among all pages with equal probability
    if not corpus[page]:
        for link in corpus:
            probability[link] = 1/len(corpus)
        return probability

    # Goes through all links in the page and assigns them a probability of (0.85 / # of links in the page)
    for link in corpus[page]:
        probability[link] = DAMPING / len(corpus[page])

    # Goes though each link in the corpus and adds a probability of (o.15 / # of links in corpus) to each link
    for link in corpus:

        # If link is already present in probability distribution, add to it
        if link in probability:
            probability[link] += (1 - DAMPING) / len(corpus)

        # If link is not already present in probability, create a new key-value pair for it
        else:
            probability[link] = (1 - DAMPING) / len(corpus)

    return probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageRank = dict()
    frequency = dict()

    # Sample states randomly for n times
    for i in range(n):
        # Chooses a page at random for first sample
        if i == 0:
            key = random.choice(list(corpus))
            frequency[key] = 1

        else:
            chances = []
            links = []
            probability = transition_model(corpus, key, damping_factor)
            for link in corpus:
                links.append(link)
                chances.append(probability[link])
            # Get a random link
            random_link = random.choices(links, chances)

            # If the random link is already in the frequency table, add one to it
            if random_link[0] in frequency.keys():
                frequency[random_link[0]] += 1

            # If random link is not already in the frequency table, initialize it at 1
            else:
                frequency[random_link[0]] = 1

            # Logs the current link for the next iteration
            key = random_link[0]

    for link in corpus:
        pageRank[link] = (frequency[link] / n)

    return pageRank


def new_pagerank(d, N, currentPageRank, links):
    """
    Returns a new pagerank value using the formula based on the previous PageRank values.
    """
    summation = []
    for page in links:
        summation.append(currentPageRank[page] / links[page])

    return (((1 - d)) / N + (d * (sum(summation))))


def check_accuracy(pageRank1, pageRank2):
    for page in pageRank1:
        if abs(pageRank1[page] - pageRank2[page]) > 0.00001:
            return False

    return True


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageRank = dict()
    copy_pageRank = dict()
    accurate = False

    # Initializes the dictionary with assigning each page a rank of 1 / N
    for link in corpus:
        pageRank[link] = 1 / len(corpus)
        copy_pageRank = copy.deepcopy(pageRank)

    # Using formular, calculate new pagerank for each page until value converge
    while not accurate:
        for page in pageRank:
            links_to_page = dict()
            for link in corpus:
                if page in corpus[link]:
                    links_to_page[link] = len(corpus[link])
            pageRank[page] = (new_pagerank(
                DAMPING, len(corpus), pageRank, links_to_page))

        accurate = check_accuracy(pageRank, copy_pageRank)
        copy_pageRank = copy.deepcopy(pageRank)

    for page in pageRank:
        pageRank[page] = pageRank[page]
    return pageRank


if __name__ == "__main__":
    main()

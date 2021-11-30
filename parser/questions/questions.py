import os
import string
import sys

import nltk

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {filename: tokenize(files[filename]) for filename in files}
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()

    for file in os.listdir(directory):
        f = open(f"{directory}/{file}", "r", encoding="utf8")
        txt = f.read()
        files[file] = txt

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    from nltk.corpus import stopwords

    # * Custom list of words/punctuations to filter out
    filter_out = ["''", "``", "'s", "====", "p", "b"]
    # * Splits text into individual words
    word_tokens = nltk.word_tokenize(document)
    # * List of stop words from nltk stopword library
    stop_words = set(stopwords.words("english"))
    # * Filters out punctuations, words that listed above
    words = [
        word.lower()
        for word in word_tokens
        if word not in stop_words
        and word not in string.punctuation
        and word not in filter_out
    ]

    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    from math import log

    num_of_docs = len(documents)
    words_frequency = dict()
    idf = dict()

    for document in documents:
        for word in documents[document]:
            if word not in words_frequency:
                words_frequency[word] = [document]
            else:
                if document in words_frequency[word]:
                    continue
                else:
                    words_frequency[word].append(document)

    for word in words_frequency:
        if word not in idf:
            idf[word] = log((num_of_docs / len(words_frequency[word])))

    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    top_list = list()

    # * Calculates the term frequency of words in each file
    frequency_map = dict()
    for file in files:
        frequencies = dict()
        for word in files[file]:
            if word in frequencies:
                frequencies[word] += 1
            else:
                frequencies[word] = 1

        frequency_map[file] = frequencies

    # * Calculates the tfidf of words
    tfidfs = dict()
    for file in files:
        tfidfs[file] = dict()
        for word in frequency_map[file]:
            tf = frequency_map[file][word]
            tfidfs[file][word] = tf * idfs[word]

    tfidfs_rank = dict()
    for word in query:
        for file in tfidfs:
            if word in tfidfs[file]:
                if file not in tfidfs_rank:
                    tfidfs_rank[file] = tfidfs[file][word]
                else:
                    tfidfs_rank[file] += tfidfs[file][word]

    sorted_tfidfs_rank = sorted(tfidfs_rank.items(), key=lambda x: x[1], reverse=True)

    for file in sorted_tfidfs_rank:
        top_list.append(file[0])

    return top_list[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    top_list = list()

    idfs_rank = dict()
    for word in query:
        for sentence in sentences:
            if word in sentences[sentence] and word in idfs:
                if sentence not in idfs_rank:
                    idfs_rank[sentence] = idfs[word]
                else:
                    idfs_rank[sentence] += idfs[word]

    sorted_idfs_rank = sorted(idfs_rank.items(), key=lambda x: x[1], reverse=True)

    if idfs_rank[sorted_idfs_rank[0][0]] == idfs_rank[sorted_idfs_rank[1][0]]:
        rank = dict()
        for sentence in sorted_idfs_rank:
            if sentence[1] == sorted_idfs_rank[0][1]:
                rank[sentence[0]] = 0
        for sentence in rank:
            length_of_sentence = len(sentence.split())
            for word in query:
                word_frequency = sentence.split().count(word)
                rank[sentence] += word_frequency / length_of_sentence

        sorted_idfs_rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)

    for sentence in sorted_idfs_rank:
        top_list.append(sentence[0])

    return top_list[:n]


if __name__ == "__main__":
    main()

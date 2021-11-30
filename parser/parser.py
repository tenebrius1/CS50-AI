import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S P S
NP -> N | Det N | Det Adj N | NP P NP | Det AdjP N
VP -> V | V NP | VP P NP | Adv V | V P NP Adv | VP NP | V AdvP | VP Conj VP | V Adv
AdvP -> P NP Adv | Adv
AdjP -> Adj | Adj AdjP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # * Tokenizes words in a sentence
    words = nltk.word_tokenize(sentence)
    # * Ensures all words are in lowercase
    processed_words = [word.lower() for word in words if word.isalpha()]

    return processed_words

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # * Initializes a list to store all NP chunks
    np_chunks = list()
    
    for subtree in tree.subtrees(lambda t: t.height() < tree.height()):
        temp = list()
        if subtree.label() == 'NP':
            for subs in subtree.subtrees(lambda t: t.height() < subtree.height()):
                temp.append(subs.label())

            if 'NP' not in temp:
                np_chunks.append(subtree)
        

    return np_chunks


if __name__ == "__main__":
    main()

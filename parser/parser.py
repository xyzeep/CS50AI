import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S

NP -> N | Det N
NP -> Det Adjp N
NP -> NP PP
Adjp -> Adj | Adj Adjp

VP -> V | V NP | V PP
VP -> V NP PP
VP -> Adv VP
VP -> VP Adv
VP -> VP Conj VP

PP -> P NP
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
    # separate the words/tokens in the sentence using nltk
    tokens = nltk.word_tokenize(sentence)
    words = []
    for word in tokens:
        # if the word is not alpha, or is a number or special character, skip
        if not word.isalpha():
            continue
        words.append(word.lower())
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunks = []
    subtrees = tree.subtrees()
    # for each subtree in tree check if it is labeled as a noun phrase
    for subtree in subtrees:
        if subtree.label() == "NP":
            valid = True
            # and if it is a NP, check if it contains other NP inside it
            for each in list(subtree.subtrees())[1:]:
                # if subsubtree contains a NP inside it, the subtree is not a valid np_chunk:w
                if each.label() == "NP":
                    valid = False
            if valid:
                np_chunks.append(subtree)

    return np_chunks


if __name__ == "__main__":
    main()


import json


WORDS_FILE = "data/words.txt"

class Node:
    def __init__(self, word, results):
        self.word = word
        # a dictionary of possible results to 'next words to guess'
        self.results = results

    def to_json(self, results="....."):
        root = {"guess" : self.word, "results" : results, "children" : []}
        for k, v in self.results.items():
            root["children"].append(v.to_json(k))

        return root

def get_result(guess, candidate):
    result = ""
    for i in range(5):
        if guess[i] == candidate[i]:
            result += "g"
        elif guess[i] in candidate:
            result += "y"
        else:
            result += "."

    return result

def compute_gini_impurity(vector):
    # gini impurity is a measurement of the likelihood of 
    # an incorrect classification of a sample from a random
    # variable if we were to randomly classify it.

    # if we maximize this metric then we eliminate most of the search space
    gini_impurity = 0.0

    for i in range(len(vector)):
        p = vector[i] / sum(vector)
        gini_impurity += p*p

    return 1 - gini_impurity


def get_best_guess(words, candidates):
    if len(candidates) == 1:
        remaining = candidates[0]
        return remaining

    max_gini_impurity = 0
    best_guess = ""

    for guess in words:
        # for a fixed word (treat this as the hypthetical solution), iterate over all possible guesses
        # and form a map of results to words e.g. the words that produce "22222" for starting word abhor is abhor etc
        results = {}
        for candidate in candidates:
            result = get_result(guess, candidate)
            if not result in results.keys():
                results[result] = [candidate]
            else:
                results[result].append(candidate)

        # replace best guess if there's a word with better gini impurity. we aim to maximize the gini impurity 
        # of our guess so we can narrow down the potential solutions as much as possible => minimizing the number of guesses
        new_gini_impurity = compute_gini_impurity([len(results_list) for results_list in results.values()])
        if new_gini_impurity > max_gini_impurity:
            max_gini_impurity = new_gini_impurity
            best_guess = guess

    return best_guess

def generate_tree(words, candidates):
    first_guess = get_best_guess(words, candidates)
    root = Node(first_guess, {})

    for candidate in candidates:
        print(f"candidate is {candidate}:", end="")

        temp_list = candidates
        guess = root
        print(f"{guess.word} -> ", end="")

        # explore the tree, going as far down as we can until we reach the bottom
        result = get_result(guess.word, candidate)
        while result in guess.results:
            temp_list = list(filter(lambda a : get_result(guess.word, a) == result, temp_list))
            guess = guess.results[result]
            print(f"{guess.word} -> ", end="")
            result = get_result(guess.word, candidate)

        while result != "ggggg":
            # at this point, we haven't correctly guessed the candidate so we begin building out the tree
            # by using the resulting best guess and the previous result

            # get a list containing all candidates that would produce the result m
            temp_list = list(filter(lambda a : get_result(guess.word, a) == result, temp_list))

            # choose the best guess from this list and add in m to the results map 
            # i.e. this guess.results[m] tells us what the next best guess is for a given m
            best_guess = get_best_guess(words, temp_list)
            guess.results[result] = Node(best_guess, {})

            # now repeat for using guess = best_guess
            guess = guess.results[result]
            print(f"{guess.word} -> ", end="")

            result = get_result(guess.word, candidate)
        
        # we have now correctly guessed the candidate
        print("DONE")

    # at this point we have generated the tree that tells us what the best move is at each step 
    # for a fixed starting word, the word with the greatest overall gini impurity 

    return root

def main():
    with open(WORDS_FILE, "r") as f:
        words = f.read().split("\n")

    words = [ word for word in words if not word is "" ]
    candidates = words
    
    dt = generate_tree(words, candidates)
    dt_json = json.dumps(dt.to_json())
    with open("data/tree.json", "w") as f:
        f.write(dt_json) 

if __name__ == "__main__":
    main()
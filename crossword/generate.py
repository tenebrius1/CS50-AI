import sys
import copy

from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # * Make a deepcopy of domains
        domains_copy = copy.deepcopy(self.domains)

        # * Loop through every variable in domains
        for variable in domains_copy:
            # * Loop through every word in variable
            for word in domains_copy[variable]:
                # * Checks whether length of word is greater than the variable length
                if len(word) != variable.length:
                    # * If it is, delete word from the current variable words
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # * Finds out the intersection between x and y
        i, j = self.crossword.overlaps[(x, y)]

        # * Makes a copy of domain
        domains_copy = copy.deepcopy(self.domains)

        # * Sets the inital value of revised to be False
        revised = False

        # * Gets the words of x and y
        x_words = domains_copy[x]
        y_words = domains_copy[y]

        # * Loops through all words in x and y
        for word1 in x_words:
            clash = list()
            for word2 in y_words:
                if word1 == word2:
                    continue
                elif word1[i] != word2[j]:
                    clash.append(word2)
            # * Removes the word from x if it is not arc consistent with y and sets revised to True
            if len(clash) == len(y_words):
                self.domains[x].remove(word1)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # * Make a deepcopy of domain
        domains_copy = copy.deepcopy(self.domains)

        if arcs:
            while len(arcs) != 0:
                x, y = arcs[0]
                arcs = arcs[1:]
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        return False
                    for neighbor in self.crossword.neighbors(x):
                        if neighbor != y:
                            arcs.append((neighbor, x))

            return True

        # * Initialize a list to contain all the arcs
        arcs = []

        # * Loops over all variable in domain adds are arcs to a queue
        for variable in domains_copy:
            overlaps = self.crossword.neighbors(variable)
            for overlap in overlaps:
                arcs.append((variable, overlap))

        # * Calls revise all arcs
        while len(arcs) != 0:
            x, y = arcs[0]
            arcs = arcs[1:]
            if self.revise(x, y):
                # * If x is revised and x is empty after revision, return false
                if len(self.domains[x]) == 0:
                    return False
                # * Adds neighbors of x back to the queue to check whether they are still are consistent after x is revised
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        arcs.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.domains):
            return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in self.domains:
            # * Only considers assigned variables
            if variable not in assignment:
                continue

            # * Checks whether the assigned word is of the correct length
            if len(assignment[variable]) != variable.length:
                return False

            # * Gets neighbors for current variable
            arcs = self.crossword.neighbors(variable)

            # * Loops through each neighbor
            for neighbor in arcs:
                if neighbor not in assignment:
                    continue
                # * Checks if all values are distinct
                if assignment[variable] == assignment[neighbor]:
                    return False

                # * Checks whether there is a conflict
                i, j = self.crossword.overlaps[(variable, neighbor)]
                if assignment[variable][i] != assignment[neighbor][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = list()
        for word in assignment[var]:
            values.append(word)

        return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = list()
        for var in self.domains:
            if var in assignment:
                continue
            num_neighbors = len(self.crossword.neighbors(var))
            variables.append((len(self.domains[var]), num_neighbors, var))

        sorted_variables = sorted(variables, key=lambda var: var[0])
        if len(sorted_variables) > 1:
            if sorted_variables[0][0] == sorted_variables[1][0]:
                sorted_variables = sorted(variables, key=lambda var:var[1], reverse=True)
            
        variable = sorted_variables[0][2]
        if variable not in assignment:
            return variable

    def inference(self, var):
        """
        Returns a dictionary of {var: value} by calling ac3 when doing 
        backtrack search.
        """
        inferences = dict()
        
        neighbours = self.crossword.neighbors(var)
        arcs = []
        for neighbour in neighbours:
            arcs.append((neighbour, var))
        if self.ac3(arcs=arcs):
            for v in self.domains:
                if len(self.domains[v]) == 1:
                    inferences[v] = self.domains[v].pop()

        return inferences

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # * Checks if the assignment is already complete and return the assignment if it is
        if self.assignment_complete(assignment):
            return assignment

        # * Gets a random unassigned variable
        var = self.select_unassigned_variable(assignment)

        domain_copy = copy.deepcopy(self.domains)

        # * Loops through all values var can take
        for word in domain_copy[var]:
            assignment[var] = word
            self.domains[var] = {word}
            inferences = self.inference(var)
            if len(inferences) > 0:
                for variable in inferences:
                    assignment[variable] = inferences[variable]
            # * Checks if current assignment is still consistent
            if self.consistent(assignment):
                # * Checks whether the assignment fails at any point in the future by recursively calling backtrack
                result = self.backtrack(assignment)
                # * If nothing fails then return the result
                if result != None:
                    return result
            # * If {var = word} fails, removes it from assignment
            del assignment[var]
            for variable in inferences:
                if variable in assignment:
                    del assignment[variable]

        # * If no assignment works, return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
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
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
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

        for var in self.domains:
            self.domains[var] = {val for val in self.domains[var] if len(val) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False
        overlap = self.crossword.overlaps[x, y]
        
        # if there is no overlap, no need to revise
        if overlap is None: return revised
        
        # but if there is overlap
        x_index, y_index = overlap
        remove_set = set()
        
        # check if each value for variable x has at least one value for variable y that satisfies their binary constraint
        for val_x in self.domains[x]:
            
            # to keep track if it is consistent
            consistent = False
            for val_y in self.domains[y]:
                if val_x[x_index]  == val_y[y_index]:
                    consistent = True # if there exists such value for y, then they are arc consistent
                    break
                
            if not consistent:
                remove_set.add(val_x) # if not consistent, add to removing set
        
        # remove values from x's domain, if any, and mark revised as true
        if remove_set:
            self.domains[x] -= remove_set
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
        if arcs == None:
            queue = list(self.crossword.overlaps.keys())
        else:
            queue = arcs
        
        for x, y in queue:
            revised = self.revise(x, y)
            if revised:
                if len(self.domains[x]) == 0:
                    return False

                for z in self.crossword.neighbors(x):
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        for var in self.crossword.variables:
            if var not in assignment:
                return False

        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # checking word length
        for var, val in assignment.items():
            if len(val) != var.length:
                return False

        # check if there are word(s) assigned to more than one variable
        if len(assignment.values()) > len(set(assignment.values())):
            return False
        
        # chek if overlapping words have the same letter in the overlapped cell
        for x in assignment:
            for y in assignment:
                if x == y:
                    continue

                overlap = self.crossword.overlaps[x, y]
                if overlap:
                    x_index, y_index = overlap
                    if assignment[x][x_index] != assignment[y][y_index]:
                        return False

        return True
                

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        result = []
        values = self.domains[var]
        neighbors = self.crossword.neighbors(var)

        for x in values:
            # how many values this assignment would eliminate
            score = 0

            for z in neighbors:
                if z not in assignment:
                    i, j = self.crossword.overlaps[var, z]
                    for z_value in self.domains[z]:
                        if x[i] != z_value[j]:
                            score += 1

            result.append((x, score))
        
        sorted_result = sorted(result, key = lambda pair: pair[1])
        
        return [value for value, score in sorted_result]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = [var for var in self.crossword.variables if var not in assignment]

        domain_sizes = {var: len(self.domains[var]) for var in unassigned_variables}

        min_size = min(domain_sizes.values())

        tied_vars = [var for var, size in domain_sizes.items() if size == min_size]
        
        if len(tied_vars) > 1:
            highest_degree_var = max(tied_vars, key = lambda var: len(self.crossword. neighbors(var)))

            return highest_degree_var

        return tied_vars[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.consistent(assignment) and self.assignment_complete(assignment): return assignment
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var, assignment):
            if self.consistent({**assignment, var: value}):
                assignment[var] = value
                
                # forward checking inference
                inferences = {} # store pruned domains
                failure = False

                for neighbor in self.crossword.neighbors(var):
                    if neighbor not in assignment:
                        # remove words form  neighbor that conflicts with var = value
                        removed = set()
                        i, j = self.crossword.overlaps[var, neighbor]
                        for word in self.domains[neighbor]:
                            if value[i] != word[j]:
                                removed.add(word)

                        if removed:
                            self.domains[neighbor] -= removed
                            inferences[neighbor] = removed

                        if not self.domains[neighbor]: # domain clear
                            failure = True
                            break
                
                if not failure:
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
                
                # undo assignment and inferences
                del assignment[var]
                for n_var, removed_words in inferences.items():
                    self.domains[n_var] |= removed_words # restore removed values form the domain


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

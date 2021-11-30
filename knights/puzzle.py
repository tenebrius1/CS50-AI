from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnave, AKnight),  # A is either a Knave or a Knight
    Not(And(AKnave, AKnight)),  # A is not both a Knave and a Knight

    # Check for (A says "I am both a knight and a knave.")
    # If A is a knight, it implies that A is both a Knight and a Knave
    Implication(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnave, AKnight),  # A is either a Knave or a Knight
    Not(And(AKnave, AKnight)),  # A is not both a Knave and a Knight
    Or(BKnave, BKnight),  # B is either a Knave or a Knight
    Not(And(BKnave, BKnight)),  # B is not both a Knave and a Knight

    # Check for (A says "We are both knaves.")
    # If A is a Knave, it implies that A and B are not both Knaves
    Implication(AKnave, Not(And(AKnave, BKnave))),
    # If A is a Knight, it implies that A and B are both Knaves
    Implication(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnave, AKnight),  # A is either a Knave or a Knight
    Not(And(AKnave, AKnight)),  # A is not both a Knave and a Knight
    Or(BKnave, BKnight),  # B is either a Knave or a Knight
    Not(And(BKnave, BKnight)),  # B is not both a Knave and a Knight

    # Check for (A says "We are the same kind.")
    # If A is a Knave, it implies that either A and B are not both Knaves or A and B are not both Knights
    Implication(AKnave, Not(Or(And(AKnave, BKnave), And(AKnight, BKnight)))),
    # If A is a Knight, it implies that either A and B are both Knaves or A and B are both Knights
    Implication(AKnight, Or(And(AKnave, BKnave), And(AKnight, BKnight))),

    # Check for (B says "We are of different kinds.")
    # If B is a Knave, it implies that it is not either A is a Knave and B is not a Knave or A is a Knight and B is not a Knight
    Implication(BKnave, Not(
        Or(And(AKnave, Not(BKnave)), And(AKnight, Not(BKnight))))),
    # If B is a Knight, it implies that either A is a Knave and B is not a Knave or A is a Knight and B is not a Knight
    Implication(BKnight, Or(And(AKnave, Not(BKnave)),
                            And(AKnight, Not(BKnight))))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnave, AKnight),  # A is either a Knave or a Knight
    Not(And(AKnave, AKnight)),  # A is not both a Knave and a Knight
    Or(BKnave, BKnight),  # B is either a Knave or a Knight
    Not(And(BKnave, BKnight)),  # B is not both a Knave and a Knight
    Or(CKnave, CKnight),  # C is either a Knave or a Knight
    Not(And(CKnave, CKnight)),  # C is not both a Knave and a Knight

    # Check for (C says "A is a knight.")
    # If C is a Knight it implies that A is a Knight
    Implication(CKnight, AKnight),
    # If C is a Knave it implies that A is not a Knight
    Implication(CKnave, Not(AKnight)),

    # Check for (B says "C is a knave.")
    # If B is a Knight, it implies that C is a knave
    Implication(BKnight, CKnave),
    # If B is a Knave, it implies that C is not a knave
    Implication(BKnave, Not(CKnave)),

    # Check for (B says "A said 'I am a knave'.")
    # If B is a Knight, either A is a Knight which implies that A is a Knave or A is a Knave which implies A is not a Knave
    Implication(BKnight, Or(Implication(AKnight, AKnave),
                            Implication(AKnave, Not(AKnave)))),
    # If B is a Knave, either A being a Knight does not imply that A is a Knave or A being a Knave does not implies A is not a Knave
    Implication(BKnave, Or(Not(Implication(AKnight, AKnave)),
                           Not(Implication(AKnave, Not(AKnave))))),

    # Check for (A says either "I am a knight." or "I am a knave.", but you don't know which.)
    # If A is a Knight, either A is a Knave or A is a Knight
    Implication(AKnight, Or(AKnave, AKnight)),
    # If A is a Knave, either A is not a Knave or A is not a Knight
    Implication(AKnave, Not(Or(AKnave, AKnight)))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

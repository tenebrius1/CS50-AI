import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_p = 1

    # Iterate through people
    for person in people:
        # If person does not have parents data
        if not people[person]["mother"] and not people[person]["father"]:
            # Initialize temp variable and get number of genes for person
            temp = 1
            if person in one_gene:
                num_genes = 1
            elif person in two_genes:
                num_genes = 2
            else:
                num_genes = 0

            # Gets the probability of having number of genes
            temp *= PROBS["gene"][num_genes]

            # Multiply probability of having trait given number of genes
            if person in have_trait:
                temp *= PROBS["trait"][num_genes][True]
            else:
                temp *= PROBS["trait"][num_genes][False]

        # If parents are in people
        else:
            # Initialize a dictionary for storing the probability of a parent passing down the gene
            parents = {"mother": 1, "father": 1}

            # Initialize a temp variable
            temp = 0

            # Updates the probability of parent passsing down the gene given number of gene parent have
            for parent in parents:
                # If parent is in one_gene, probability of passing down is (1 - mutation chance) * 0.5
                if people[person][parent] in one_gene:
                    parents[parent] *= 0.5
                # If parent is in two_genes, probability of passing down is (1 - mutation chance)
                elif people[person][parent] in two_genes:
                    parents[parent] *= 1 - PROBS["mutation"]
                # If parent has no genes, probability of passing down is mutation chance)
                else:
                    parents[parent] *= PROBS["mutation"]

            # Calculate the probability of the person having 0, 1 or 2 genes
            if person in one_gene:
                num_genes = 1
                temp += parents["mother"] * (1 - parents["father"])
                temp += parents["father"] * (1 - parents["mother"])

            elif person in two_genes:
                num_genes = 2
                temp += parents["mother"] * parents["father"]

            else:
                num_genes = 0
                temp += (1 - parents["mother"]) * (1 - parents["father"])

            # Calculate the probability of person having trait given number of genes
            if person in have_trait:
                temp *= PROBS["trait"][num_genes][True]
            else:
                temp *= PROBS["trait"][num_genes][False]

        joint_p *= temp

    return joint_p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    gene_and_trait = dict()
    for person in probabilities:
        if person in one_gene:
            gene_and_trait[person] = {"gene": 1}

        elif person in two_genes:
            gene_and_trait[person] = {"gene": 2}

        else:
            gene_and_trait[person] = {"gene": 0}

        if person in have_trait:
            gene_and_trait[person].update({"trait": True})
        else:
            gene_and_trait[person].update({"trait": False})

        probabilities[person]["gene"][gene_and_trait[person]["gene"]] += p
        probabilities[person]["trait"][gene_and_trait[person]["trait"]] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        alpha = 0
        temp = 0
        for value in probabilities[person]["gene"].values():
            temp += value
        alpha = 1 / temp

        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= alpha

        alpha = 0
        temp = 0

        for value in probabilities[person]["trait"].values():
            temp += value
        alpha = 1 / temp

        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= alpha


if __name__ == "__main__":
    main()

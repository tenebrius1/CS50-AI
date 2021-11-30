import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import Perceptron
from sklearn.svm import SVC

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def convert_data(row):
    months = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}
    visitorType = {'Returning_Visitor': 1, 'New_Visitor': 0, 'Other': 0}
    weekend = {'TRUE': 1, 'FALSE': 0}
    # * Converts months to their interger format
    row[10] = months[row[10]]
    # * Converts VisitorType to their integer format
    row[15] = visitorType[row[15]]
    # * Converts weekend into their integer format
    row[16] = weekend[row[16]]

    # * Convert string to int
    row[0] = int(row[0])
    row[2] = int(row[2])
    row[4] = int(row[4])
    row[11] = int(row[11])
    row[12] = int(row[12])
    row[13] = int(row[13])
    row[14] = int(row[14])

    # * Convert string to float
    row[1] = float(row[1])
    row[3] = float(row[3])
    row[5] = float(row[5])
    row[6] = float(row[6])
    row[7] = float(row[7])
    row[8] = float(row[8])
    row[9] = float(row[9])

    # * Convert whether user purchase to be an int
    row[17] = weekend[row[17]]

    return row

def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = list()
    label = list()
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            row = convert_data(row)
            evidence.append(row[:-1])
            label.append(row[-1])
        
    return (evidence, label)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivity, specificty, true_postive, true_negative, positive, negative = 0, 0, 0, 0, 0, 0 
    for i in range(len(labels)):
        if labels[i] == 1:
            positive += 1
        if labels[i] == 0:
            negative += 1
        if labels[i] == predictions[i]:
            if labels[i] == 1:
                true_postive += 1
            else:
                true_negative += 1
        
    sensitivity = true_postive/positive
    specificty = true_negative/negative

    return (sensitivity, specificty)


if __name__ == "__main__":
    main()

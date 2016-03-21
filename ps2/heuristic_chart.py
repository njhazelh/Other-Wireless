#! /usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys

def read_lines():
    names = []
    scores = []
    for line in sys.stdin.readlines():
        parts = line.strip().split("\t")
        names.append(parts[0])
        scores.append(float(parts[1]))
    return names, np.array(scores)


def make_chart(names, scores):
    plt.title("Heuristic Performance in Choosing Access Points Cover")
    plt.ylabel("Percent of possible access points chosen")
    plt.xlabel("Heuristics")

    index = np.arange(len(names))

    bar_width = .9

    rects = plt.bar(index, scores * 100, bar_width)
    plt.xticks(index + bar_width / 2, names)

    for r in rects:
        height = r.get_height()
        plt.text(
            r.get_x() + r.get_width() / 2,
            height - 20,
            "%.2f%%" % height,
            color='w',
            ha="center",
            va="bottom")

    plt.show()


def main():
    names, scores = read_lines()
    make_chart(names, scores)


if __name__ == "__main__":
    main()
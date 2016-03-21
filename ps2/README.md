# Wireless Networking: Problem Set 2
This repo contains the code for question 4 of Wireless Networking
Problem Set 2.

## Dependencies
This code relies on numpy and matplotlib.

## Running Code.
Code for this question is divided into the simulation script
and the chart-generation script.  It is expected that these
can be combined using bash IO redirection.

This script will run NUM_SIMULATIONS tests on a space of WIDTH x HEIGHT with access points that
have a range oF AP_RANGE.  The stdout consists of the performance for each heuristic.
```bash
./networking_planning.py [--width WIDTH] [--height HEIGHT] [--range AP_RANGE] [--sims NUM_SIMULATIONS]
```

This script will create a bar chart of the results.  It reads from stdin, which
should be redirected from a file or script using bash.
```bash
./heuristic_char.py
```
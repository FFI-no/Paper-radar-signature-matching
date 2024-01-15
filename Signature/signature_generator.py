import pandas as pd
import numpy as np
import os

max = 88

database_P1_single = list(range(1, max + 1))

database_P1_double = list(range(1, 46))
database_P2_double = list(range(46,max + 1))

database_P1_triple = list(range(1, 31))
database_P2_triple = list(range(31, 61))
database_P3_triple = list(range(61, max + 1))

database_P1_quadruple = list(range(1, 31))
database_P2_quadruple = list(range(31, 61))
database_P3_quadruple = list(range(61, 77))
database_P4_quadruple = list(range(77, max + 1))

def contained(measurement_rf, measurement_pri, mean_rf, mean_pri):
    """
    Checking if measurement is inside rectangular box
    """
    counter = 0
    counter += (measurement_pri <= mean_pri+9400)
    counter += (measurement_pri >= mean_pri-9400)
    counter += (measurement_rf <= mean_rf+30000)
    counter += (measurement_rf >= mean_rf-30000)
    return (counter==4)

def mahalanobis_distance(database, coeff, measurement_rf, measurement_pri):
    """
    Calculates mahalanobis distance through choleskey decomposition,   however we do not perform choleskey decomposition.
    """
    y1 = measurement_pri - database[2]
    y2 = measurement_rf - database[1]

    summand_1 = y1**2 * coeff[0]
    summand_2 = y2**2 * coeff[1]
    summand_3 = -2 * y1 * y2 * coeff[2]

    eta = summand_1 + summand_2 + summand_3

    return eta

sigs = pd.read_csv("syn_sigs.csv", sep=";", decimal=",")
signatures = dict()

for ind in sigs.index:
    cov = np.array([
                [sigs["cov11"][ind], sigs["cov12"][ind]], 
                [sigs["cov21"][ind], sigs["cov22"][ind]]
            ])
    det = cov[0][0] * cov[1][1] - cov[0][1]**2
    signature = {
        "pri": sigs["pri"][ind],
        "rf": sigs["rf"][ind],
        "cov": cov,
        "coeffs": [
                cov[1][1]/det,
                cov[0][0]/det,
                cov[0][1]/det,
            ]
    }
    signatures[sigs["no"][ind]] = signature

samples = dict()
for no, signature in signatures.items():
    print("Sampling", no)
    sample_ok = False
    while not sample_ok:
        sample = list(
                np.round(
                    np.random.default_rng().multivariate_normal(
                        np.array([signature["rf"], signature["pri"]]), 
                        signature["cov"], 
                        size=1, 
                        check_valid="warn"
                    )[0]
                )
            )
        
        possible = []
        for no2, sig2 in signatures.items():
            if contained(sample[0], sample[1], sig2['rf'], sig2['pri']):
                possible.append(no2)

        if len(possible) == 0:
            print("Outeside box", no, sample)
        elif (len(possible) == 1) and (possible[0] == no):
            sample_ok = True
        else:
            matches = []
            for no2 in possible:
                entry = [
                        no2,
                        signatures[no2]['rf'],
                        signatures[no2]['pri'],
                    ]
                coeff = signatures[no2]['coeffs']
                eta = mahalanobis_distance(entry, coeff, sample[0], sample[1])
                matches.append([abs(eta), no2])

            matches = sorted(matches)
            if no == matches[0][1]:
                sample_ok = True

    samples[no] = sample

filename = "Demo/Inputs/samples"
os.makedirs(os.path.dirname(filename), exist_ok=True) 
with open(filename, 'w') as f:
    f.write(str(samples) + '\n')

# Nests the columns to a list and creates the input files
# This code is not very pretty, but it works and should never ever be rewritten
player1_single = ''
player1_single_coeffs = ''
player1_double = ''
player1_double_coeffs = ''
player2_double = ''
player2_double_coeffs = ''
player1_triple = ''
player1_triple_coeffs = ''
player2_triple = ''
player2_triple_coeffs = ''
player3_triple = ''
player3_triple_coeffs = ''
player1_quadruple = ''
player1_quadruple_coeffs = ''
player2_quadruple = ''
player2_quadruple_coeffs = ''
player3_quadruple = ''
player3_quadruple_coeffs = ''
player4_quadruple = ''
player4_quadruple_coeffs = ''

# 65;1853818;172943;2;-410;-410;82483

for i, sig in signatures.items():
    cluster = str(i)
    rf = str(sig['rf'])
    pri = str(sig['pri'])
 
    signature = cluster + ' ' + rf + ' ' + pri + ' '
    coeffs = ' '.join([str(s) for s in sig['coeffs']]) + ' '

    if i in database_P1_single:
        player1_single += signature
        player1_single_coeffs += coeffs

    if i in database_P1_double:
        player1_double += signature
        player1_double_coeffs += coeffs

    if i in database_P2_double:
        player2_double += signature
        player2_double_coeffs += coeffs

    if i in database_P1_triple:
        player1_triple += signature
        player1_triple_coeffs += coeffs

    if i in database_P2_triple:
        player2_triple += signature
        player2_triple_coeffs += coeffs

    if i in database_P3_triple:
        player3_triple += signature
        player3_triple_coeffs += coeffs

    if i in database_P1_quadruple:
        player1_quadruple += signature
        player1_quadruple_coeffs += coeffs

    if i in database_P2_quadruple:
        player2_quadruple += signature
        player2_quadruple_coeffs += coeffs

    if i in database_P3_quadruple:
        player3_quadruple += signature
        player3_quadruple_coeffs += coeffs

    if i in database_P4_quadruple:
        player4_quadruple += signature
        player4_quadruple_coeffs += coeffs

with open("Demo/Inputs/Input-Single-P1-0", 'w') as f:
    f.write(player1_single + player1_single_coeffs + '\n')

with open("Demo/Inputs/Input-Double-P1-0", 'w') as f:
    f.write(player1_double + player1_double_coeffs + '\n')

with open("Demo/Inputs/Input-Double-P2-0", 'w') as f:
    f.write(player2_double + player2_double_coeffs + '\n')

with open("Demo/Inputs/Input-Triple-P1-0", 'w') as f:
    f.write(player1_triple + player1_triple_coeffs + '\n')

with open("Demo/Inputs/Input-Triple-P2-0", 'w') as f:
    f.write(player2_triple + player2_triple_coeffs + '\n')

with open("Demo/Inputs/Input-Triple-P3-0", 'w') as f:
    f.write(player3_triple + player3_triple_coeffs + '\n')

with open("Demo/Inputs/Input-Quadruple-P1-0", 'w') as f:
    f.write(player1_quadruple + player1_quadruple_coeffs + '\n')

with open("Demo/Inputs/Input-Quadruple-P2-0", 'w') as f:
    f.write(player2_quadruple + player2_quadruple_coeffs + '\n')

with open("Demo/Inputs/Input-Quadruple-P3-0", 'w') as f:
    f.write(player3_quadruple + player3_quadruple_coeffs + '\n')

with open("Demo/Inputs/Input-Quadruple-P4-0", 'w') as f:
    f.write(player4_quadruple + player4_quadruple_coeffs + '\n')

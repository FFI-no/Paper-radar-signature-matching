import numpy as np
from Demo.data import *

features = 3
num_coeffs = 3
records = 88


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
		

# Helping functions for classifier

def mahalanobis_distance(database, coeff, measurement_rf, measurement_pri):
    """
    Calculates mahalanobis distance through choleskey decomposition, however we do not perform choleskey decomposition. 
    """	
    y1 = measurement_pri - database[2]
    y2 = measurement_rf - database[1]
	
    summand_1 = y1**2 * coeff[0]
    summand_2 = y2**2 * coeff[1]
    summand_3 = - 2 * y1 * y2 * coeff[2]

    eta = summand_1 + summand_2 + summand_3
    #print('%s: %s %s, %s + %s + %s' % (database[0], y1, y2, summand_1, summand_2, summand_3))

    return eta	
	
	
# Finds the best cluster for the measurments given a database
def classify(database, coeffs, number_of_signatures, measurement_rf, measurement_pri):
    """
    classifying the measurement in given database
    """
    temp = []
    res = np.zeros(shape=(10, 2))

    for i in range(number_of_signatures):
        mask = int(contained(measurement_rf, measurement_pri, database[i][1], database[i][2]))
        temp.append(mask * database[i][0])
        
    temp.sort()

    for k in range(10):
        counter = records - k - 1
        if temp[counter] != 0:
            res[k][0] = temp[counter]
            res[k][1] = mahalanobis_distance(database[temp[counter]-1], coeffs[temp[counter]-1], measurement_rf, measurement_pri)

    return res

fname = './Signature/Demo/Inputs/Input-Single-P1-0'
with open(fname) as f:
    loaded_list = f.read().split()

signatures = np.array([int(x) for x in loaded_list[:features*records]]).reshape(-1, features)
coeffs = np.array([float(x) for x in loaded_list[num_coeffs*records:]]).reshape(-1, features)

for vessel, measurement in radar_sample.items():
    detected_vessels = classify(signatures, coeffs, records, measurement[0], measurement[1])
    detected_vessels = sorted((list(x) for x in detected_vessels if (x[1] > 0)), key=lambda x: x[1])
    if vessel==detected_vessels[0][0]:
        print(vessel, 'ok', detected_vessels)
    else:
        print(vessel, 'fail', detected_vessels)        
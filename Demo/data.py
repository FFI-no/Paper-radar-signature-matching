max = 88

database_P1_single = list(range(1, max + 1))

database_P1_double = list(range(1, 46))
database_P2_double = list(range(46,max + 1))

database_P1_triple = list(range(1, 31))
database_P2_triple = list(range(31, 61))
database_P3_triple = list(range(62, max + 1))

database_P1_quadruple = list(range(1, 31))
database_P2_quadruple = list(range(31, 61))
database_P3_quadruple = list(range(62, 77))
database_P4_quadruple = list(range(77, max + 1))

radar_sample = {
        1: [2310213, 129913], 
        2: [2173686, 40565], 
        3: [1979001, 131497], 
        4: [2426865, 133080], 
        5: [2072906, 56233], 
        6: [2249781, 137938], 
        7: [2176625, 65576], 
        8: [1883971, 198005], 
        9: [2003834, 127629], 
        10: [2069782, 111776], 
        11: [1850261, 219246], 
        12: [2225949, 200592], 
        13: [1840758, 154283], 
        14: [1965018, 89163], 
        15: [1937280, 111610], 
        16: [1919286, 72968], 
        17: [2287718, 131632],
        18: [2118199, 43337], 
        19: [2267117, 137151], 
        20: [1922270, 210042], 
        21: [1864198, 78451], 
        22: [1805800, 61128], 
        23: [2247246, 102411], 
        24: [1867887, 84984], 
        25: [1916798, 196422], 
        26: [1847493, 211170], 
        27: [2268940, 57960], 
        28: [1825314, 193230], 
        29: [2325809, 138889], 
        30: [2342697, 43146], 
        31: [1847751, 119627], 
        32: [2086011, 102133], 
        33: [2331914, 187115], 
        34: [1971372, 197183], 
        35: [2336377, 108022], 
        36: [2264027, 107050], 
        37: [1826478, 61438], 
        38: [1945688, 119864], 
        39: [2001086, 171649], 
        40: [2334952, 143345], 
        41: [1980060, 59620], 
        42: [2117677, 79944], 
        43: [2071705, 102502], 
        44: [2292888, 129712], 
        45: [1990821, 159564], 
        46: [1900075, 83749], 
        47: [2253595, 128317], 
        48: [2236491, 124986], 
        49: [1807375, 173610], 
        50: [1963726, 199013], 
        51: [1808464, 154827], 
        52: [2284591, 139294], 
        53: [2149845, 181768], 
        54: [1924110, 178834], 
        55: [2271006, 209579], 
        56: [2013666, 170681], 
        57: [2129127, 72669], 
        58: [2282581, 64385], 
        59: [2210372, 64720], 
        60: [2252592, 60558], 
        61: [2185614, 203068], 
        62: [2102130, 157903], 
        63: [2300944, 135557], 
        64: [2248999, 133822], 
        65: [2124323, 127119], 
        66: [2199724, 200205], 
        67: [2080824, 206122], 
        68: [2205581, 169862], 
        69: [2266592, 54507], 
        70: [2335136, 145119], 
        71: [2257577, 130552], 
        72: [2166582, 83636], 
        73: [2201494, 90841], 
        74: [1893291, 105978], 
        75: [2298035, 171211], 
        76: [1923335, 162885], 
        77: [1894954, 105781], 
        78: [2157224, 88069], 
        79: [2228037, 99361], 
        80: [2095541, 195555], 
        81: [1959155, 108346], 
        82: [2310650, 132166], 
        83: [2048169, 46289], 
        84: [2166701, 183214], 
        85: [1963183, 145039], 
        86: [1927254, 81267], 
        87: [2165322, 64940], 
        88: [2028527, 127868]
    }

vessel_id_to_name = {   # (Name, Speed), where Speed is: 25kph * Speed = real world speed
                      1: ('Vessel 1', 1, 0), 2: ('Vessel 2', 1, 0), 3: ('Vessel 3', 1, 0), 4: ('Vessel 4', 1, 0),
                      5: ('Vessel 5', 1, 0), 6: ('Vessel 6', 1, 0), 7: ('Vessel 7', 1, 1), 8: ('Vessel 8', 1, 0),
                      9: ('Vessel 9', 1, 0), 10: ('Vessel 10', 1, 0), 11: ('Speed Boat 11', 22, 1), 12: ('Speed Boat 12', 22, 0),
                      13: ('Speed Boat 13', 22, 0), 14: ('Speed Boat 14', 22, 0), 15: ('Speed Boat 15', 22, 0), 16: ('Speed Boat 16', 22, 1),
                      17: ('Speed Boat 17', 22, 1), 18: ('Speed Boat 18', 22, 1), 19: ('Speed Boat 19', 22, 0), 20: ('Fighter Jet 20', 77, 0),
                      21: ('Fighter Jet 21', 77, 0), 22: ('Fighter Jet 22', 77, 0), 23: ('Fighter Jet 23', 77, 0), 24: ('Fighter Jet 24', 77, 0),
                      25: ('Fighter Jet 25', 77, 1), 26: ('Fighter Jet 26', 77, 0), 27: ('Fighter Jet 27', 77, 1), 28: ('Fighter Jet 28', 77, 1),
                      29: ('Missile 29', 245, 1), 30: ('Vessel 30', 1, 1), 31: ('Vessel 31', 1, 0), 32: ('Vessel 32', 1, 1),
                      33: ('Vessel 33', 1, 1), 34: ('Vessel 34', 1, 1), 35: ('Vessel 35', 1, 1), 36: ('Vessel 36', 1, 0),
                      37: ('Vessel 37', 1, 1), 38: ('Vessel 38', 1, 1), 39: ('Vessel 39', 1, 1), 40: ('Vessel 40', 1, 1),
                      41: ('Speed Boat 41', 22, 0), 42: ('Speed Boat 42', 22, 1), 43: ('Speed Boat 43', 22, 1), 44: ('Speed Boat 44', 22, 1),
                      45: ('Speed Boat 45', 22, 0), 46: ('Speed Boat 46', 22, 1), 47: ('Speed Boat 47', 22, 1), 48: ('Speed Boat 48', 22, 0),
                      49: ('Speed Boat 49', 22, 0), 50: ('Speed Boat 50', 22, 0), 51: ('Fighter Jet 51', 77, 1), 52: ('Fighter Jet 52', 77, 1),
                      53: ('Fighter Jet 53', 77, 1), 54: ('Fighter Jet 54', 77, 1), 55: ('Fighter Jet 55', 77, 0), 56: ('Fighter Jet 56', 77, 1),
                      57: ('Fighter Jet 57', 77, 0), 58: ('Fighter Jet 58', 77, 0), 59: ('Fighter Jet 59', 77, 1), 60: ('Fighter Jet 60', 77, 1),
                      61: ('Missile 61', 245, 1), 62: ('Vessel 62', 1, 1), 63: ('Vessel 63', 1, 1), 64: ('Vessel 64', 1, 0),
                      65: ('Vessel 65', 1, 1), 67: ('Vessel 67', 1, 1), 68: ('Vessel 68', 1, 0), 69: ('Vessel 69', 1, 0),
                      70: ('Vessel 70', 1, 0), 71: ('Vessel 71', 1, 1), 72: ('Vessel 72', 1, 0), 73: ('Speed Boat 73', 22, 0),
                      74: ('Speed Boat 74', 22, 1), 75: ('Speed Boat 75', 22, 0), 76: ('Speed Boat 76', 22, 0), 77: ('Speed Boat 77', 22, 1),
                      78: ('Speed Boat 78', 22, 1), 79: ('Speed Boat 79', 22, 0), 80: ('Speed Boat 80', 22, 0), 81: ('Speed Boat 81', 22, 0),
                      82: ('Fighter Jet 82', 77, 1), 83: ('Fighter Jet 83', 77, 0), 84: ('Fighter Jet 84', 77, 1), 85: ('Fighter Jet 85', 77, 1),
                      86: ('Fighter Jet 86', 77, 1), 87: ('Fighter Jet 87', 77, 1), 88: ('Fighter Jet 88', 77, 0), 89: ('Fighter Jet 89', 77, 0),
                      66: ('Missile 66', 245, 0)
                      }


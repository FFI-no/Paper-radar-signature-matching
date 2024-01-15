# Filename for the protocol to run
protocol = 'mascot-party.x'   # Warning: We have only tested with MASCOT. Other protocols *should* work as well.
protocol_options = []

# This should have a trailing /
mpspdz_location = '../MP-SPDZ/'

measurement_input = './Signature/Demo/Inputs/Input'

database_input = './Signature/Demo/Inputs/Input-'
database_input_single = database_input + 'Single'
database_input_double = database_input + 'Double'
database_input_triple = database_input + 'Triple'
database_input_quadruple = database_input + 'Quadruple'

protocol_path = mpspdz_location + protocol

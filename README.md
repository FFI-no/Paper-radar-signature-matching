# Private detection and classification of radar signals

Any reports of improvements and problems in the MPC code is highly appreciated.

The work was primarily carried out by FFI summer interns Mathias Karsrud Nordal (NTNU) and Benjamin Hansen Mortensen (UiO), with help and follow-up work by Martin Strand (FFI).

## Installation
1. Install [MP-SPDZ](https://github.com/data61/MP-SPDZ) on your system, and make a note of where you placed the binaries (e.g. `mascot-party.x`).
2. Clone this repository to your system.
3. Edit `settings.py` to point to MP-SPDZ
4. Run 
```
chmod u+x SETUP.sh
./SETUP.sh
```
to automatically compile the MPC files and install the necessary Python packages. You might want to open a virtual environment before installing the Python packages.
5. Execute `python demo_v1.py` to run the demonstration.

## Known issues
- The Multi PC option in the demo contains hardcoded IP addresses, and must be customized before using.
- The fixed-point parameters are possibly set a bit too low, and may result in wrong results. Please report any at sight.


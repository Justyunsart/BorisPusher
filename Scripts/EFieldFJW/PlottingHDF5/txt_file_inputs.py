# script.py
import sys
import os

# from diff import file_path1

path = "/Users/fwessel/Documents/Boris_Usr/Outputs/Custom/100000.0/Magpy/washer_potential/comparisons/ns-85000_dt-2e-09, 1-9,1.1,0.75,0.25/data.hdf5"
# Remove the last component (file name)
pruned_path = os.path.dirname(path)
print(pruned_path)




#
# filepath = sys.argv[1]
# print(pruned_path)
#
def read_params(filename):
    with open(filename, "r") as f:
        # read the first line (header)
        header_line = f.readline().strip()

        # split by commas
        fields = header_line.split(",")

        # grab positions 0, 3, 4
        param1 = fields[0]  # PosX
        param2 = fields[3]  # Amp
        param3 = fields[4]  # Diameter

        return param1, param2, param3


if __name__ == "__main__":
    filename = "b_coils.txt"
    posx, amp, diameter = read_params(filename)
    print("Parameter 1 (PosX):", posx)
    print("Parameter 2 (Amp):", amp)
    print("Parameter 3 (Diameter):", diameter)
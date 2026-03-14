import sys
from urllib.parse import quote

# usage:
# % python ./whats_missing.py <larger_file.csv> <shorter_file.csv> <results_file.dat>

# sort files before execution
def read_list(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip()]

list1_file = sys.argv[1]
list2_file = sys.argv[2]
list3_file = sys.argv[3]

list1 = read_list(list1_file)
list2 = read_list(list2_file)

list1.sort()
list2.sort()
list2 = set(list2)

with open(list3_file, "w") as out:
    for item in list1:
        item = item.rstrip("\n")
        if item not in list2:
            out.write(item + "\n")


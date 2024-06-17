import csv

config = {}
with open("config.txt") as config_file:
    lines = config_file.read().split()
    for line in lines:
        words = line.split("=")
        if len(words)==2:
            config[words[0]] = words[1]

lines = []
if "excel_name" in config:
    print(config["excel_name"])
    with open(config["excel_name"]) as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            lines.append(line)

divide_by = 8

lines_per_file = len(lines)//divide_by

for i in range(0, len(lines), lines_per_file):
    print(i)
    lines_to_write = lines[i:i+lines_per_file]
    with open("data/split_excel/split_csv_{}.csv".format(i), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in lines_to_write:
            csv_writer.writerow(row)

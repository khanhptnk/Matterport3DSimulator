import os
import sys
from pprint import pprint

def read_obj_category():
    obj_category_map = {}
    with open('category_mapping.tsv') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            fields = line.split('\t')
            obj_category_map[fields[0]] = fields[1]
    return obj_category_map

def read_region_label():
    region_label_map = {}
    with open('region_label.txt') as f:
        for line in f:
            line = line.rstrip()
            code = line[1]
            try:
                label = line[line.index('=') + 2:line.index('(') - 1]
            except ValueError:
                label = line[line.index('=') + 2:]
            region_label_map[code] = label
    return region_label_map

def read_house_file_format():
    field_names = {}
    with open('house_file_format.txt') as f:
        for line in f:
            fields = line.rstrip().split()
            field_names[fields[0]] = fields[1:]
    return field_names

def read_line(code, values):
    res = {}
    for k, v in zip(field_names[code], values):
        res[k] = v
    return res

def get_cord(x):
    return float(x['px']), float(x['py']), float(x['pz'])

def find_nearest_point(a, bs):
    def distance(a, b):
        return (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2

    best_id = -1
    best_dist = 1e9
    for i, b in enumerate(bs):
        d = distance(a, b)
        if best_id == -1 or d < best_dist:
            best_id = i
            best_dist = d
    return best_id


OMIT_MPCAT40_CATEGORIES = [0, 1, 2, 17, 29, 40, 41]
OMIT_CATEGORY_NAMES = ['object', 'objects']

region_label_map = read_region_label()
pprint(region_label_map)
field_names = read_house_file_format()

in_file = '/home/kxnguyen/Data/v1/scans/17DRP5sb8fy/house_segmentations/17DRP5sb8fy.house'
with open(in_file) as f:
    lines = f.readlines()

data = {}

for i, line in enumerate(lines[1:]):
    field_code = line[0]
    if field_code not in data:
        data[field_code] = []

    field_values = line[2:].split()
    if field_code == 'P' and len(field_values) != 12:
        continue

    data[field_code].append(read_line(field_code, field_values))

categories = []
omit_categories = []
for item in data['C']:
    if int(item['mpcat40_index']) in OMIT_MPCAT40_CATEGORIES:
        omit_categories.append(item['category_index'])
        continue
    item['category_mapping_name'] = item['category_mapping_name'].replace('#', ' ').replace(';', '').replace('\\', '/ ')
    categories.append(item)

data['C'] = categories
data['O'] = list(filter(lambda item: item['category_index'] not in omit_categories, data['O']))

pprint(sorted([item['category_mapping_name'] for item in data['C']]))
"""
obj_cords = [get_cord(item) for item in data['O']]

for item in data['P']:
    print item['panorama_index'], item['name'],
    region_label = region_label_map[data['R'][int(item['region_index'])]['label']]
    print region_label,
    view_cord = get_cord(item)
    nearest_obj_id = find_nearest_point(view_cord, obj_cords)
    print nearest_obj_id
    print
"""

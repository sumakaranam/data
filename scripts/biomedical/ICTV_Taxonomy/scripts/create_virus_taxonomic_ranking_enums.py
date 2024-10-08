# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Author: Samantha Piekos
Date: 02/21/2024
Name: create_virus_taxonomic_ranking_enums.py
Description: Creates hierarchical viral taxonomy enum schema from the
ICTV Virus Metadata Resource.
@file_input: ICTV Virus Metadata Resource .xslx file
@file_output: formatted .mcf files for viral taxonomy enum schema
"""

# load environment
import pandas as pd
import sys

# declare universal variables
HEADER = [
    'sort', 'isolateSort', 'realm', 'subrealm', 'kingdom', 'subkingdom',
    'phylum', 'subphylum', 'class', 'subclass', 'order', 'suborder', 'family',
    'subfamily', 'genus', 'subgenus', 'species', 'isExemplar', 'name',
    'abbreviation', 'isolateDesignation', 'genBankAccession', 'refSeqAccession',
    'genomeCoverage', 'genomeComposition', 'hostSource', 'host', 'source',
    'dcid', 'isolate_dcid', 'isolate_name'
]

LIST_DROP = [
    'sort', 'isolateSort', 'species', 'isExemplar', 'name', 'abbreviation',
    'isolateDesignation', 'genBankAccession', 'refSeqAccession',
    'genomeCoverage', 'genomeComposition', 'hostSource', 'host', 'source',
    'dcid', 'isolate_dcid', 'isolate_name'
]


# declare functions
def pascalcase(s):
    list_words = s.split()
    converted = "".join(
        word[0].upper() + word[1:].lower() for word in list_words)
    return converted


def check_for_illegal_charc(s):
    list_illegal = ["'", "–", "*"
                    ">", "<", "@", "]", "[", "|", ":", ";"
                    " "]
    if any([x in s for x in list_illegal]):
        print('Error! dcid contains illegal characters!', s)


def initiate_enum_dict():
    d = {}
    list_levels = [i for i in HEADER if i not in LIST_DROP]
    for item in list_levels:
        enum_name = 'Virus' + item.capitalize() + 'Enum'
        d[enum_name] = {}
    return d


def add_enums_to_dicts(key, value, d):
    if value == value:
        enum = 'Virus' + key + 'Enum'
        dcid = 'Virus' + key + pascalcase(value)
        check_for_illegal_charc(dcid)
        d[enum][value] = dcid
    return d


def add_item_to_enums(df):
    list_levels = [i for i in HEADER if i not in LIST_DROP]
    dict_of_dicts = initiate_enum_dict()
    dict_specialization = {}  # keep track of previous top level
    for index, row in df.iterrows():
        last_level_dcid = False  # initiate empty value for tracking specialization
        for item in list_levels:
            level = item.capitalize()
            if row[item] != row[item]:
                continue
            dict_of_dicts = add_enums_to_dicts(level, row[item], dict_of_dicts)
            if last_level_dcid:  # track specialization if relevant
                dcid = 'Virus' + level + pascalcase(row[item])
                dict_specialization[dcid] = last_level_dcid
            last_level_dcid = 'Virus' + level + pascalcase(
                row[item])  # update top level
    return dict_of_dicts, dict_specialization


def write_individual_entries_to_file(w, enum, d, dict_specialization):
    for key, value in d.items():
        w.write('Node: dcid:' + value + '\n')
        w.write('name: "' + key + '"\n')
        w.write('typeOf: dcs:' + enum + '\n')
        if value in dict_specialization:
            w.write('specializationOf: dcs:' + dict_specialization[value] +
                    '\n\n')
        else:
            w.write('\n')
    return w


def write_dict_to_file(w, enum, d, dict_specialization):
    w.write('# ' + enum + '\n')
    w.write('Node: dcid:' + enum + '\n')
    w.write('name: "' + enum + '"\n')
    w.write('typeOf: schema:Class\n')
    w.write('subClassOf: schema:Enumeration\n\n')
    w = write_individual_entries_to_file(w, enum, d, dict_specialization)
    w.write('\n')
    return w


def generate_enums_mcf(f, w):
    df = pd.read_excel(f, names=HEADER, header=None, sheet_name=0)
    df = df.drop(LIST_DROP, axis=1).drop(0, axis=0)
    dict_of_dicts, dict_specialization = add_item_to_enums(df)
    w = open(w, mode='w')
    w.write('# Schema generated by create_virus_taxonomic_ranking_enums.py\n\n')
    for key, value in dict_of_dicts.items():
        w = write_dict_to_file(w, key, value, dict_specialization)


def main():
    file_input = sys.argv[1]
    file_output = sys.argv[2]

    generate_enums_mcf(file_input, file_output)


if __name__ == '__main__':
    main()

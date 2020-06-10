import math
import pathlib
import random

state_codes = {
    'WA': '53', 'DE': '10', 'D.': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

state_names = {
    'WA': 'Washington', 'DE': 'Delaware', 'D.': 'District of Columbia', 'WI': 'Wisconsin', 'WV': 'West Virginia',
    'HI': 'Hawaii', 'FL': 'Florida', 'WY': 'Wyoming', 'PR': 'Puerto Rico', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'TX': 'Texas', 'LA': 'Louisiana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'TN': 'Tennessee',
    'NY': 'New York', 'PA': 'Pennsylvania', 'AK': 'Alaska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'VA': 'Virginia',
    'CO': 'Colorado', 'CA': 'California', 'AL': 'Alabama', 'AR': 'Arkansas', 'VT': 'Vermont', 'IL': 'Illinois',
    'GA': 'Georgia', 'IN': 'Indiana', 'IA': 'Iowa', 'MA': 'Massachusetts', 'AZ': 'Arizona', 'ID': 'Idaho',
    'CT': 'Connecticut', 'ME': 'Maine', 'MD': 'Maryland', 'OK': 'Oklahoma', 'OH': 'Ohio', 'UT': 'Utah',
    'MO': 'Missouri', 'MN': 'Minnesota', 'MI': 'Michigan', 'RI': 'Rhode Island', 'KS': 'Kansas', 'MT': 'Montana',
    'MS': 'Mississippi', 'SC': 'South Carolina', 'KY': 'Kentucky', 'OR': 'Oregon', 'SD': 'South Dakota',
    'U.': 'Virgin Islands'
}

LARGE_FONT = ('Verdana', 12)
MEDIUM_FONT = ('Verdana', 9)
SMALL_FONT = ('Verdana', 6)

CONFIRMED = 'Confirmed'
DEATHS = 'Deaths'
MORTALITY = 'Mortality rate'
RECOVERED = 'Recovered'
RT = 'Rt'

ALPHABETICAL = 'Alphabetical'
PER_CAPITA_INCOME = 'Per Capita Income'
POPULATIONAL_DENSITY = 'Populational Density'
LARGER_RISK_GROUP = 'Larger Risk Group'


def get_upper_case(string):
    char = string[0]
    if ord(char) > 96:
        char = chr(ord(char) - 32)
    return char + string[1:]


def string_in(string, string_array, is_in):
    bool_array = []
    for strings in string_array:
        if is_in:
            bool_array.append(string in strings)
        else:
            bool_array.append(string not in strings)
    return bool_array


def string_in_tuple(string, string_array, is_in):
    bool_array = []
    for index, strings in string_array.iteritems():
        if is_in:
            bool_array.append((index, (string in strings)))
        else:
            bool_array.append((index, (string not in strings)))
    return bool_array


def string_until(string, delimiter):
    for i in range(len(string)):
        if string[i] == delimiter:
            return string[:i], string[i + 2:]

    return string, ''


def random_color():
    hex_number = str(hex(random.randint(1118481, 16777215)))
    return '#' + hex_number[2:]


def take_second(elem):
    if math.isnan(elem[1]):
        return float('inf')
    return elem[1]


def name_in_tuple_list(elem, tuple_list):
    if len(tuple_list) > 0:
        list1, _ = list(zip(*(tuple_list.copy())))
        return elem in list1

    return False


def return_unique(list_repeated):
    new_list = []
    for elem in list_repeated:
        if elem not in new_list:
            new_list.append(elem)

    return new_list


def count_files(path_name):
    count = 0
    for path in pathlib.Path(path_name).iterdir():
        if path.is_file():
            count += 1
    return count

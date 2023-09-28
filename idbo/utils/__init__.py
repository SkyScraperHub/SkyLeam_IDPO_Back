import string, random

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def convert_id_int_to_str(id):
    return "0"*(6 - len(str(id))) + str(id)
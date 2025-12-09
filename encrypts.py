import string

key = "af2r5huh6333"
az = string.ascii_lowercase


def caesar(input_str, shifts):
    upper = string.ascii_uppercase
    newstr = ""
    # new_char = ''
    new_shift = shifts
    for i in range(len(input_str)):
        char = input_str[i].upper()
        if char in upper:
            index = upper.index(char.upper())
            shifted = (index + new_shift) % 26
            new_char = upper[shifted]
            if input_str[i].islower():
                new_char = new_char.lower()
        else:
            new_char = char
        newstr = newstr + new_char
        new_shift = new_shift + 1
    return newstr


def rail(strings, amount):
    if len(strings) < 3:
        return strings
    new_str = ""
    for i in range(0, len(strings), 2):
        new_str = new_str + strings[i]
    for i in range(1, len(strings), 2):
        new_str = new_str + strings[i]
    if amount > 0:
        rail(strings, amount - 1)
    return new_str


# noinspection SpellCheckingInspection
def decaesar(input_str, shift):
    upper = string.ascii_uppercase
    newstr = ""
    # new_char = ''
    new_shift = shift
    for i in range(len(input_str)):
        char = input_str[i].upper()
        if char in upper:
            index = upper.index(char)
            if index - new_shift < 0:
                shifted = (index - new_shift) + 26
            else:
                shifted = (index - new_shift)
            new_char = upper[shifted]
            if input_str[i].islower():
                new_char = new_char.lower()
        else:
            new_char = char
        newstr = newstr + new_char
        new_shift = (new_shift + 1) % 26
    return newstr


def derail(strings, amount):
    result = ""
    if len(strings) < 3:
        return strings
    half = (len(strings) + 1) // 2
    even = strings[:half]
    odd = strings[half:]
    i = 0
    j = 0
    for step in range(len(strings)):
        if step % 2 == 0:
            result = result + even[i]
            i += 1
        else:
            result = result + odd[j]
            j += 1
    if amount > 0:
        derail(strings, amount - 1)
    return result


def encrypt(message):
    # key = "af2r5huh6333"
    text = message
    # print(text)
    # print("\npre encrypt\n")
    for k in key:
        if k.isalpha():
            cea_num = az.index(k.lower())
            text = caesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = rail(text, shift_by)
    # print(text)
    # print("\npost encrypt\n")
    return text


def decrypt(ciphertext):
    # key = "af2r5huh6333"
    text = ciphertext
    # Reverse the key order for decryption
    for k in reversed(key):
        if k.isalpha():
            cea_num = az.index(k.lower())
            text = decaesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = derail(text, shift_by)

    return text

import string

key = "af2r5huh6333"
az = string.ascii_lowercase


def caesar(input_str, shifts):
    upper = string.ascii_uppercase
    newstr = ""
    new_char = ''
    for i in range(len(input_str)):
        char = input_str[i]
        if char in upper:
            index = upper.index(char.upper())
            shifted = (index + shifts) % 26
            new_char = upper[shifted]
            if char.islower():
                new_char = new_char.lower()
        else:
            new_char = char
        newstr = newstr + new_char
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
    new_char = ''
    for i in range(len(input_str)):
        char = input_str[i]
        if char in upper:
            index = upper.index(char)
            shifted = (index - shift)
            new_char = upper[shifted]
        else:
            new_char = char
        newstr = newstr + new_char
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
    text = message
    offset = 0
    # print(text)
    # print("\npre encrypt\n")
    for k in key:
        if k.isalpha():
            cea_num = (az.index(k.lower()) + offset) % 26
            offset = (az.index(k.lower()) + offset) % 26
            text = caesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = rail(text, shift_by)
    # print(text)
    # print("\npost encrypt\n")
    return text


def decrypt(ciphertext):
    text = ciphertext
    offset = 0
    for k in key:
        if k.isalpha():
            offset = (az.index(k.lower()) + offset) % 26
    # Reverse the key order for decryption
    for k in reversed(key):
        if k.isalpha():
            cea_num = (az.index(k.lower()) + offset) % 26
            offset = offset - az.index(k.lower())
            if offset < 0:
                offset = offset + 26
            text = decaesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = derail(text, shift_by)

    return text
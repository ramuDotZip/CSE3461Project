import string
#public variables
key = "af2r5huh6333"
az = string.ascii_lowercase

#shift/ceasers cypher
def caesar(input_str, shifts):
    upper = string.ascii_uppercase
    newstr = ""
    #new_shift makes it incriment the shift for each char
    new_shift = shifts
    #loop though each char in string
    for i in range(len(input_str)):
        char = input_str[i].upper()
        #if char is letter then shift it
        if char in upper:
            index = upper.index(char.upper())
            shifted = (index + new_shift) % 26
            new_char = upper[shifted]
            if input_str[i].islower():
                new_char = new_char.lower()
        #char is not a letter so dont change
        else:
            new_char = char
        newstr = newstr + new_char
        new_shift = new_shift + 1
    return newstr

#rail cipher
def rail(strings, amount):
    #minimum amount needed for rail, should always be possible but just in case
    if len(strings) < 3:
        return strings
    new_str = ""
    #"layers" the characters by going back and forth
    for i in range(0, len(strings), 2):
        new_str = new_str + strings[i]
    for i in range(1, len(strings), 2):
        new_str = new_str + strings[i]
    #recusrsivly rails it the amout of times called by num from key
    if amount > 0:
        rail(strings, amount - 1)
    return new_str

#decript ceaser/shift cypher
# noinspection SpellCheckingInspection
def decaesar(input_str, shift):
    upper = string.ascii_uppercase
    newstr = ""
    # new_char = ''
    new_shift = shift
    #almost the same but opposite
    for i in range(len(input_str)):
        char = input_str[i].upper()
        if char in upper:
            index = upper.index(char)
            #make sure it doesnt go negative
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

#un rail cyophers it
def derail(strings, amount):
    result = ""
    #once again ensuring no bugs there
    if len(strings) < 3:
        return strings
    #split the string into 2 halfs to put together
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

#reads though key if letter do shift/cipher using letter value as shift, if number use rail shift number amout of times
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

#reads though key backwards if letter do reverse shift/cipher using letter value as shift, if number use reverse rail shift number amout of times
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

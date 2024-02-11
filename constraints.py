# opti.py
# This is a program based on Optimality Theory. 
# The first section is intended to help users determine if a word violates or passes constraints.
# The second section is intended to provide a Winners/Losers table for user.
# The final section uses Recursive Constraint Demotion to rank Constraints into Stratas

import eng_to_ipa as e2i

# Static Variables
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 
              'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'y', 'z']
vowels = ['a', 'e', 'i', 'o', 'u', 'w']

constraint_functions = []

def constraint(func):
    constraint_functions.append(func)
    return func

def get_constraint_functions():
    return constraint_functions


# Constraint Functions
@constraint
def starCC(word):
    """Checks if the input word violates the *CC constraint (Complex Onsets).
    
    A syllable with a structure of CCV (where C is a consonant and V is a vowel)
    is considered to have a complex onset and thus violates the constraint.
    CV and V structures are permitted.
    
    Args:
        word (str): The word to be checked against the *CC constraint.
        
    Returns:
        bool: True if the word passes the *CC constraint, False otherwise.
    """
    # Loop through each character in the word until a vowel is found
    consonant_count = 0
    for char in word:
        if char.lower() in vowels:
            break
        elif char.lower() in consonants:
            consonant_count += 1
        if consonant_count > 1:
            # More than one consonant before a vowel is a violation
            return False
    # If the loop ends without a violation, the word passes the constraint
    return True

@constraint
def noDiphthong(word):
    """Checks if the input word violates the NoDiphthong constraint.
    
    This constraint checks for the presence of long vowels or diphthongs in a syllable. 
    A diphthong is defined as two adjacent vowel sounds within the same syllable.
    
    Args:
        word (str): The word to be checked against the NoDiphthong constraint.
        
    Returns:
        bool: True if the word does not contain diphthongs, False otherwise.
    """
    extended_vowels = vowels
    previous_char_was_vowel = False
    
    for char in word:
        if char.lower() in extended_vowels:
            if previous_char_was_vowel:
                # Found two vowels in a row, this is a diphthong
                return False
            previous_char_was_vowel = True
        else:
            previous_char_was_vowel = False
    
    # No diphthongs found in the word
    return True

@constraint
def noDeleteVowel(input_word, output_word):
    """
    Checks if a vowel has been deleted from the original input word in the new output word.
    
    Args:
        input_word (str): The original word before deletion.
        output_word (str): The word after deletion has been applied.
        
    Returns:
        bool: True if no vowel has been deleted, False otherwise.
    """
    input_vowels = [char for char in input_word if char.lower() in vowels]
    output_vowels = [char for char in output_word if char.lower() in vowels]
    
    input_vowel_count = len(input_vowels)
    output_vowel_count = len(output_vowels)
    
    return input_vowel_count == output_vowel_count


@constraint
def noDeleteConsonant(input_word, output_word):
    """
    Checks if a consonant has been deleted from the original input word in the new output word.
    
    Args:
        input_word (str): The original word before deletion.
        output_word (str): The word after deletion has been applied.
        
    Returns:
        bool: True if no consonant has been deleted, False otherwise.
    """
    input_consonants = [char for char in input_word if char.lower() in consonants]
    output_consonants = [char for char in output_word if char.lower() in consonants]
    
    input_consonant_count = len(input_consonants)
    output_consonant_count = len(output_consonants)
    
    return input_consonant_count == output_consonant_count

# @constraint
# def noSkippingIPA(input_word, output_word): 
#     '''
#     This function is currently not tested! 
#     I'm unsure if it works correctly, especially within the context of the assignment.
#     It might technically be more accurate than noSkipping(), if you're really looking for
#     the phonetically correct answer. However, its probably easier to just use noSkipping()
#     until we full understand what the NoSkipping constraint actually requires.
#     '''
    
#     # Convert words to their IPA representations
#     input_ipa = e2i.convert(input_word)
#     output_ipa = e2i.convert(output_word)
#     print(f"Input: {input_ipa}")
#     print(f"Output: {output_ipa}")

#     # Convert IPA strings to lists of individual phonetic elements
#     # This is necessary to correctly handle multi-character IPA symbols
#     input_ipa_list = list(input_ipa)
#     output_ipa_list = list(output_ipa)
#     print(f"Input: {input_ipa_list}")
#     print(f"Output: {output_ipa_list}")

#     i, j = 0, 0
#     while i < len(input_ipa_list) and j < len(output_ipa_list):
#         print(f"Comparing {input_ipa_list[i]} with {output_ipa_list[j]}")
#         if input_ipa_list[i] == output_ipa_list[j]:
#             j += 1
#         elif i > 0 and i < len(input_ipa_list) - 1 and input_ipa_list[i - 1] == output_ipa_list[j - 1] and input_ipa_list[i + 1] == output_ipa_list[j]:
#             # Adjacent character found, thus violating the constraint
#             print(f"Adjacent characters found at index {i} in {input_ipa} and index {j} in {output_ipa}")
#             return False
#         i += 1

#     # If the entire output_word is checked
#     print(f"Entire output_word checked")
#     return j == len(output_ipa_list)

@constraint
def noSkipping(input_word, output_word):
    """
    Use instead of noSkippingIPA() for now!
    This function is at least consistent with how we came to understand the NoSkipping constraint.
    Check if the output_word can be generated from the input_word without skipping any characters. 
    Returns True if the entire output_word is checked, otherwise False.
    """
    i, j = 0, 0
    while i < len(input_word) and j < len(output_word):
        if input_word[i] == output_word[j]:
            j += 1
        elif i > 0 and i < len(input_word) - 1 and input_word[i - 1] == output_word[j - 1] and input_word[i + 1] == output_word[j]:
            # Adjacent character found, thus violating the constraint
            return False
        i += 1

    # If the entire output_word is checked
    return j == len(output_word)

@constraint
def maxSonorityRise(input_word):
    """
    This function finds the maximum sonority rise between the onset consonant and the peak
    (vowel) of the syllable. It compares the sonority profiles of the onset consonant-vowel (CV)
    sequences in the output and returns the input segment that creates the greatest sonority rise
    from the consonant directly preceding the vowel to the vowel.
    """
    vowels = 'aeiou'
    max_sonority_diff = -1
    best_consonant = ''
    peak_vowel = ''

    # Find the first vowel which is considered the peak of the syllable
    for i, c in enumerate(input_word):
        if c in vowels:
            peak_vowel = c
            break

    if peak_vowel:
        # Find the onset consonant with the maximum sonority rise to the peak vowel
        for j in range(i):
            consonant = input_word[j]
            diff = sonority_scale(peak_vowel) - sonority_scale(consonant)
            if diff > max_sonority_diff:
                max_sonority_diff = diff
                best_consonant = consonant

    return best_consonant + peak_vowel if best_consonant else ''

# Helper functions

def sonority_scale(letter):
    """Assigns a sonority value to a letter according to the Modified Sonority Rating (MSR) scale."""
    msr_sonority_hierarchy = {
        'a': 8, 'e': 8, 'i': 8, 'o': 8, 'u': 8,  # Vowels
        'm': 7, 'n': 7, 'ŋ': 7,                   # Nasals
        'l': 6, 'r': 6,                           # Liquids
        'j': 5, 'w': 5,                           # Glides
        'z': 4, 'v': 4, 'ð': 4,                   # Voiced fricatives
        'b': 3, 'd': 3, 'g': 3,                   # Voiced stops
        'p': 2, 't': 2, 'k': 2,                   # Voiceless stops
        'f': 1, 's': 1, 'ʃ': 1, 'θ': 1, 'h': 1    # Voiceless fricatives
    }
    return msr_sonority_hierarchy.get(letter.lower(), -1)
def compare_sounds(input_word, output_word):

    # Convert the input and output words to IPA
    input_ipa = word_to_ipa(input_word)
    output_ipa = word_to_ipa(output_word)
    
    # Split the IPA representation into individual sounds
    input_sounds = input_ipa.split()
    output_sounds = output_ipa.split()

    output_index = 0
    for sound in input_sounds:
        if output_index >= len(output_sounds):
            return False
        try:
            # Find the sound in the output, starting from the current index
            output_index = output_sounds.index(sound, output_index) + 1
        except ValueError:
            return False  # Sound not found in output
    
    return True
def word_to_ipa(input_word):
    """
    Converts a word to its IPA representation.
    
    Args:
        input_word (str): The word to be converted.
        
    Returns:
        str: The word in IPA representation.
    """
    return e2i.convert(input_word)
def gen(input_word):
    """
    Generates a list of output candidates based on the input word, following the principles of Optimality Theory.
    
    This function assumes "richness of the base", meaning it generates candidates without language-specific input restrictions.
    It handles inputs with complex clusters and generates candidates that may include epenthesis or deletion strategies.
    
    Args:
        input_word (str): The word to generate output candidates for.
        
    Returns:
        list: A list of possible output words (candidates).
    """
    candidates = []
    # Epenthesis candidates: insert a vowel after each consonant
    for vowel in vowels:
        for i in range(len(input_word) + 1):
            candidate = input_word[:i] + vowel + input_word[i:]
            candidates.append(candidate)
    
    # Deletion candidates: delete each consonant one by one
    for i in range(len(input_word)):
        if input_word[i].lower() in consonants:
            candidate = input_word[:i] + input_word[i+1:]
            candidates.append(candidate)
    
    # Allow original word as a possible candidate
    candidates.append(input_word)
    
    # Remove duplicates before returning
    return list(set(candidates))
def gather_input_words():
    """
    Gathers multiple words from the user to generate a list for constraint testing.
    
    This function prompts the user to enter words one by one and adds them to a list.
    The user can stop the process by entering 'exit'.
    
    Returns:
        list: A list of words collected from the user.
    """
    input_words = []
    print("Enter words for constraint testing (type 'exit' to finish):")
    
    while True:
        word = input("Enter a word: ").strip()
        if word.lower() == 'exit':
            break
        input_words.append(word)
    
    return input_words

# if run as _main_

test_cases = [
    ("snow", "sno"),
    ("snow", "sow"),
    ("snow", "so"),
    ("snow", "no"),
    ("ski", "si"),
    ("ski", "ki")
]

if __name__ == "__main__":

    #test get constraint functions
    for func in get_constraint_functions():
        print(func.__name__)

    # for i in test_cases:
    #     print("Input: " + i[0] + " Output: " + i[1])
    #     #print("NoSkipping: " + str(noSkipping(i[0], i[1])))
    #     print("MSR: " + str(maxSonorityRise(i[1])))

    # Example usagesno
    #while True:
        # print("Input a word: ")
        # inputWord = input()
        # print("Input output word: ")
        # outputWord = input()
        # if inputWord == "exit":
        #     break
        # #outputs = gen(inputWord)
        # #print(noSkippingIPA(inputWord, outputWord))
        # print(word_to_ipa(inputWord))
        # print(word_to_ipa(outputWord))

        #Test noSkipping 


        #print("Output Candidates: " + str(outputs))
        #print("*CC: " + str(starCC(inputWord)))
        #print("NoDiphthong: " + str(noDiphthong(inputWord)))




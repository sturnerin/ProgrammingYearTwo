#выбрать букву
#просить ввести
#буква или нет?
#угадано или нет?
#левее или правее?

import random

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z']
def pickletter():
    letter = random.choice(alphabet)
    print(letter)
    return letter

def tryandguess(letter):
    trial = 1
    numletter = alphabet.index(letter)
    while trial != letter:
        trial = input('print a letter: ')
        numtrial = alphabet.index(trial)
        if trial not in alphabet:
            print('not a letter')
        elif numletter < numtrial:
            print('to the left')
        elif numletter > numtrial:
            print('to the right')
    print('cool!')
    return

letter = pickletter()
tryandguess(letter)

import unittest
# -*- coding: utf-8 -*-


# Given a string and a non-negative int n, return a larger string
# that is n copies of the original string.

def string_times(string, n):
    return string * n

# Given an array of ints, return True if one of the first 4 elements
# in the array is a 9. The array length may be less than 4.
def array_front9(nums):
    result = False
    length = min(len(nums), 4)
    for i in range(length):
        if nums[i] == 9:
            result = True
            break
    return result

# Given a string, return the count of the number of times
# that a substring length 2 appears  in the string and also as
# the last 2 chars of the string, so "hixxxhi" yields 1 (we won't count the end substring).
def last2(string):
    result = 0
    for i in range(len(string)-2):
        if string[-2:] == string[i:i+2]:
            result += 1
    return result

#Write a proramm that returna dictionary of occurences of the alphabet for a given string.
# Test it with the Lorem upsuj
# text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
def occurences(text):
    result_dict = {}
    for i in text.lower():
        if i in result_dict.keys():
            result_dict[i] += 1
        else:
            result_dict[i] = 1
    return result_dict

# print(occurences(text))

#Write a program that maps a list of words into a list of
#integers representing the lengths of the correponding words.
def length_words(array):
    result = []
    for i in range(len(array)):
        result += [len(array[i])]
    return result


#Write a function that takes a number and returns a list of its digits.
def number2digits(number):
    result = [int(digit) for digit in str(number)]
    return result


#Write function that translates a text to Pig Latin and back.
#English is translated to Pig Latin by taking the first letter of every word,
#moving it to the end of the word and adding 'ay'
def pigLatin(text):
    text_list = text.split(" ")
    translated_text = text_list[0][1:].capitalize() + text_list[0][0].lower() + 'ay '
    for i in range(1, len(text_list[1:])):
         translated_text += text_list[i][1:] + text_list[i][0] + 'ay '
    translated_text += text_list[-1][1:] + text_list[-1][0] + 'ay'
    return "".join(translated_text)


#write fizbuzz programm
# Write a program that prints the numbers from 1 to 100. But for multiples of three print “Fizz” instead of the number
# and for the multiples of five print “Buzz”. For numbers which are multiples of both three and five print “FizzBuzz”."
def fizbuzz():
    for number in range(100):
        if number % 15 == 0:
            print("FizzBuzz")

        elif number % 3 == 0:
            print("Fizz")

        elif number % 5 == 0:
            print("Buzz")

        else:
            print(number)
    return


response = {
  "nhits": 1000,
  "parameters": {},
  "records": [
    {
      "datasetid": "les-1000-titres-les-plus-reserves-dans-les-bibliotheques-de-pret",
      "recordid": "4b950c1ac5459379633d74ed2ef7f1c7f5cc3a10",
      "fields": {
        "nombre_de_reservations": 1094,
        "url_de_la_fiche_de_l_oeuvre": "https://bibliotheques.paris.fr/Default/doc/SYRACUSE/1009613",
        "url_de_la_fiche_de_l_auteur": "https://bibliotheques.paris.fr/Default/doc/SYRACUSE/1009613",
        "support": "indéterminé",
        "auteur": "Enders, Giulia",
        "titre": "Le charme discret de l'intestin [Texte imprimé] : tout sur un organe mal aimé"
      },
      "record_timestamp": "2017-01-26T11:17:33+00:00"
    },
    {
      "datasetid":"les-1000-titres-les-plus-reserves-dans-les-bibliotheques-de-pret",
      "recordid":"3df76bd20ab5dc902d0c8e5219dbefe9319c5eef",
      "fields":{
        "nombre_de_reservations":746,
        "url_de_la_fiche_de_l_oeuvre":"https://bibliotheques.paris.fr/Default/doc/SYRACUSE/1016593",
        "url_de_la_fiche_de_l_auteur":"https://bibliotheques.paris.fr/Default/doc/SYRACUSE/1016593",
        "support":"Bande dessinée pour adulte",
        "auteur":"Sattouf, Riad",
        "titre":"L'Arabe du futur [Texte imprimé]. 2. Une jeunesse au Moyen-Orient, 1984-1985"
      },
      "record_timestamp":"2017-01-26T11:17:33+00:00"
    },
  ]
}

#Given the above response object extract a array of records with columns nombre_de_reservations , auteur and timestamp
import json
def flatten():
    parsed_json = json.loads(response)
    result_array = []
    record_1 = parsed_json[records][0]
    record_2 = parsed_json[records][1]
    result_array = [record_1["nombre_de_reservations"], record_1["fields"]["auteur"], record_1["record_timestamp"]]
    result_array.append([record_2["nombre_de_reservations"], record_2["fields"]["auteur"], record_2["record_timestamp"]])
    return result_array


# Here's our "unit tests".
class Lesson1Tests(unittest.TestCase):
    fizbuzz()
    def testArrayFront9(self):
        self.assertEqual(array_front9([1, 2, 9, 3, 4]) , True)
        self.assertEqual(array_front9([1, 2, 3, 4, 9]) , False)
        self.assertEqual(array_front9([1, 2, 3, 4, 5]) , False)

    def testStringTimes(self):
        self.assertEqual(string_times('Hel', 2),'HelHel' )
        self.assertEqual(string_times('Toto', 1),'Toto' )
        self.assertEqual(string_times('P', 4),'PPPP' )

    def testLast2(self):
        self.assertEqual(last2('hixxhi') , 1)
        self.assertEqual(last2('xaxxaxaxx') , 1)
        self.assertEqual(last2('axxxaaxx') , 2)

    def testLengthWord(self):
        self.assertEqual(length_words(['hello','toto']) , [5,4])
        self.assertEqual(length_words(['s','ss','59fk','flkj3']) , [1,2,4,5])

    def testNumber2Digits(self):
        self.assertEqual(number2digits(8849) , [8,8,4,9])
        self.assertEqual(number2digits(4985098) , [4,9,8,5,0,9,8])

    def testPigLatin(self):
        self.assertEqual(pigLatin("The quick brown fox") , "Hetay uickqay rownbay oxfay")



def main():
    unittest.main()

if __name__ == '__main__':
    main()

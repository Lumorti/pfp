#! /usr/bin/env python3

import os
import sys
from random import randint

phraseList = []
wordList = {}

wordFolder = "/usr/local/share/pfp/dicts/"
phraseFolder = "/usr/local/share/pfp/phrases/"

badSwaps = ["that", "the", "a", "an", "it", "those", "this"]

verbose = 0
monochrome = True
listAll = False
quiet = False
justChecking = False
justWord = False
randomOrder = False
maxOutput = 0
wordToUse = ""

brightRed = "\033[91m"
brightGreen = "\033[92m"''
brightYellow = "\033[93m"
normalRed = "\033[31m"
normalGreen = "\033[32m"
normalYellow = "\033[33m"

# Load a list of phrases by filename, turning each into phonemes
def loadPhrases(filename):

    filename = filename.replace("//", "/")

    with open(filename, "r") as phraseFile:

        currentOrigin = ""

        for line in phraseFile:

            if len(line.strip()) <= 1: continue

            if line[0] == "#":
                currentOrigin = line[1:].strip()
                continue

            fixedLine = line.strip()
            fixedLine = fixedLine.replace(",", " , ")
            fixedLine = fixedLine.replace("-", " - ")
            fixedLine = fixedLine.replace(".", " . ")
            fixedLine = fixedLine.replace("?", " ? ")
            fixedLine = fixedLine.replace("!", " ! ")
            fixedLine = fixedLine.replace(":", " : ")

            phraseList.append({"origin": currentOrigin, "file": filename, "original": line.strip(), "words": fixedLine.split(), "phonemes": determinePronunciation(fixedLine)})

# Load a phonetic dictionary by filename
def loadWords(filename):

    filename = filename.replace("//", "/")

    with open(filename, "r", errors='replace') as wordFile:

        for line in wordFile:

            if line[0:3] == ";;;" or line.strip() == "": continue

            split = line.upper().split()
            wordList[split[0]] = split[1:]

# Return an array of phonemes, converting using the word list
def determinePronunciation(phrase):

    phonemes = []

    splitPhrase = phrase.upper().split()

    for word in splitPhrase:

        if word in wordList.keys():

            phonemes.append(wordList[word])

        elif word not in [".", "!", "?", ",", ":", "-"]:

            if not quiet: print("WARNING - unknown word: " + word)
            phonemes.append([])

        else:

            phonemes.append([])

    return phonemes

# Determine the similiarity between two sets of phonemes (0 is none, 1 is partial,  2 is rhyme, 3 is same)
def similiarity(phonemes1, phonemes2):

    shorterLength = min(len(phonemes1), len(phonemes2))

    # Check for same
    if "".join(phonemes1) == "".join(phonemes2):
        return 1

    # Check for rhyme
    i = 1
    same = 0
    while i < shorterLength:

        if phonemes2[len(phonemes2)-i] == phonemes1[len(phonemes1)-i]: same += 1
        else: break
        i += 1

    if (same >= 2) or (same >= 1 and shorterLength <= 2 and len(phonemes1) == len(phonemes2)):
        return 3

    # Check for the word being similiar (e.g. Luke and look)
    if len(phonemes1) == len(phonemes2) and phonemes1[0] == phonemes2[0] and phonemes1[-1] == phonemes2[-1]:
        return 2

    # Check for the word being inside the other word
    if " ".join("phonemes2") in " ".join("phonemes1"):
        return 1

    # Otherwise no similiarity
    return 0

# The main function, generate a list of puns for a word
def generatePuns(word):

    wordPhonemes = determinePronunciation(word)[-1]
    punList = []

    for phrase in phraseList:

        j = 0
        while j < len(phrase["phonemes"]):

            phrasePhonemes = phrase["phonemes"][j]

            if len(phrasePhonemes) > 0:

                sim = similiarity(phrasePhonemes, wordPhonemes)
                if (verbose >= 1 and sim >= 1) or verbose >= 2:

                    print("comparing " + str(phrase["words"][j]) + " " + str(phrasePhonemes) + " and " + str(word) + " " + str(wordPhonemes) + " returns " + str(sim))

                if sim >= 1:

                    if phrase["words"][j].lower() in badSwaps: sim = 1

                    punText = phrase["original"].replace(phrase["words"][j], word).replace(phrase["words"][j].capitalize(), word)
                    punText = punText[0].capitalize() + punText[1:]
                    pun = {"pun": punText, "quality": sim, "origin": phrase["origin"], "originalWord": phrase["words"][j], "file": phrase["file"]}
                    punList.append(pun)
                    break

            j += 1

    return punList

# Process the arguments passed to the program, returning boolean of whether to continue or not
def processArgs(argsList):

    global listAll, monochrome, maxOutput, randomOrder, quiet
    global verbose, justChecking, justWord
    global wordToUse

    i = 0
    while i < len(argsList):

        if argsList[i] in ["-h", "--help", "-help", "--h"]:

            print("------------------------------------------------------------------------")
            print("                               Usage                                    ")
            print("------------------------------------------------------------------------")
            print("                                                                        ")
            print(" pfp [<flags>] <word>     generate a list of puns from a word           ")
            print("                                                                        ")
            print("------------------------------------------------------------------------")
            print("                           General Flags                                ")
            print("------------------------------------------------------------------------")
            print("                                                                        ")
            print(" -h --help                print this help message                       ")
            print(" -d <directory>           specify the dictionary directory              ")
            print(" -p <directory>           specify the phrase directory                  ")
            print("                                                                        ")
            print("------------------------------------------------------------------------")
            print("                           Output Flags                                 ")
            print("------------------------------------------------------------------------")
            print("                                                                        ")
            print(" -l --list                list extra info about each pun                ")
            print(" -m --max <max puns>      limit the amount of puns                      ")
            print(" -r --random              randomise the order of puns                   ")
            print(" -c --colour --color      coloured output (ANSI)                        ")
            print(" -t --quality <min qual>  only output puns above a certain quality      ")
            print(" -q --quiet               don't print warnings                          ")
            print("                                                                        ")
            print("------------------------------------------------------------------------")
            print("                          Debugging Flags                               ")
            print("------------------------------------------------------------------------")
            print("                                                                        ")
            print(" -v --verbose             verbose output                                ")
            print(" -vv --vverbose           extra verbose output, warning: outputs a lot  ")
            print(" -w --word                output the phonemes for a word, no puns       ")
            print(" -j --check               just check the files for errors, no puns      ")
            print("                                                                        ")
            return False

        elif argsList[i] in ["-d"]:

            if os.path.isdir(argsList[i+1]):

                global wordFolder
                wordFolder = argsList[i+1]

                i += 1

            else: print("ERROR - not a valid directory: " + argsList[i+1])

        elif argsList[i] in ["-p"]:

            if os.path.isdir(argsList[i+1]):

                global phraseFolder
                phraseFolder = argsList[i+1]

                i += 1

            else: print("ERROR - not a valid directory: " + argsList[i+1])

        elif argsList[i] in ["-m"]:

            if isInt(argsList[i+1]):

                maxOutput = int(argsList[i+1])

                i += 1

            else: print("ERROR - not a valid integer: " + argsList[i+1])

        elif argsList[i] in ["-v", "--verbose"]: verbose += 1
        elif argsList[i] in ["-c", "--colour", "--color"]: monochrome = False
        elif argsList[i] in ["-l", "--list"]: listAll = True
        elif argsList[i] in ["-q", "--quiet"]: quiet = True
        elif argsList[i] in ["-j", "--check"]: justChecking = True
        elif argsList[i] in ["-w", "--word"]: justWord = True
        elif argsList[i] in ["-r", "--random"]: randomOrder = True
        elif argsList[i] in ["-t", "--quality"]: minQuality = True

        # If mutliple options are given as one flag, split them and recurse
        elif argsList[i][0] == "-" and argsList[i][1] != "-":

            newArgString = ""
            for char in argsList[i][1:]:

                if char not in ["l", "q", "v", "c", "w", "r", "j"]:

                    print("ERROR - not a valid flag: -" + char)
                    return False

                newArgString += "-" + char + " "

            processArgs(newArgString.strip().split())

        elif argsList[i][0:2] == "--":

            print("ERROR - not a valid flag: -" + argsList[i][3:])
            return False

        else:

            wordToUse += argsList[i] + " "

        i += 1


    return True

def isInt(string):

    try:
        int(string)
        return True
    except Exception as e:
        return False

def sortFunction(pun):

    return - 10000 * pun["quality"] + len(pun["pun"])

if __name__ == "__main__":

    # Ensure a word is given
    if len(sys.argv) <= 1:

        processArgs(["--help"])
        exit()

    # Process any other arguments
    if not processArgs(sys.argv[1:len(sys.argv)]): exit()

    wordToUse = wordToUse.strip()

    # Ensure there's a word to make puns from
    if len(wordToUse.strip()) <= 1 and not justChecking:

        print("ERROR - please specify a word to generate puns from")
        exit()

    # Load the dictionaries
    if not os.path.isdir(wordFolder): wordFolder = "./dicts"
    if not os.path.isdir(wordFolder): print("ERROR - not a valid directory: " + wordFolder)
    wordFiles = os.listdir(wordFolder)
    for file in wordFiles: loadWords(wordFolder + "/" + file)

    # Load the phrase lists
    if not os.path.isdir(phraseFolder): phraseFolder = "./phrases"
    if not os.path.isdir(phraseFolder): print("ERROR - not a valid directory: " + phraseFolder)
    phraseFile = os.listdir(phraseFolder)
    for file in phraseFile: loadPhrases(phraseFolder + "/" + file)

    # Output if verbose mode is specified
    if verbose >= 1:
        print("Loaded " + str(len(wordList)) + " words")
        print("Loaded " + str(len(phraseList)) + " phrases")

    wordsGiven = wordToUse.split()

    puns = []

    for word in wordsGiven:

        phonemes = determinePronunciation(word)[-1]

        if len(phonemes) <= 0:
            print("ERROR - given word not in dictionary so cannot continue")
            exit()

        if justWord:
            print("Pronounciation of " + word + " is " + str(phonemes))
            exit()

        if justChecking: exit()

        if verbose >= 1:
            print("Generating puns for: " + word + str(phonemes))

        # Generate puns and output
        punsList = generatePuns(word)
        puns.extend(punsList)

    puns.sort(key=sortFunction)

    if verbose >= 1:
        print("---------------------------------------------------------------------")

    for i in range(len(puns)):

        if not randomOrder:
            punIndex = 0
        else:
            punIndex = randint(0, len(puns)-1)

        pun = puns.pop(punIndex)

        colorCode = ""
        if not monochrome:

            if pun["quality"] == 3: colorCode = brightGreen
            elif pun["quality"] == 2: colorCode = brightYellow
            elif pun["quality"] == 1: colorCode = brightRed

        if listAll:

            print(colorCode + str(pun["pun"]) + " (replaced: '" + str(pun["originalWord"]) + "', origin: " + str(pun["origin"]) + ", quality: " + str(pun["quality"]) + ")")

        else:

            print(colorCode + str(pun["pun"]))

        if maxOutput is not 0 and i >= maxOutput-1: break

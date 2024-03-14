from pdfminer.high_level import extract_pages, extract_text
import re
import csv

def getBlankDict():
    return dict(jurisdiction='N/A', office='N/A', division='N/A', term='N/A', pick='N/A', duration='N/A', first='N/A', middle='N/A', last='N/A', suffix='N/A',
                      party='N/A', filed='N/A', valid='N/A', address='N/A', zip='N/A', email='N/A', phone='N/A', phone2='N/A')

def writeCSVLines(personListingList):
    with open('output.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Jurisdiction', 'Office', 'Division/District', 'Term', 'Pick', 'Duration', 'Ward', 'Pct', 'City', 'First', 'Middle', 'Last', 'Suffix', 'Party', 'Filed', 'Valid', 'Address', 'Zip', 'Email', 'Phone', 'Phone2'])

        for person in personListingList:
            filewriter.writerow([person.get('jurisdiction'),person.get('office'),person.get('division'),person.get('term'),person.get('pick'),person.get('duration'),person.get('ward'),person.get('pct'),person.get('city'),person.get('first'),person.get('middle'),person.get('last'),person.get('suffix'),person.get('party'),person.get('filed'),person.get('valid'),person.get('address'),person.get('zip'),person.get('email'),person.get('phone'),person.get('phone2')])

class PersonListing:
    def __init__(self, jurisdiction, office, division, term, pick, duration, ward, pct, city, first, middle, last, suffix, party, filed, valid, address, zip, email, phone, phone2):
        self.jurisdiction = jurisdiction
        self.office = office
        self.division = division
        self.term = term
        self.pick = pick
        self.duration = duration
        self.ward = ward
        self.pct = pct
        self.city = city
        self.first = first
        self.middle = middle
        self.last = last
        self.suffix = suffix
        self.party = party
        self.filed = filed
        self.valid = valid
        self.address = address
        self.zip = zip
        self.email = email
        self.phone = phone
        self.phone2 = phone2

def parseName(inputString):
    print(inputString)
    firstName = ""
    middleName = ""
    lastName = ""
    suffix = ""
    splitString = inputString.split(" ")
    firstName = splitString[0]
    ALLOWED_SUFFIXES = ['Sr', 'Sr.', 'Jr', 'Jr.', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    if len(splitString) == 4:
        if splitString[3] in ALLOWED_SUFFIXES: #only allow these suffixes
            middleName = splitString[1]
            lastName = splitString[2]
            suffix = splitString[3]
        else:
            middleName = splitString[1]
            lastName = splitString[2] + ' ' + splitString[3]
    elif len(splitString) == 3:
        if '.' in splitString[1] or 1==1:
            middleName = splitString[1]
            lastName = splitString[2]
        # else:
        #     lastName = splitString[1]
        #     suffix = splitString[2][:-1]
    elif len(splitString) == 2:
        lastName = splitString[1]
    #print([firstName,middleName,lastName,suffix],'\n')
    return [firstName,middleName,lastName,suffix]


text = extract_text("csv/2024_Candidate_Contact_Info_1.2.24_all_2.pdf")
#print(text)
rawExtractedText = text.split('\n\n')
#filter out useless lines
IGNORED_WORDS = ['/ 139 ', 'Candidates with same name: ', 'Total Filed: ', 'Total Candidates: ', 'Total Contests: ','Los nombres de los candidatos que se retiren a menos de 70 días antes del día de las elecciones  serán impresos en la paeleta.','PRESIDENTIAL PRIMARY ELECTION Candidate List','']

for i in range(len(rawExtractedText)):
    rawExtractedText[i] = rawExtractedText[i].replace('\n',' ')
    #print('##',rawExtractedText[i],'##')

for i in range(6):
    IGNORED_WORDS.append(rawExtractedText[i])

print(IGNORED_WORDS)
listJurisdiction,listOffice,listDivision,listTerm,listDuration,listPick,listFirst,listMiddle,listLast,listSuffix,\
listParty,listFiled,listValid,listEmail,listPhone,listPhone2,listZip,listAddress, = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
listHeaderStuff = []
listFullNames = []
prevMatched = 0
extractedTextLineCount = 0
addressLineFoundOn = 0
currentHeaderStuff, currentPick, currentDuration = 'N/A','N/A','N/A'
for line in rawExtractedText:
    # remove useless lines
    if line in IGNORED_WORDS:
        #rawExtractedText.remove(line)
        extractedTextLineCount+=1
        continue
    # remove useless lines
    if ' / 139' in line or 'Candidates with same name: ' in line or 'Total Filed: ' in line or 'Total Candidates: ' in line or 'Total Contests: ' in line or 'Candidate Name | Nombre del Candidato' in line or 'Party | Partido' in line or 'Valid | Válido' in line or 'Junta Electoral del Condado de Cuyahoga' in line or 'Filed | Presentada' in line: #ignore line
        extractedTextLineCount += 1
        continue
    # collect validity
    if 'Yes | Sí' in line:
        listValid.append('Yes')
        extractedTextLineCount+=1
        continue
    if 'Yes - Write-In' in line:
        listValid.append('Yes - Write In')
        extractedTextLineCount+=1
        continue
    if 'Removed by Board action |' in line:
        listValid.append('Removed by board action')
        extractedTextLineCount+=1
        continue
    if 'Withdrawn ' in line and 'Retirado ' in line:
        listValid.append(line[:line.find('Retirado')-1])
        extractedTextLineCount+=1
        continue
    # collect party
    if 'Republican | Republicana' in line:
        listParty.append('Republican')
        extractedTextLineCount+=1
        continue
    if 'Democratic | Demócrata' in line:
        listParty.append('Democrat')
        extractedTextLineCount+=1
        continue
    if 'Nonpartisan |' in line:
        listParty.append('Nonpartisan')
        extractedTextLineCount+=1
        continue
    # collect PI
    if re.match('.*(?:^|\D)(\d{5})(?!\d).*', line) or 'Redacted' in line: #if zip code in line (5 consecutive numbers)
        lineNoExtraSpace = re.sub(' +', ' ', line)
        listAddress.append(lineNoExtraSpace)
        # need to check for a stray phone number in case of no email, it makes phone numbers and address on different lines
        addressLineFoundOn = extractedTextLineCount
        extractedTextLineCount+=1
        continue
    if extractedTextLineCount == addressLineFoundOn+1: #check for phone number after address line
        if re.match('^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',line):
            listAddress[len(listAddress)-1] = listAddress[len(listAddress)-1]+" "+line
            extractedTextLineCount+=1
            continue

    # collect file date
    if '/' in line and ' ' not in line: # exclude spaces to avoid lines like '(Full Term Commencing 1/1/2025)'  term
        listFiled.append(line)
        extractedTextLineCount+=1
        continue
    ### store header, pick, and duration and use them for future entries until another one is read
    # collect duration and pick
    if 'Year Term Período' in line:
        currentDuration = line[0]
        #listDuration.append(line[0]) #first char in line is year number
        # third number that appears in line is the vote count number
        indexOfThirdNumber = re.match('\d[A-zñíá ]+\d[A-zñíá ]+\d', line).span()[1]
        thirdNumberValue = line[indexOfThirdNumber-1]
        currentPick = thirdNumberValue
        #listPick.append(thirdNumberValue)
        extractedTextLineCount+=1
        continue
    # collect jurisdiction/office/division line
    if re.match('.*\d+.*',line):
        if prevMatched == 1: #ignore the spanish
            prevMatched = 0
            continue
        currentHeaderStuff = line.replace(',',' ')
        #listHeaderStuff.append(line)
        prevMatched = 1
        continue
    # only lines left are the names:
    listFullNames.append(line)
    # add current header the name is under
    listHeaderStuff.append(currentHeaderStuff)
    listDuration.append(currentDuration)
    listPick.append(currentPick)

    extractedTextLineCount+=1
    #print('##',line,'##')

# Parse full names into first, middle, last, suffix
for fullname in listFullNames:
    nameInfo = parseName(fullname)
    listFirst.append(nameInfo[0])
    listMiddle.append(nameInfo[1])
    listLast.append(nameInfo[2])
    listSuffix.append(nameInfo[3])

# parse header stuff in to jurisdiction, office, division, and term
listJurisdiction = ['N/A'] * len(listHeaderStuff)
listDivision = ['N/A'] * len(listHeaderStuff)
listTerm = ['N/A'] * len(listHeaderStuff)
listOffice = ['N/A'] * len(listHeaderStuff)
listCity = ['N/A'] * len(listHeaderStuff)
listWard = ['N/A'] * len(listHeaderStuff)
listPct = ['N/A'] * len(listHeaderStuff)
for i in range(len(listHeaderStuff)):
    splitHeaderStuff = listHeaderStuff[i].split("(")
    splitFirstTwoLines = splitHeaderStuff[0].split('For ')
    listJurisdiction[i] = splitFirstTwoLines[0][:-1]
    listOffice[i] = splitFirstTwoLines[1]
    print(splitHeaderStuff)
    print(len(splitHeaderStuff))
    if len(splitHeaderStuff) == 3:
        #listDivision[i] = splitHeaderStuff[1][:-1] # [:-1] to remove ending ')'
        listDivision[i] = listDivision[i].replace('(','')
        listDivision[i] = listDivision[i].replace(')','')
        listTerm[i] = splitHeaderStuff[2][:-1]
    elif len(splitHeaderStuff) == 2:
        if ' Term ' in splitHeaderStuff[1]:
            listDivision[i] = 'N/A'
            listTerm[i] = splitHeaderStuff[1][:-1]
        else:
            listDivision[i] = splitHeaderStuff[1][:-1]
            listTerm[i] = 'N/A'
    if 'Member of County Central Committee' in listOffice[i]:
        currentCombined = listJurisdiction[i].strip()
        listPct[i] = currentCombined[len(currentCombined)-1]
        listWard[i] = currentCombined[len(currentCombined)-5:len(currentCombined)-3]
        listCity[i] = currentCombined[:len(currentCombined)-6]

# Split up PI from listAddress to email and phone numbers
listZip = ['N/A'] * len(listAddress)
listPhone = ['N/A'] * len(listAddress)
listPhone2 = ['N/A'] * len(listAddress)
listEmail = ['N/A'] * len(listAddress)
for i in range(len(listAddress)):
    currentPI = listAddress[i]
    print(f"\n\n=======Current PI is {currentPI}==========")
    if 'Information Redacted' in currentPI:

        listZip[i] = 'Information Redacted'
        listPhone[i] = 'Information Redacted'
        listPhone2[i] = 'Information Redacted'
        listEmail[i] = 'Information Redacted'
        continue
    # extract email
    indexOfEmailStart = 0
    indexOfEmailEnd = 0
    indexOfPhoneStart2 = -1
    indexOfAt = currentPI.find('@')
    tempPhone2 = 'N/A'
    if indexOfAt == -1:
        listEmail[i] = 'N/A'
    else:
        if '@ohioansdefendingfreed ' in currentPI: #this email in particular is too long for the parser to put on one line, so put it on one line manually for it
            currentPI = currentPI.replace('@ohioansdefendingfreed ', '@ohioansdefendingfreed')
        indexOfEmailStart = currentPI[:indexOfAt].rfind(' ')
        currentPI += ' '
        indexOfEmailEnd = currentPI[indexOfAt:len(currentPI)].find(' ') + len(currentPI[0:indexOfAt])
        listEmail[i] = currentPI[indexOfEmailStart:indexOfEmailEnd].strip()
        currentPI = currentPI[:indexOfEmailStart] + currentPI[indexOfEmailEnd:]
        # print(f"----------\nfinds:{indexOfEmailStart},{indexOfEmailEnd}")
        print("pi after extract email: [",currentPI,"]")
        # print("email: [", listEmail[i],"]")
    # extract phone numbers
    if re.match('^.*[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}.*$',currentPI): # if phone number in currentPI
        print("U HAVE A PHONE NUMBER")
        indexOfPhoneStart = currentPI.rfind('-') - 7 # last dash in line is for phone numbers, 7 characters back is start
        tempPhone1 = currentPI[indexOfPhoneStart:]
        currentPI = currentPI[:indexOfPhoneStart]
        # check for second phone number
        if re.match('^.*[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}.*$',currentPI):
            indexOfPhoneStart2 = currentPI.rfind('-') - 7
            tempPhone2 = currentPI[indexOfPhoneStart2:]
            currentPI = currentPI[:indexOfPhoneStart2]
        if indexOfPhoneStart2 != -1: # because we look for the last phone number in the string first, swap the order around if it exists
            listPhone[i] = tempPhone2
            listPhone2[i] = tempPhone1
        else:
            listPhone[i] = tempPhone1
        # print(f"ur phones are {listPhone[i],listPhone2[i]}")
        # print(f"current pi is {currentPI}")
    else:
        listPhone[i] = 'N/A'
        listPhone2[i] = 'N/A'
    currentPI = currentPI.strip()
    # extract zip
    indexOfZipStart = currentPI.rfind(' ')
    listAddress[i] = currentPI[:indexOfZipStart]
    listZip[i] = currentPI[indexOfZipStart:]







listOfPeople = []
# Write each person to csv
for i in range(len(listAddress)):
    #print('start')
#jurisdiction, office, division, term, pick, duration, first, middle, last, suffix, party, filed, valid, address, zip, email, phone, phone2):
    currentPerson = getBlankDict()
    currentPerson['jurisdiction'] = listJurisdiction[i]
    currentPerson['office'] = listOffice[i]
    currentPerson['division'] = listDivision[i]
    currentPerson['term'] = listTerm[i]
    currentPerson['pick'] = listPick[i]
    currentPerson['duration'] = listDuration[i]
    currentPerson['ward'] = listWard[i]
    currentPerson['city'] = listCity[i]
    currentPerson['pct'] = listPct[i]
    currentPerson['first'] = listFirst[i]
    currentPerson['middle'] = listMiddle[i]
    currentPerson['last'] = listLast[i]
    currentPerson['suffix'] = listSuffix[i]
    currentPerson['party'] = listParty[i]
    currentPerson['filed'] = listFiled[i]
    currentPerson['valid'] = listValid[i]
    currentPerson['address'] = listAddress[i]
    currentPerson['zip'] = listZip[i]
    currentPerson['email'] = listEmail[i]
    currentPerson['phone'] = listPhone[i]
    currentPerson['phone2'] = listPhone2[i]
    #print(f"Adding current person:{currentPerson}")
    listOfPeople.append(currentPerson)
writeCSVLines(listOfPeople)

# for line in rawExtractedText:
#     print('##',line,'##')
# print('------------------------------------------------------\n\n\n')
# print(len(listAddress),' address')
# print(len(listFiled), ' filed')
# print(len(listValid), ' valid')
# print(len(listFullNames), ' full names')
# print(len(listParty), ' party')
# print(len(listHeaderStuff), ' header stuff')
# print(len(listPick), ' pick')
# print(len(listDuration), ' duration')
# print(listJurisdiction)
# print(listTerm)
# print(listDivision)
# print(len(listJurisdiction))
# print('----')
# print(listWard)
# print(listCity)
# print(listPct)
# print(len(listCity))
#if read address: check for email and phone1/2 following it
#following line will be the area

#information redacted:
#after yes | si, if no address (likely a name will be there instead), then its information redacted

# Division:  General
# Term(?):  Full Term Commencing 1/11/2025
# Duration:  6 Year Term
# Pick:  Not more than 1
# First:
# Middle:
# Last:
# Suffix:
# Party:
# Filed:
# Valid:
# Phone:
# Email:

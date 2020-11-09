

#Author: Emanuel Durmaz


from blockchain import blockexplorer
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import utils
import re

class TxSent:
    def __init__(self, date, txVal):
        self.date = date

        if(txVal < 0):
            self.txVal = txVal * -1
        else:
            self.txVal = txVal

class TxReceived:
    def __init__(self, date, txVal):
        self.date = date
        self.txVal = txVal

##############################################

def extractTransactionLists(ownAddress):
    TxReceivedList = []
    TxSentList = []

    transactionList = []
    stepsize = 50
    address = blockexplorer.get_address(ownAddress, limit=stepsize)
    nTx = address.n_tx

    for i in range(0, nTx, stepsize):
        print(i)
        address = blockexplorer.get_address(ownAddress, limit=stepsize, offset=i)
        transactionList += address.transactions


    print("No. Tx: " + str(address.n_tx))
    print("len: " + str(len(transactionList)))
    finalBalance = 0
    totalSent = 0
    totalReceived = 0

    for tx in transactionList:
        date = datetime.datetime.fromtimestamp(tx.time)
        dateFormatted = date.strftime('%Y-%m-%d %H:%M:%S')
        print(dateFormatted)
        print(tx.hash)
        print("inputs")
        txVal = 0
        for input in tx.inputs:
            print(str(input.address) + " | value: " + str(input.value))

            if str(input.address) == ownAddress:
                txVal -= input.value

        print("outputs")
        for output in tx.outputs:
            print(str(output.address) + " | value: " + str(output.value) + " | " + str(output.spent))

            if str(output.address) == ownAddress:
                txVal += output.value

        if(txVal < 0):
            totalSent -= txVal #negative
            TxSentList.append(TxSent(date, txVal))
        else:
            totalReceived += txVal #positive
            TxReceivedList.append(TxReceived(date, txVal))

        print("txVal: " + str(txVal)) # if negative: sent |txVal|, if positive: received |txVal|
        finalBalance += txVal

        print("#################################################")

    if(address.total_received == totalReceived and
       address.total_sent == totalSent and
       address.final_balance == finalBalance):
        print("OK!")
    else:
        print("ERROR!")

    TxReceivedList.reverse()
    TxSentList.reverse()

    return TxReceivedList, TxSentList


def plotTransactions(TxReceivedList, TxSentList):
    receivedDate = []
    receivedVal = []
    for txReceived in TxReceivedList:
        receivedDate.append(txReceived.date)
        receivedVal.append(txReceived.txVal/100000000.)

    sentDate = []
    sentVal = []
    for txSent in TxSentList:
        sentDate.append(txSent.date)
        sentVal.append(txSent.txVal/100000000.)

    fig = plt.figure(figsize=(10, 7))

    plt.scatter(receivedDate, receivedVal, c="g", s=50, alpha=0.5, marker="^")
    plt.scatter(sentDate, sentVal, c="r" , s=50, alpha=0.5, marker="v")

    #plt.plot(receivedDate, receivedVal,'g.', alpha=0.5) # x,y
    #plt.plot(sentDate, sentVal,'r.', alpha=0.5) #
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator()) #mdates.YearLocator()
    plt.savefig("plotTransactions.pdf", bbox_inches='tight')


    plt.show()


def plotIncome(TxReceivedList):
    receivedDate = []
    balanceStates = []

    totalReceived = 0
    for txReceived in TxReceivedList:
        receivedDate.append(txReceived.date)

        totalReceived += txReceived.txVal
        balanceStates.append(totalReceived/100000000.)

    fig = plt.figure(figsize=(10, 7))
    plt.plot(receivedDate, balanceStates) # x,y
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.savefig("plotIncome.pdf", bbox_inches='tight')
    plt.show()


def sortTxLists(TxReceivedList, TxSentList):
    TxReceivedList.sort(key=lambda x: x.date, reverse=False)
    TxSentList.sort(key=lambda x: x.date, reverse=False)

def extractAddresses(lines):
    addresses = []
    for line in lines:

        address = utils.extractStringBetween(line, "", " |")
        if address == "":
            if(line[-1] == '\n'):
                address = line[:-1]
            else:
                address = line

        address = re.sub(r'[^\x00-\x7f]', r'', address) #remove non-ascii chars
        addresses.append(address)

    filteredSet = set(addresses)
    if len(filteredSet) != len(addresses): #return filtered set if there are any dupes
        return filteredSet

    return addresses




################################ MAIN ################################

#INPUT
#allAddresses = ["1BQZKqdp2CV3QV5nUEsqSg1ygegLmqRygj"]

allAddresses = []
filepaths = [
                "/home/user/TransactionInfos/JigsawVanityAddresses/5976edf04bcb2c717e17d820ebf29b398a90993d2ebf20de5d6f6c1ac5c04e54/5976edf04bcb2c717e17d820ebf29b398a90993d2ebf20de5d6f6c1ac5c04e54_vanityAddresses.txt",
                "/home/user/TransactionInfos/JigsawVanityAddresses/454280128478d0da357e8609d5bef43a601ba18582a96678c0d5e60ceb9b08aa/454280128478d0da357e8609d5bef43a601ba18582a96678c0d5e60ceb9b08aa_vanityAddresses.txt"
             ]

lines = ""
addresses = []
for path in filepaths:
    f = open(path, "r")
    lines = f.readlines()
    #print(lines)
    f.close()
    addresses = extractAddresses(lines)
    print("Read " + str(len(addresses)) + " addresses")
    allAddresses += addresses

print("Total: " + str(len(allAddresses)) + " addresses")

TotalTxReceivedList = []
TotalTxSentList = []

i = 0
for address in allAddresses:
    print("No.: " + str(i) + " | address: " + address)
    i +=1
    TxReceivedList, TxSentList = extractTransactionLists(address) #cut off \n
    TotalTxReceivedList += TxReceivedList
    TotalTxSentList += TxSentList

totalReceived = 0
for txReceived in TotalTxReceivedList:
    totalReceived += txReceived.txVal
totalReceived = totalReceived/100000000.

totalSent = 0
for txSent in TotalTxSentList:
    totalSent += txSent.txVal
totalSent = totalSent / 100000000.

########################################################################
print("Report:")
print("Number of samples: " + str(len(lines)))
print("Number of distinct addresses: " + str(len(addresses)))
print("Total transactions with received bitcoins: " + str(len(TotalTxReceivedList)))
print("Total transactions with sent bitcoins: " + str(len(TotalTxSentList)))
print("Total received bitcoins: " + str(totalReceived))
print("Total sent bitcoins: " + str(totalSent))

sortTxLists(TotalTxReceivedList,TotalTxSentList)

plotIncome(TotalTxReceivedList)
plotTransactions(TotalTxReceivedList, TotalTxSentList)

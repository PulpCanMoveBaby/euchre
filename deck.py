import random

class Deck:  
    def __init__(self):
        self.right = 'RIGHT'
        self.left = 'LEFT'
        self.ace = 'ACE'
        self.trumpname = 'TRUMP'
        self.suits = ['TRUMP', 'SPADES', 'CLUBS', 'HEARTS', 'DIAMONDS']
        self.colors = {'black' : ['SPADES', 'CLUBS'], 'red' : ['HEARTS', 'DIAMONDS']}
        self.facecards = dict(J = 11, Q = 12, K = 13, A = 14)
        self.trumpdict = dict(Q = 23, K = 24, ACE = 25, LEFT = 26, RIGHT = 27)
        self.deckdict = dict(SPADES = [9,10,11,12,13,14], CLUBS = [9,10,11,12,13,14], 
                        HEARTS = [9,10,11,12,13,14],  DIAMONDS = [9,10,11,12,13,14])
        self.fulldeck = []
        for suit in self.deckdict:
            for card in self.deckdict[suit]:
                if card > 10:
                    for key in self.facecards:
                        if card == self.facecards[key]:
                            card = key
                self.fulldeck.append([card, suit])
        self.shuffled = []
        self.trumpcards = []
        self.trump = None

    def istrump(self, trumpsuit):
        self.trump = trumpsuit
        #iterate through the colors to find the right and left bauer
        for suitcolor in self.colors:
            
            #if trump is black or red------------
            if trumpsuit in self.colors[suitcolor]:
                
                #trying out this code to see if i can iterate only once through the deck to make these changes                   
                #if trump is the first suit in list
                rightsuit = 0 if trumpsuit == self.colors[suitcolor][0] else 1
                leftsuit = 0 if rightsuit == 1 else 1
                for i, [num, suit] in enumerate(self.fulldeck):
                    
                    if num == 'J' and suit == self.colors[suitcolor][rightsuit]: #if suit is trump
                        self.fulldeck[i][0] = self.right
                        
                    if num == 'A' and suit == self.colors[suitcolor][rightsuit]:
                        self.fulldeck[i][0] = self.ace

                    if suit == trumpsuit:
                        self.fulldeck[i][1] = self.trumpname

                    if num == 'J' and suit == self.colors[suitcolor][leftsuit]:
                        self.fulldeck[i][0] = self.left
                        self.fulldeck[i][1] = self.trumpname

                    if self.fulldeck[i][1][-5:] == self.trumpname:
                        self.trumpcards.append(self.fulldeck[i])
            
    def resetdeck(self):   #I wonder if just calling self.__init__ to reset the initial state would work here...
        self.fulldeck = []
        self.shuffled = []
        for suit in self.deckdict:
            for card in self.deckdict[suit]:
                if card > 10:
                    for suitkey in self.facecards:
                        if card == self.facecards[suitkey]:
                            card = suitkey
                self.fulldeck.append([card, suit])

    def shuffle(self):
        for i in range(len(self.fulldeck)):
            x = random.choice(self.fulldeck)
            self.fulldeck.remove(x)
            self.shuffled.append(x)
        self.fulldeck = self.shuffled
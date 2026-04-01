from deck import Deck
import random, time

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
    def firstcall(self, turncard, dealer, teammate, observe):
        ans = input("\n\nDo you want to call trump? Enter 'yes' or press any key for no. ")
        print('\n'*30)
        return ans
    def makemove(self, currenttrick, suitled = None):
        res = input("\nThe cards are numbered 1-5 from top to bottom in your hand, which one would you like to play? ")
        options = list((range(1, len(self.hand)+1)))
        options = [str(i) for i in options]
        while res not in options:
            res = input("\nThe cards are numbered 1-5 from top to bottom in your hand, which one would you like to play? ")
        print('\n'*30)
        card = int(res)-1
        currenttrick.append((self.hand[card], self.name))
        self.hand.remove(self.hand[card])
        return currenttrick
       
class Computer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.deck = Deck()
        self.suitscore = {'SPADES': 0, 'CLUBS': 0, 'HEARTS': 0, 'DIAMONDS': 0}
        self.bauers = {'SPADES': 0, 'CLUBS': 0, 'HEARTS': 0, 'DIAMONDS': 0}
        self.trumpvals = {9:1, 10:2, 'Q':3, 'K':4, 'A':5, 'J':8}
        self.offsuitaces = {'SPADES': 0, 'CLUBS': 0, 'HEARTS': 0, 'DIAMONDS': 0}
        self.numcards = {'SPADES': 0, 'CLUBS': 0, 'HEARTS': 0, 'DIAMONDS': 0}
        self.bestsuit = []
        self.evaluated = []
        self.haveright = {'SPADES': False, 'CLUBS': False, 'HEARTS': False, 'DIAMONDS': False}
        self.haveleft = {'SPADES': False, 'CLUBS': False, 'HEARTS': False, 'DIAMONDS': False}
        self.haveace = {'SPADES': False, 'CLUBS': False, 'HEARTS': False, 'DIAMONDS': False}
        self.suitsinhand = []
        self.numtrump, self.numoffaces = 0, 0
        self.right, self.left, self.ace = False, False, False
        self.rightplayed, self.leftplayed, self.aceplayed = False, False, False

    def evaluatePrecall(self):   
        self.evaluated = [] 
        self.numcards = {'SPADES': 0, 'CLUBS': 0, 'HEARTS': 0, 'DIAMONDS': 0} 
        onlyleft = {'SPADES': False, 'CLUBS': False, 'HEARTS': False, 'DIAMONDS': False}
        #evaluate each card in the hand
        for [num, suit] in self.hand:

            #number of cards in each suit
            self.numcards[suit] = self.numcards[suit] + 1

            #get point totals for each suit
            self.suitscore[suit] = self.suitscore[suit] + self.trumpvals[num]
            
            #deal with the bauers
            if num == 'J':  #J Clubs(example)
                color = 'black' if suit in self.deck.colors['black'] else 'red'
                for i in self.deck.colors[color]: 
                    #case where 'J' is the right bauer ('clubs')      
                    if suit == i: # when i = Clubs
                        self.haveright[suit] = True
                        self.bauers[i] = self.bauers[i] + 5
                    
                    #case where 'J' is the left bauer ('spades')
                    else: #when i = Spades
                        # self.haveleft[i] = True
                        self.suitscore[i] = self.suitscore[i] + 7
                        self.bauers[i] = self.bauers[i] + 3

                        if suit in self.suitsinhand: pass
                        else: onlyleft[suit] = True

            #get a list of suits to determine if two suited or three suited
            if suit not in self.suitsinhand:
                self.suitsinhand.append(suit)

            elif suit in self.suitsinhand and onlyleft[suit] == True:
                onlyleft[suit] = False

            #deal with the aces
            if num == 'A':
                self.bauers[suit] = self.bauers[suit] + 1
                for i in self.offsuitaces:
                    if suit != i:
                        self.offsuitaces[i] = self.offsuitaces[i] + 1
                        self.suitscore[i] = self.suitscore[i] + 3

        
        for suit in self.bauers: #9 = all three, 8 = both bauers, 6 = right and ace, 5 = just right, 4 = left and ace, 3 = just left, 1 = just ace
            if self.bauers[suit] == 8:
                self.suitscore[suit] = self.suitscore[suit] + 1 # score for having both bauers


        #deal with the case that the left bauer is the only card in a particular suit for determining if two or three suited
        for suit in self.suitsinhand:
            
            if self.numcards[suit] == 1 and self.haveright[suit] == True:
                color = 'black' if suit in self.deck.colors['black'] else 'red'
                idx = 1 if suit == self.deck.colors[color][0] else 0
                addtosuit = self.deck.colors[color][idx]
                self.suitscore[addtosuit] = self.suitscore[addtosuit] + 0.51

                
            #add to score if one, two, or three suited
            if len(self.suitsinhand) == 3:
                self.suitscore[suit] = self.suitscore[suit] + 0.52
            if len(self.suitsinhand) == 2:
                self.suitscore[suit] = self.suitscore[suit] + 1
            if len(self.suitsinhand) == 1:
                self.suitscore[suit] = self.suitscore[suit] + 1.75

            

        #organize and reorder scores, create an evaluated list with the scores and suits in descending order                      
        for suit in self.suitscore:
            self.bestsuit.append(self.suitscore[suit])
        
        self.bestsuit = sorted(self.bestsuit)
        self.bestsuit.reverse()
        for score in self.bestsuit:            
            for suit in self.suitscore:
                if score == self.suitscore[suit]:
                    self.evaluated.append([suit, score])
                    self.suitscore[suit] = -1

    def evaluatePostcall(self):
        for [num, suit] in self.hand:
            if suit == self.deck.trumpname:
                self.numtrump += 1
            if num == 'A' and suit != self.deck.trumpname:
                self.numoffaces += 1
            if num == self.deck.right:
                self.right = True
            if num == self.deck.left:
                self.left = True
            if num == self.deck.ace:
                self.ace = True

    def firstcall(self, turncard, dealer, teammate, observe):
        # print(self.evaluated)
        potentialcalls = []
        definitecalls = []
        for [suit, score] in self.evaluated:
            if score > 13.6:
                potentialcalls.append(suit)
            if score > 18:
                definitecalls.append(suit)

        if turncard[1] in potentialcalls:
            if turncard[0] != 'J' or turncard[0] == 'J' and dealer == teammate or turncard[1] in definitecalls:
                if observe:  
                    print('\n'*30)
                    print(F"The Turncard: {turncard[0]} {turncard[1]}")
                    # print(self.evaluated) #CHANGE BACK IF ERRORS!!!!!!!!!!!!!!!!!
                    print(F'\n\n{self.name}: Call \n\nTrump is {turncard[1]}\n\n')
                    for i in  range(2):
                        print('-'*25)
                    time.sleep(4)
                return 'yes'

            elif self == dealer:
                if observe:
                    print('\n'*30)
                    print(F"The Turncard: {turncard[0]} {turncard[1]}")
                    # print(self.evaluated)
                    print(F'\n\n{self.name}: The Dealer picked it up. \n\nTrump is {turncard[1]}\n\n')
                    for i in  range(2):
                        print('-'*25)
                    time.sleep(4)
                return 'yes'

        else:
            if observe:
                print('\n'*30)
                print(F"The Turncard: {turncard[0]} {turncard[1]}")
                # print(self.evaluated)
                print(F'\n\n{self.name}: Pass \n\n')
                for i in  range(2):
                    print('-'*25)
                time.sleep(1.5)
            return 'no'

    def checkbauers(self, currenttrick):
        for [i,j],k in currenttrick:
            if i == self.deck.right: 
                self.rightplayed = True

            if i == self.deck.left: 
                self.leftplayed = True

            if i == self.deck.ace: 
                self.aceplayed = True
       
    def evaluatetrick(self, currenttrick, suitled):        
        self.converttonum(currenttrick) #Card num in INTEGER FORM, suits become irrelevant

        #set the high card and trick winner to the first to play
        highcard = currenttrick[0][0][0]
        winner = currenttrick[0][1]

           
        for ([i,j],k) in currenttrick[1:]:
            if i > highcard and j == suitled or i > highcard and i > 14:
                winner = k
                highcard = i
                   
        return winner, highcard #card nums return as INTEGERS

    def makemoveCPU(self, currenttrick, team, caller, suitled=None):
        
        teammate = team[1] if self == team[0] else team[0]
        teammatecalled = False
        if caller == teammate: teammatecalled = True


        #computer leads... -----------------------------------------------------------------
        if len(currenttrick) == 0:      
            #These card values are in INTEGER FORM!!!!!!!!!!!!!!!!!!!!!!!!!
            self.converttonum(self.hand, currenttrick) 
            
            if self.right:   
                self.playcard(currenttrick, cardname=self.deck.trumpdict[self.deck.right]) 
                self.right = False

            elif self.left and teammatecalled:
                self.playcard(currenttrick, cardname=self.deck.trumpdict[self.deck.left])
                self.left = False

            elif self.rightplayed and self.left:
                self.playcard(currenttrick, cardname=self.deck.trumpdict[self.deck.left])
                self.left = False
            
            elif self.rightplayed and self.leftplayed and self.ace:
                self.playcard(currenttrick, cardname=self.deck.trumpdict[self.deck.ace])
                self.ace = False
           
            elif self.numoffaces:                
                self.playcard(currenttrick, cardname = self.deck.facecards['A'])

            elif self.numtrump == len(self.hand):
                findlowtrump = [num for [num,suit] in self.hand]
                self.playcard(currenttrick, cardname = min(findlowtrump),suitname=self.deck.trumpname)


            else:
                self.playcard(currenttrick)
      
        else: 
            self.converttonum(self.hand, currenttrick)
            high = currenttrick[0][0][0]
            winner = currenttrick[0][1]
            followsuit = []
            havetrump = []
            haveace = []

            for [num, suit] in self.hand:
                if suit == suitled:
                    followsuit.append(num)
                elif suit == self.deck.trumpname:
                    havetrump.append(num)
                elif num == self.deck.facecards['A']:
                    haveace.append(suit)
          
            #computer's partner not yet played--------------------------------------------------------------------------
            if len(currenttrick) < 2: #partner hasnt gone yet...
                if followsuit:
                    if max(followsuit) > high:
                        self.playcard(currenttrick, cardname = max(followsuit), suitname = suitled)
                    else:
                        self.playcard(currenttrick, cardname = min(followsuit), suitname = suitled)

                
                elif not followsuit and havetrump:
                    couldplay = [i for i in havetrump if i > high]
                    if teammatecalled:
                        self.playcard(currenttrick, cardname = max(couldplay), suitname = self.deck.trumpname)
                    else:
                        self.playcard(currenttrick, cardname = min(couldplay), suitname = self.deck.trumpname)
                
                else:
                    findlow = [num for [num,suit] in self.hand]
                    self.playcard(currenttrick, cardname = min(findlow))
                           
            #computer's partner already played--------------------------------------------------------------------------
            elif len(currenttrick) > 1:  

                winner, highcard = self.evaluatetrick(currenttrick, suitled)              
                
                if followsuit:
                    if max(followsuit) > highcard and winner != teammate.name:
                        self.playcard(currenttrick,  cardname = max(followsuit), suitname = suitled)
                    else:
                        self.playcard(currenttrick, cardname = min(followsuit), suitname = suitled)

                elif not followsuit and havetrump:                    
                    if winner != teammate.name:
                        couldplay = [i for i in havetrump if i > highcard]

                        if len(currenttrick) == 3 and couldplay:
                            self.playcard(currenttrick, cardname = min(couldplay), suitname = self.deck.trumpname)
                        
                        #if teammate called, play highest trump to try and take at least one trick
                        elif teammatecalled and couldplay:
                            self.playcard(currenttrick, cardname = max(couldplay), suitname = self.deck.trumpname)
                        
                        #if none of the trump in your hand could win, play a low offsuit, or your lowest trump if only have trump
                        elif not couldplay:
                            findlow = [num for [num,suit] in self.hand if suit != self.deck.trumpname]
                            if not findlow:
                                findlow = [num for [num,suit] in self.hand]
                            self.playcard(currenttrick, cardname = min(findlow))
                        
                        #if teammate did not call, take the trick with the lowest trump that will win it
                        else:
                            self.playcard(currenttrick, cardname = min(couldplay), suitname = self.deck.trumpname)
                    
                    #this is if you have trump, dont have to follow suit but your partner has the trick...        
                    else:
                        findlow = [num for [num,suit] in self.hand]
                        self.playcard(currenttrick, cardname = min(findlow))
             
                else:
                    findlow = [num for [num,suit] in self.hand]
                    self.playcard(currenttrick, cardname = min(findlow))
        return currenttrick
    
    def deal(self):
        count = 0
        for i in range(20):
            self.deck.shuffle() 
        for i in range(5):
            self.hand.append(self.deck.fulldeck[count])
            count+=1
        self.farmers = self.deck.fulldeck[-4:]
        self.turncard = self.farmers[0]

    def playcard(self, currenttrick, cardname=None, suitname=None):
        if cardname and suitname:
            card = [[num, suit] for [num,suit] in self.hand if num == cardname and suit == suitname]
            self.hand.remove(card[0]) 
            currenttrick.append((card[0], self.name))
            self.converttostr(self.hand, currenttrick)
            if card[0][0] == self.deck.right: 
                self.right = False
            if card[0][0] == self.deck.left: 
                self.left = False
            if card[0][0] == self.deck.ace: 
                self.ace = False
            if card[0][0] == 'A':
                self.numoffaces = self.numoffaces - 1
            if card[0][1] == self.deck.trumpname:
                self.numtrump = self.numtrump - 1
            return card[0]

        elif cardname:
            card = [[num, suit] for [num,suit] in self.hand if num == cardname] 
            self.hand.remove(card[0]) 
            currenttrick.append((card[0], self.name))
            self.converttostr(self.hand, currenttrick)
            if card[0][0] == self.deck.right: 
                self.right = False
            if card[0][0] == self.deck.left: 
                self.left = False
            if card[0][0] == self.deck.ace: 
                self.ace = False
            if card[0][0] == 'A':
                self.numoffaces = self.numoffaces - 1
            if card[0][1] == self.deck.trumpname:
                self.numtrump = self.numtrump - 1
            return card[0]

        elif len(self.hand) == 1:
            currenttrick.append((self.hand[0], self.name))
            self.hand.remove(self.hand[0])
            self.converttostr(self.hand, currenttrick)

        else:
            nottrump = [i for i,[num,suit] in enumerate(self.hand) if suit != self.deck.trumpname and num != self.deck.facecards['A']]
            idx = random.choice(nottrump)
            currenttrick.append((self.hand[idx], self.name))
            self.hand.remove(self.hand[idx])          
            self.converttostr(self.hand, currenttrick)  

    def dealerevaluate(self, turncard):
        self.hand.append(turncard)
        self.converttonum(hand = self.hand)
        #find the left
        leftcolor = 'black' if turncard[1] in self.deck.colors['black'] else 'red'
        leftsuit = self.deck.colors[leftcolor][1] if turncard[1] == self.deck.colors[leftcolor][0] else self.deck.colors[leftcolor][0]

        #filter cards out of hand
        potentials = [[num,suit] for [num,suit] in self.hand if suit != turncard[1]]
        potentialsAces = [[num,suit] for [num,suit] in potentials if [num,suit] != [self.deck.facecards['J'], leftsuit]]
       
        lowcard = 42
        #if the only "non trump" is the left, drop lowest trump, or just only trump in hand
        if not potentialsAces:
            for [num,suit] in self.hand:
                if num != self.deck.facecards['J']:
                    if num < lowcard:
                        lowcard = num
            card =  [lowcard, turncard[1]]

        #there are non-trump to discard
        else:
            #organize list
            x = [[[num,suit] for [num,suit] in potentialsAces if i == suit] for i in ("SPADES", "CLUBS", "DIAMONDS", "HEARTS")]

            #find one-card suits that arent aces
            lowcards = [[j for j in i if len(i)==1 and i[0][0] != self.deck.facecards['A']]for i in x]
            
            #if you have droppable one-card suits
            if any(lowcards):
                lowcard = 42
                for i in lowcards:
                    for j in i:
                        if j[0] < lowcard:
                            card = j
            
            else:
                lowcard = 42
                found = False
                for i in x:
                    #if the one-card suit is an ace, continue
                    if len(i) == 1 and i[0][0] == self.deck.facecards['A']:
                        continue
                    for j in i:
                        #find low cards that arent aces
                        if j[0] != self.deck.facecards['A']:
                            #found will stay false if all potentials with len 1 are aces
                            found = True
                            if j[0] < lowcard:
                                lowcard = j[0]
                
                #if all one card suits are aces, drop random offsuit ace
                if not found:
                    x = [i for i in x if i]
                    card = random.choice(x)[0]
                #drop lowest possible card
                else:
                    z = [[num,suit] for [num,suit] in potentialsAces if num == lowcard]
                    if len(z) > 1:
                        card = random.choice(z)
                    else:
                        card = z[0]
        discard = card
        self.hand.remove(card)
        self.converttostr(hand = self.hand, card = card)
        self.evaluatePrecall()
        if card != turncard:
            self.hand.remove(turncard)
            self.hand.append(card)
        return discard

    def discard(self, turncard, trump, colors):
        
        self.converttonum(hand = self.hand)
        
        for [num,suit] in self.hand:
            if suit == self.deck.trumpname and num != self.deck.trumpdict[self.deck.left]:            
                self.numcards[trump] = self.numcards[trump] - 1
            if num == self.deck.trumpdict[self.deck.left]:
                color = 'black' if trump in colors['black'] else 'red'
                idx = 1 if trump == colors[color][0] else 0
                leftsuit = colors[color][idx]
                self.numcards[leftsuit] = self.numcards[leftsuit] - 1
            if num == self.deck.facecards['A']:
                self.numcards[suit] = self.numcards[suit] - 1

        #filter out trump cards and aces
        potentials = [[num, suit] for [num,suit] in self.hand if suit != self.deck.trumpname and num != self.deck.facecards['A']]

        if potentials:
            #find the suit or suits with smallest amount
            listvalues = list(self.numcards.values())
            listvalues_nonzero = [i for i in listvalues if i]
            minsuitvalue = min(listvalues_nonzero)
            x = [[[num,suit] for [num,suit] in potentials if suit == key] for key in self.numcards if self.numcards[key] == minsuitvalue]

            #find the smallest card in the suits, ideally getting rid of a suit entirely
            
            lowcard = 42 #make sure this number is higher than any possible card value, random high number
            for i in x:
                for [num,suit] in i:
                    if num < lowcard:
                        lowcard = num
                        lowsuit = suit

            card = [lowcard, lowsuit]
            return card

        #if you have ALL TRUMP
        elif not potentials:
            aces = [[num,suit] for [num,suit] in self.hand if num == self.deck.facecards['A']]
            if aces:
                card = random.choice(aces)
                return card
            nums = [num for [num,suit] in self.hand if num != self.deck.facecards['A']]
            minnums = min(nums)
            card = [[num,suit] for [num,suit] in self.hand if num == minnums]
            card = card[0]
            return card

    def converttonum(self, hand = None, currenttrick = None):
        if currenttrick:
            for h,([i,j],k) in enumerate(currenttrick):
                if j == self.deck.trumpname:
                    if i in self.deck.trumpdict:
                        currenttrick[h][0][0] = self.deck.trumpdict[i]
                    elif i < 15:
                        currenttrick[h][0][0] = currenttrick[h][0][0] + 6

                elif i in self.deck.facecards:
                    currenttrick[h][0][0] = self.deck.facecards[i]       
    
        if hand:
            for h,([i,j]) in enumerate(self.hand):
                if j == self.deck.trumpname:
                    if i in self.deck.trumpdict: #face trump cards
                        self.hand[h][0] = self.deck.trumpdict[i]
                    
                    elif i < 15: #non face trump cards
                        self.hand[h][0] = self.hand[h][0] + 6

                elif i in self.deck.facecards: #regular face cards
                    self.hand[h][0] = self.deck.facecards[i]
        return currenttrick

    def converttostr(self, hand = None, currenttrick = None, card = None):
        if hand:
            for idx,[cardname, suit] in enumerate(hand):
                if cardname > 22:
                    for key in self.deck.trumpdict:
                        if cardname == self.deck.trumpdict[key]:
                            self.hand[idx][0] = key

                elif cardname >14:
                    self.hand[idx][0] = cardname - 6

                elif cardname > 10:
                    for key in self.deck.facecards:
                        if cardname == self.deck.facecards[key]:
                            self.hand[idx][0] = key
        if currenttrick:
            for h,([i,j],k) in enumerate(currenttrick):
                    if i > 22:
                        for key in self.deck.trumpdict:
                            if i == self.deck.trumpdict[key]:
                                currenttrick[h][0][0] = key

                    elif i > 14:
                        currenttrick[h][0][0] = currenttrick[h][0][0] - 6

                    elif i >10:
                        for key in self.deck.facecards:
                                if i == self.deck.facecards[key]:
                                    currenttrick[h][0][0] = key 
        if card:
            if card[0] > 22:
                for key in self.deck.trumpdict:
                    if card[0] == self.deck.trumpdict[key]:
                        card[0] = key

            elif card[0] > 14:
                card[0] = card[0] - 6

            elif card[0] > 10:
                for key in self.deck.facecards:
                    if card[0] == self.deck.facecards[key]:
                        card[0] = key  
        return currenttrick    
                    
if __name__ == '__main__':
    x = Computer('Keith')
    x.name
    x.hand
    x.deal()
    x.hand
    x.evaluatePrecall()
    x.evaluated
from deck import Deck
from player import Player, Computer
import random, time

class GameEuchre:
    def __init__(self, play):
        
        self.deck = Deck()
        
        if play:
            self.player1 = Computer('Brad')
            self.player2 = Computer('Jeff (teammate)')
            self.player3 = Computer('Dave')
            self.player4 = Player('You')
        else:
            self.player1 = Computer('COMPUTER1')
            self.player2 = Computer('COMPUTER2')
            self.player3 = Computer('COMPUTER3')
            self.player4 = Computer('COMPUTER4')
        if play:
            self.tricksdict = {'Brad': 0, 'Jeff (teammate)': 0, 'Dave' :0, 'You' : 0}
            self.went_alone = {'Brad': 0, 'Jeff (teammate)': 0, 'Dave' :0, 'You' : 0}
        else:
            self.tricksdict = dict(COMPUTER1 = 0, COMPUTER2 = 0, COMPUTER3 = 0, COMPUTER4 = 0)
            self.went_alone = dict(COMPUTER1 = 0, COMPUTER2 = 0, COMPUTER3 = 0, COMPUTER4 = 0)
        self.gotsetdict = dict(EVEN = 0, ODD = 0)
        self.totalpointsdict = dict(EVEN = 0, ODD = 0)
        self.team1 = [self.player1, self.player3]
        self.team1score = [0, 0]
        self.team2 = [self.player2, self.player4]
        self.team2score = [0, 0]
        self.table = [self.player1, self.player2, self.player3, self.player4]
        self.called = None
        self.currenttrick = []
        self.winner = None
        self.showstart = True
        self.go_alone = False
        self.go_aloneval = 19.99
        self.player1.Teammate = self.player3
        self.player2.Teammate = self.player4
        self.player3.Teammate = self.player1
        self.player4.Teammate = self.player2
        self.observe = False
        self.checkplayers()

    def checkplayers(self):
        for player in self.table:
            if player.__class__ == Player:
                self.observe = True

    def playGame(self, total = 5, totalgames = 1):
        #this code is PER GAME!!!!!!!!!!!!!!!!!!!-------------------------------
        if self.showstart == True and self.observe:
            self.startscreen()
        self.gamecounter = 0
        while self.gamecounter < totalgames:
            win = "EVEN" if self.team2score[1] > self.team1score[1] else "ODD"
            self.totalpointsdict[win] += 1
            self.team1score = [0, 0]
            self.team2score = [0, 0]            
            while self.team1score[1] < total and self.team2score[1] < total:           
                self.playHand()
            self.gamecounter+=1

            self.showstart = False
            if self.observe:
                self.winscreen()
            else:
                self.simulationdata()
        self.simulationdata()
        input('press enter to exit...')

    def playHand(self):            
            #this code is PER HAND!!!!!!!!!!!!!!!!!!!-------------------------------
            self.dealer = self.table[3]
            tableStart = self.table  #remember the original order to use for dealer change                      
            self.deck.resetdeck()                      
            self.deal()
            self.called = None
            
            #have all cpus evaluate hand first
            for player in self.table:  
                if player.__class__ == Computer:
                    if player == self.dealer:
                        dealerdiscard = player.dealerevaluate(self.turncard)
                    else:    
                        player.evaluatePrecall()   #cards are strs 
            
            #go around for the first opportunity to call the turncard

            for player in self.table:
                team = self.team1 if player in self.team1 else self.team2 
                teammate = team[1] if player == team[0] else team[0] 
                #---------------------------------------------------------------- 
                if self.observe:
                    self.preCallStats(player)    
                ans = player.firstcall(self.turncard, self.dealer, teammate, self.observe)
                if ans == 'yes':
                    self.called = player
                    if player.__class__ == Player:
                        self.preCallStats(player)
                        res = input("\n\nDo you want to go alone? Press 'y' for yes, press enter for no. ")
                        if res.lower() in ['y','yes']:
                            self.go_alone = True
                    else:
                        for [suit, score] in player.evaluated:
                            if suit == self.turncard[1] and score > self.go_aloneval:
                                self.go_alone = True
                                self.went_alone[player.name]+=1

                    self.deck.istrump(self.turncard[1])                
                    break

            #after trump has been called in the first go around--------
            if self.called:  
                if self.dealer.__class__ == Computer:
                    discard = dealerdiscard
                    self.pickitup(self.dealer, discard)
                else:
                    self.pickitup(self.dealer)
            
            #if the turn card is flipped over, pick from remaining suits------
            else:
                if self.dealer.__class__ == Computer:
                    self.dealer.evaluatePrecall()
                self.callTrump()
            
            #just code to organize cards in hand------
            for player in self.table:
                self.sorthand(player) 
            
            #start the hand------
            self.playTricks()

            #reset the table to change dealer and first to play-------
            self.table = tableStart[1:] + tableStart[:1] #shift the players to reflect chging of dealer

    def evaluatetrick(self):        
        self.converttonum(currenttrick = self.currenttrick)

        #set the high card and trick winner to the first to play
        highcard = self.currenttrick[0][0][0]
        self.winner = self.currenttrick[0][1]
            
        for ([i,j],k) in self.currenttrick[1:]:
            if i > highcard and j == self.suitled or i > highcard and i > 14:
                self.winner = k
                highcard = i

        for player in self.table:
            if player.name == self.winner:
                x = self.table.index(player)
                self.table = self.table[x:] + self.table[:x]
        
        return self.currenttrick   
        
    def checkwin(self, winner):    
        for player in self.team1:
            if winner in player.name:
                self.team1score[0] += 1
                if not self.observe:
                    self.tricksdict[winner] += 1
        for player in self.team2:
            if winner in player.name:
                self.team2score[0] += 1
                if not self.observe:
                    self.tricksdict[winner] += 1

        #check to see if either team got set----------------
        if self.team1score[0] == 3 and self.called in self.team2:
            if self.observe:
                print("SET!!!!!")
            self.team1score[1] += 2
            if not play:
                self.gotsetdict['EVEN'] += 1
            self.anothertrick = False
            self.team1score[0] = 0
            self.team2score[0] = 0
            self.resetplayers()
            return self.anothertrick

        elif self.team2score[0] == 3 and self.called in self.team1:
            if self.observe:
                print("SET!!!!!")
            self.team2score[1] += 2
            if not play:
                self.gotsetdict['ODD'] += 1
            self.anothertrick = False
            self.team1score[0] = 0
            self.team2score[0] = 0
            self.resetplayers()
            return self.anothertrick

        #check the trick counts after five tricks---------
        if self.team1score[0] + self.team2score[0] == 5:
            #team 1 took three tricks
            if self.team1score[0] > self.team2score[0]:
                self.team1score[1]+=1
            
            #team 2 took three tricks
            else:
                self.team2score[1]+=1


            #if either team took all 5 tricks
            if self.team1score[0] == 5:
                if self.called in self.team1 and self.go_alone == True:
                    self.team1score[1]+=3
                else:
                    self.team1score[1]+=1
            elif self.team2score[0] == 5:
                if self.called in self.team2 and self.go_alone == True:
                    self.team2score[1]+=3
                else:
                    self.team2score[1]+=1
            
            self.anothertrick= False
            self.go_alone = False
            self.team1score[0] = 0
            self.team2score[0] = 0
            self.resetplayers()
            return self.anothertrick
                
    def deal(self):
        count = 0
        for i in range(20):
            self.deck.shuffle() #chgd and not checked---- changed so it would shuffle 20 times instead of once
        for i in range(5):
            for player in self.table:
                player.hand.append(self.deck.fulldeck[count])
                count+=1
        self.farmers = self.deck.fulldeck[-4:]
        self.turncard = self.farmers[0]

    def pickitup(self, player, discardarg = None):
        if discardarg:
            if discardarg[1] == self.deck.trump:
                discardarg[1] = self.deck.trumpname
        if player.__class__ == Player:    
            print(F"\nThe dealer ({self.dealer.name}) will now pick up the turn card.")
            self.preCallStats(self.dealer)
            discard = input("\nWhich card would you like to discard? Pick a number 1-5 going top to bottom: ")       
            while discard not in ['1','2','3','4','5']:
                print("\nIndexError: Please select a number between 1 and 5.\n\n")
                self.preCallStats(self.dealer)
                discard = input("\nWhich card would you like to discard? Pick a number 1-5 going top to bottom: ")
            self.dealer.hand.pop(int(discard)-1)
            self.dealer.hand.append(self.turncard)
        else:
            if discardarg != self.turncard:
                self.dealer.hand.remove(discardarg)
                self.dealer.hand.append(self.turncard)

    def callTrump(self):
        suits = ['SPADES', 'CLUBS', 'HEARTS', 'DIAMONDS']
        suits.remove(self.turncard[1])
        
        for player in self.table[:-1]:
            if player.__class__ == Player:
                print(F"\n\n\nYour hand: \n") 
                # self.sorthand(player)       
                for i, [num,suit] in enumerate(player.hand):
                    print(F"\t\t\t   {num:>8} {suit:<8} \t\t({i+1})")
                answer = input(f"Pick any suit except {self.turncard[1]}, or pass:")
                while answer.upper() not in suits and answer.lower() != 'pass':
                    print("\n\nSorry, try again...\n\n")
                    for i, [num,suit] in enumerate(player.hand):
                        print(F"\t\t\t   {num:>8} {suit:<8} \t\t({i+1})")
                    answer = input(f"Pick any suit except {self.turncard[1]}, or pass:")
                if answer.lower() == 'pass':
                    continue
                elif answer.upper() in suits:
                    self.deck.istrump(answer.upper())
                    self.called = player
                    self.correctDealerHand()
                    self.currenttrick = []
                    self.stats(player)
                    res = input("Do you want to go alone? ")
                    if res.lower() in ['y','yes']:
                        self.go_alone = True
                    return

            else: #computer calls if the score of an available suit is over a certain number
                for [bestsuit, score] in player.evaluated:
                    if bestsuit in suits and score > 13.6:
                        self.deck.istrump(bestsuit) #this is where trump is called...........
                        self.called = player
                        self.correctDealerHand()
                        if score > self.go_aloneval: #experimental number for computer to go alone-----------------------------------
                            self.go_alone = True
                            self.went_alone[player.name]+=1
                            break
                        return
                if self.observe:
                    print(F"\n\n{player.name} has decided to pass")
        self.screwthedealer(suits)

    def correctDealerHand(self):
        for i,[num,suit] in enumerate(self.dealer.hand):
            if suit == self.deck.trump:
                self.dealer.hand[i][1] == self.deck.trumpname

    def screwthedealer(self, suits):
        if self.dealer.__class__ == Player:
            print(F"\n\n\nYour hand: \n") 
            # self.sorthand(player)       
            for i, [num,suit] in enumerate(self.dealer.hand):
                print(F"\t\t\t   {num:>8} {suit:<8} \t\t({i+1})")
            answer = input(f"\nYou've been screwed, you must pick any suit except {self.turncard[1]}:")
            while answer.upper() not in suits:
                print("\n\nSorry, try again...you've been screwed.\n\n")
                for i, [num,suit] in enumerate(self.dealer.hand):
                    print(F"\t\t\t   {num:>8} {suit:<8} \t\t({i+1})")
                answer = input(f"\nPick any suit except {self.turncard[1]}, or pass:")
            
            self.deck.istrump(answer.upper())
            self.called = self.dealer
            self.correctDealerHand()
            self.stats(self.dealer)
            res = input("Do you want to go alone? ")
            if res.lower() in ['y','yes']:
                self.go_alone = True
            return

        for [bestsuit, score] in self.dealer.evaluated:
            if bestsuit in suits:
                self.deck.istrump(bestsuit) #this is where trump is called...........
                self.called = self.dealer
                if score > self.go_aloneval:
                    self.go_alone = True
                    self.went_alone[self.dealer.name]+=1

                return

    def playTricks(self):
        self.suitled = None
        self.anothertrick = True
        for player in self.table:
            if player.__class__ == Computer:
                player.evaluatePostcall()
        
        #this code is PER TRICK!!!!!!!!!!!!!!!!!!!-------
        while self.anothertrick:
            #First player leads-------
            self.currenttrick = []
            self.suitled = None
            if self.table[0].Teammate == self.called and self.go_alone == True:
                leader = self.table[1]
                idx = 2
            else:
                leader = self.table[0]
                idx = 1
            if self.observe:
                self.stats(leader)
            if leader.__class__ == Player:
                leader.makemove(self.currenttrick)
            else:
                leader.myteam = self.team1 if leader in self.team1 else self.team2
                leader.makemoveCPU(self.currenttrick, leader.myteam, self.called)
            
            self.suitled = self.currenttrick[0][0][1]

            #The next three players play---------
            for player in self.table[idx:]:
                if player.Teammate == self.called and self.go_alone == True:
                    continue
                if player.__class__ == Player:
                    self.stats(player)
                    haveSuitled = False
                    for [card,suit] in player.hand:
                        if suit == self.suitled:
                            haveSuitled = True
                    if haveSuitled:   
                        while haveSuitled:
                                                      
                            player.makemove(self.currenttrick, self.suitled)
                            if self.currenttrick[-1][0][1] != self.suitled:
                                for i in range(15):
                                    print('-'*20)
                                print("\t\t\t\tYou must follow suit if you have it....")
                                for i in range(15):
                                    print('-'*20)
                                input("Press enter to continue...")
                                mycard = self.currenttrick.pop()[0]
                                player.hand.append(mycard)
                                self.sorthand(player)
                                self.stats(player)
                            else:
                                haveSuitled = False
                    else:
                        player.makemove(self.currenttrick, self.suitled)

                else:
                    if self.observe:
                        self.stats(player)
                    player.myteam = self.team1 if player in self.team1 else self.team2
                    player.makemoveCPU(self.currenttrick, player.myteam, self.called, self.suitled)

            for player in self.table:
                if player.__class__ == Computer:
                    player.checkbauers(self.currenttrick)
            if self.observe:   
                print('\n'*20)
                print("The total trick was: \n\n")
                for [i,j],k in self.currenttrick:
                    print(F"\t\t\t  {i:>8} {j:<8} ----> {k}")

            self.evaluatetrick()
            self.checkwin(self.winner)

            if self.observe:    
                print(F"\n{self.winner} won this Trick!!!!")
                self.score()
                input('\n\n\nPress enter to continue...')

    def stats(self, player):
        print('\n\n     ' + '-'*75)
        print('     ' + '-'*75)
        print('\n\t\t\t\t    ', player.name + '\n')
        print('     ' + '-'*75)
        print('     ' + '-'*75)
        self.score()
        print(F"\nThe Dealer: {self.dealer.name}")
        print(F"Called by: {self.called.name}{'(alone)' if self.go_alone else ''}")
        print(F'\nTrump: {self.deck.trump}')
        print(F"Suit Led: {self.suitled}")
        print(F"\nThe current trick: \n")
        for ([num,suit], playerdisplay) in self.currenttrick:
            print(F"\t\t   {num:>8} {suit:<8} ----> {playerdisplay}")
        print(F"\n\n\nYour hand: \n")     
        for i, [num,suit] in enumerate(player.hand):
            print(F"\t\t    {num:>8} {suit:<8} \t\t({i+1})")

    def preCallStats(self, player):
        print('\n\n     ' + '-'*75)
        print('     ' + '-'*75)
        print('\n\t\t\t\t    ', player.name + '\n')
        print('     ' + '-'*75)
        print('     ' + '-'*75)
        self.score()
        print(F"\nThe Dealer: {self.dealer.name}")
        print(F'\nTrump: {self.deck.trump if self.called else None}')
        print("Called by: ", self.called.name if self.called else None)
        print(F"\n\n\t\t\t    The turncard: {self.turncard[0]} {self.turncard[1]}")
        print(F"\n\n\nYour hand: \n")      
        for i, [num,suit] in enumerate(player.hand):
            print(F"\t\t    {num:>8} {suit:<8} \t\t({i+1})")
        return self.deck
            
    def score(self):
        print(F"\n\t\t\t    Number of Tricks Taken:")
        print('\t\t\t   '+'-'*25)
        if play:
            print(F"\t\t\tVillians: {self.team1score[0]} ------- Heroes: {self.team2score[0]}")
        else:
            print(F"\t\t\tTeam Odd: {self.team1score[0]} ------- Team Even: {self.team2score[0]}")

        print(F"\n\t\t\t          Total Score:")
        print('\t\t\t   '+'-'*25)
        if play:
            print(F"\t\t\tVillians: {self.team1score[1]} ------- Heroes: {self.team2score[1]}")
        else:
            print(F"\t\t\tTeam Odd: {self.team1score[1]} ------- Team Even: {self.team2score[1]}")


    def converttonum(self, player = None, hand = None, currenttrick = None):
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
            for h,([i,j]) in enumerate(player.hand):
                if j == self.deck.trumpname:
                    if i in self.deck.trumpdict: #face trump cards
                        player.hand[h][0] = self.deck.trumpdict[i]
                    
                    elif i < 15 : #non face trump cards
                        player.hand[h][0] = player.hand[h][0] + 6

                elif i in self.deck.facecards: #regular face cards
                    player.hand[h][0] = self.deck.facecards[i]
        return currenttrick

    def converttostr(self, player = None, hand = None, currenttrick = None):
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
        return currenttrick      
        
    def sorthand(self, player):
        length = len(player.hand)
        for suit in self.deck.suits:
            for [num, card] in player.hand[:length]:
                if card == suit:
                    player.hand.append([num, card])
        player.hand = player.hand[-length:]

        self.converttonum(player = player, hand = player.hand)
        
        for suittest in self.deck.suits:
            nums = [num for [num, suit] in player.hand if suit == suittest]
            nums = list(sorted(nums))
            nums.reverse()
            for i in nums:
                player.hand.append([i, suittest])
        player.hand = player.hand[-length:]
        
        for idx,[cardname, suit] in enumerate(player.hand):
                if cardname > 22:
                    for key in self.deck.trumpdict:
                        if cardname == self.deck.trumpdict[key]:
                            player.hand[idx][0] = key
                elif cardname >14:
                    player.hand[idx][0] = cardname - 6
                elif cardname > 10:
                    for key in self.deck.facecards:
                        if cardname == self.deck.facecards[key]:
                            player.hand[idx][0] = key

    def resetplayers(self):
        for player in self.table:
            player.__init__(player.name)
        return self.table
    
    @staticmethod
    def startscreen():
            largeblock = 6
            spacer = '|||' + ' '*94 + '|||'
            phrases = ['This is a Euchre Game.', spacer, "Written by Kyle Sullivan",
                    spacer, '\u00A9 1984 \u00AE', spacer, 'I hope you are bringing your A-game to this program,',
                    'because these computer players WILL beat you.',
                    'Best of luck...']

            print('-'*100)
            print('-'*100)
            print('-'*100)
            for i in range(largeblock):
                print(spacer)

            for i in phrases:
                if len(i)%2 != 0:
                    i = i + ' '
                multiplier = int((94-len(i))/2)
                if i != spacer:
                    print('|||' + ' '*multiplier + i + ' '*multiplier + '|||')
                else:
                    print(spacer)
    
            for i in range(largeblock):
                print(spacer)
            print('-'*100)
            input("Press enter to play some Euchre...")

    def winscreen(self):
        if play:
            win = "Villians" if self.team1score > self.team2score else "Heroes"
        else:
            win = "Team Even" if self.team1score < self.team2score else "Team Odd"
        print("We have a winner!!!  " + win + '!!!!!!!!' )
        print(F"Team 1: {self.team1score} \nTeam2: {self.team2score}")
        winners_team = []
        winners = self.team1 if self.team1score > self.team2score else self.team2
        for winner in winners:
            winners_team.append(winner.name)

        largeblock = 2
        spacer = '|||' + ' '*94 + '|||'
        phrases = ['WE HAVE A WINNER!!!!!!', spacer, F"{win}", spacer, F"Team Odd Score: {self.team1score[1]} Team Even Score: {self.team2score[1]}",
                spacer, 'The winning players are:', spacer, F'{winners_team[0]} and {winners_team[1]}',
                spacer, 'I know you will go on to do great things...',
                'Winning this game is really just the beginning for you.',spacer,spacer,'I bet the funniest thing a person says when they are being secretly recorded,',
                'would be whatever comes right before "I\'m glad no one heard that."',
                spacer, spacer, 'Thanks for playing and I hope you enjoyed my game,', spacer, '-Kyle Sullivan']

        print('-'*100)
        print('-'*100)
        print('-'*100)
        for i in range(largeblock):
            print(spacer)

        for i in phrases:
            if len(i)%2 != 0:
                i = i + ' '
            multiplier = int((94-len(i))/2)
            if i != spacer:
                print('|||' + ' '*multiplier + i + ' '*multiplier + '|||')
            else:
                print(spacer)

        for i in range(largeblock):
            print(spacer)
        print('-'*100)
        self.team1score = [0, 0]
        self.team2score = [0, 0]
        self.called = None
        self.currenttrick = []
        playagain = input("Do you want to play again? -----> ")
        if playagain in ['y', 'Y', 'yes', 'Yes']:
            self.playGame()
        else:
            exit()

    def simulationdata(self):

        print('\nTRICKS: \n')
        for key in self.tricksdict:
            print(key, '===>', self.tricksdict[key])

        print('\nGot set: \n')
        for key in self.gotsetdict:
            print(key, '===>', self.gotsetdict[key])

        print('\nWent Alone: \n')
        for key in self.went_alone:
            print(key, '===>', self.went_alone[key])

        print('\nTotal Points: \n')
        for key in self.totalpointsdict:
            print(key, '===>', self.totalpointsdict[key])

        print(F"\n\t\t\t    Number of Tricks Taken:")
        print('\t\t\t   '+'-'*25)
        print(F"\t\t\tTeam Odd: {self.team1score[0]} ------- Team Even: {self.team2score[0]}")
        print(F"\n\t\t\t          Total Score:")
        print('\t\t\t   '+'-'*25)
        print(F"\t\t\tTeam Odd: {self.team1score[1]} ------- Team Even: {self.team2score[1]}")

        print(F"Game number: {self.gamecounter}")

if __name__ == '__main__':
    
    ans = input("\n\nPress 1 to run simulation, press any other key to play...")
    if ans == '1':
        ans = int(ans)
        play = False
        totalgames = input("\nHow many games would you like to simulate?  ")
    else:
        play = True

    x = GameEuchre(play)
    
    if play:
        x.playGame()
    else:
        x.playGame(totalgames = int(totalgames))

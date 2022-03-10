import random
import pyttsx3
import datetime

SYMBOLS = ['♠', '♢', '♡', '♣']
SUIT = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
RANK = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
RANK_VALUE = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13}
SUIT_SYMBOLS = {'Hearts': '♡', 'Clubs': '♣', 'Spades': '♠', 'Diamonds': '♢'}

def speak(audio) :
    engine.say(audio)
    engine.runAndWait()
	
class Card:
	""" Card Class - Models a single Playing Card """

	def __init__(self, rank, suit):
		
		self.rank = rank
		self.suit = suit
		self.isjoker = False

	def __str__(self):
		""" Helper for builtin __str__ function"""
		
		
		if self.isjoker:
			return (self.rank + SUIT_SYMBOLS[self.suit] + '-J')
		return (self.rank + SUIT_SYMBOLS[self.suit])

	def is_joker(self):
		"""Status check to see if this Card is a Joker"""
		
		
		return self.isjoker

class Deck:
	""" Deck Class - Models the card Deck """

	def __init__(self, packs):
		
		self.packs = packs
		self.cards = []
		self.joker = None

		# Create all cards in the Deck
		for i in range(packs):
			for s in SUIT:
				for r in RANK:
					self.cards.append(Card(r, s))

	def shuffle(self):
		
		random.shuffle(self.cards)

	def draw_card(self):
		""" Draw a card from the top of the Deck"""
		
		a = self.cards[0]
		self.cards.pop(0)
		return a

	def set_joker(self):
		""" Set the Joker Cards in the Deck
		A Card is selected at random from the deck as Joker.
		All cards with the same Rank as the Joker are also set to Jokers."""
		
		
		self.joker = random.choice(self.cards)

		# remove the Joker from Deck and display on Table for Players to see
		self.cards.remove(self.joker)

		for card in self.cards:
			if self.joker.rank == card.rank:
				card.isjoker = True

class Player:
	""" Player Class - Models Players Hand and play actions """

	def __init__(self, name, deck, game):
		
		self.stash = []	# Stash represents the hand of the Player.
		self.name = name
		self.deck = deck
		self.game = game

	def deal_card(self, card):
		""" Deal a Card to the Player"""
		
		try:
			self.stash.append(card)
			if len(self.stash) > 14:
				raise ValueError('ERROR: Player cannot have more than 14 cards during turn')
		except ValueError as err:
			print(err.args)

	def drop_card(self, card):
		""" Drop Card operation by the Player"""
		
		# Get the actual card object from string representation
		card = get_object(self.stash, card)

		# Cannot drop a card if it is already not in stash
		if card not in self.stash:
			return False

		self.stash.remove(card)

		# Player dropped card goes to Pile
		self.game.add_pile(card)

		return True


	def close_game(self):
		""" Close Game operation by the Player"""
		
		
		# Divide the stash into 4 sets, 3 sets of 3 cards and 1 set of 4 cards
		set_array = [self.stash[:3], self.stash[3:6], self.stash[6:9], self.stash[9:]]

		# Need to count the number of sets that are runs without a joker.
		# 	There must be at least one run with out a joker
		count = 0
		for s in set_array:
			if is_valid_run(s):
				count += 1
		if count == 0:
			return False

		# Check if each of the sets is either a run or a book
		for s in set_array:
			if is_valid_run(s) == False and is_valid_book(s) == False and is_valid_run_joker(s) == False:
				return False

		return True

	def play(self):
		""" Play a single turn by the Player"""
		
		# Stay in a loop until the Player drops a card or closes the game.
		while True:
            
			# clear screen to remove the output of previous Player action
			print(chr(27)+"[2J")
			print("***",self.name,"your cards are:")
            
			print(print_cards(self.stash))
			self.game.display_pile()

			# Get Player Action
			action = input("*** " + self.name + ", What would you like to do? ***, \n(M)ove Cards, (P)ick from pile, (T)ake from deck, (D)rop, (S)ort, (C)lose Game, (R)ules: ")

			# Move or Rearrange Cards in the stash
			if action == 'M' or action == 'm':
				# Get the Card that needs to moved.
				speak("Enter which card you want to move")
				move_what = input("Enter which card you want to move. \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
				move_what.strip()
				if get_object(self.stash, move_what.upper()) not in self.stash:
					input("ERROR: That card is not in your stash.  Enter to continue")
					continue

				# Get the Card where the move_what needs to moved.
				speak("Enter where you want move card to")
				move_where = input("Enter where you want move card to (which card the moving card will go before) Enter Space to move to end \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts):" )
				move_where.strip()
				if move_where != "" and get_object(self.stash, move_where.upper()) not in self.stash:
					input("ERROR: This is an invalid location.  Enter to continue")
					continue

				# Perform the Move Operation
				move_what = get_object(self.stash, move_what.upper())
				if move_where != "":
					move_where = get_object(self.stash, move_where.upper())
					location = self.stash.index(move_where)
					if location > self.stash.index(move_what):
						location = location - 1
					self.stash.remove(move_what)
					self.stash.insert(location, move_what)
				else:
					# If the move_where was not specified by the User then,
					#		the card to the end of the stash
					self.stash.remove(move_what)
					self.stash.append(move_what)

			# Pick card from Pile
			if action == 'P' or action == 'p':
				if len(self.stash) < 14:
					c = self.game.draw_pile()
					self.stash.append(c)
				else:
					input("ERROR: You have " + str(len(self.stash)) + " cards. Cannot pick anymore. Enter to continue")

			# Take Card from Deck
			if action == 'T' or action == 't':
				if len(self.stash) < 14:
					c = self.deck.draw_card()
					self.stash.append(c)
				else:
					input("ERROR: You have " + str(len(self.stash)) + " cards. Cannot take anymore. Enter to continue")

			# Drop card to Pile
			if action == 'D' or action == 'd':
				if len(self.stash) == 14:    					
					speak("Which card would you like to drop?")
					drop = input("Which card would you like to drop? \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
					drop = drop.strip()
					drop = drop.upper()
					if self.drop_card(drop):
						# return False because Drop Card does not end the game
						return False
					else:
    						
						input("ERROR: Not a valid card, Enter to continue")
				else:
					input("ERROR: Cannot drop a card. Player must have 13 cards total. Enter to continue")

			# Sort cards in the stash
			if action == 'S' or action == 's':
				sort_sequence(self.stash)

			# Close the Game
			if action == 'C' or action == 'c':

				if len(self.stash) == 14:
					drop = input("Which card would you like to drop? \nEnter Rank followed by first letter of Suit. i.e. 4H (4 of Hearts): ")
					drop = drop.strip()
					drop = drop.upper()
					if self.drop_card(drop):
						if self.close_game():
							print(print_cards(self.stash))
							# Return True because Close ends the Game.
							return True
						else:
							input("ERROR: The game is not over. Enter to Continue playing.")
							# if this Close was false alarm then discarded Card will
							#		have to be put back into the stash for the Player to continue.
							self.stash.append(self.game.draw_pile())
					else:
						input("ERROR: Not a valid card, Enter to continue")
				else:
					input("ERROR: You do not have enough cards to close the game. Enter to Continue playing.")

			# Show Rules of the game
			if action == 'R' or action == 'r':
				print("------------------ Rules --------------------",
					"\n- Rummy is a card game based on making sets.",
					"\n- From a HAND of 13 cards, 4 sets must be created (3 sets of 3, 1 set of 4).",
					"\n- The set of 4 must always be at the end"
					"\n- A valid set can either be a run or a book.",
					"\n- One set must be a run WITHOUT using a joker."
					"\n- A run is a sequence of numbers in a row, all with the same suit. ",
					"\n \tFor example: 4 of Hearts, 5 of Hearts, and 6 of Hearts",
					"\n- A book of cards must have the same rank but may have different suits.",
					"\n \tFor example: 3 of Diamonds, 3 of Spades, 3 of Clubs",
					"\n- Jokers are randomly picked from the deck at the start of the game.",
					"\n- Joker is denoted by '-J' and can be used to complete sets.",
					"\n- During each turn, the player may take a card from the pile or from the deck.",
					"Immediately after, the player must drop any one card into the pile so as not go over the 13 card limit.",
					"\n- When a player has created all the sets, select Close Game option and drop the excess card into the pile.",
					"\n- Card with Rank 10 is represented as Rank T"
					"\n--------------------------------------------" )
					
				input("Enter to continue ....")

class Game:
	""" Game Class - Models a single Game """ 

	def __init__(self, hands, deck):
		
		self.pile = []
		self.players = []

		for i in range(hands):
			name = input("Enter name of Player " + str(i) + ": ")
			self.players.append(Player(name, deck, self))

	def display_pile(self):
		""" Displays the top of the Pile."""
			
		if len(self.pile) == 0:
			print("Empty pile.")
		else:
			print("The card at the top of the pile is: ", self.pile[0])

	def add_pile(self, card):
		""" Adds card to the top of the Pile."""
			
		self.pile.insert(0, card)

	def draw_pile(self):
		""" Draw the top card from the Pile."""
			
		if len(self.pile) != 0:
			return self.pile.pop(0)
		else:
			return None

	def play(self):
		""" Play the close_game."""
			
		i = 0
		while self.players[i].play() == False:
            
			print(chr(27)+"[2J")
			i += 1
			if i == len(self.players):
				i = 0
			print("***", self.players[i].name, "to play now.")
			input(self.players[i].name + " hit enter to continue...")

		# Game Over
		speak(" GAME OVER !")
		print("*** GAME OVER ***")
		speak(f"CONGURATULATIONS {self.players[i].name} WON THE GAME")
		print("*** ", self.players[i].name, " Won the game ***")


#global nonclass functions
def is_valid_book(sequence):
	""" Check if the sequence is a valid book."""
		
	# Move all Jokers to the end of the sequence
	while(sequence[0].isjoker == True):
		sequence.append(sequence.pop(0))

	# Compare Cards in sequnce with 0th Card, except for Jokers.
	for card in sequence:
		if card.is_joker() == True:
			continue
		if card.rank != sequence[0].rank:
			return False

	return True

def is_valid_run(sequence):
	""" Check if the sequence is a valid run."""
		
	RANK_VALUE["A"] = 1 #resetting value of A (may have been set to 14 in previous run)

	# Order the Cards in the sequence
	sort_sequence(sequence)

	# Check to see if all Cards in the sequence have the same SUIT
	for card in sequence:
		if card.suit != sequence[0].suit:
			return False

	# this is to sort a sequence that has K, Q and A
	if sequence[0].rank == "A":
		if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
			RANK_VALUE[sequence[0].rank] = 14
			sort_sequence(sequence)

	# Rank Comparison
	for i in range(1,len(sequence)):
		if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+1:
			return False

	return True

def is_valid_run_joker(sequence):
	""" Check if the sequence with Jokers is a valid run."""
		

	RANK_VALUE["A"] = 1 #resetting value of A (may have been set to 14 in previous run)

	# Order the Cards in the sequence
	sort_sequence(sequence)

	# Push all Jokers to the end and count the number of Jokers
	push_joker_toend(sequence)
	joker_count = 0
	for card in sequence:
		if card.is_joker() == True:
			joker_count += 1

	# Make sure the Suit Match except for Jokers.
	for card in sequence:
		if card.is_joker() == True:
			continue
		if card.suit != sequence[0].suit:
			return False

	# This is to cover for K, Q and A run with Jokers
	if sequence[0].rank == "A":
		if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
			RANK_VALUE[sequence[0].rank] = 14
			sort_sequence(sequence)
			push_joker_toend(sequence)

	rank_inc = 1
	for i in range(1,len(sequence)):
		if sequence[i].is_joker() == True:
			continue
		# Compare RANK values with accomodating for Jokers.
		while (RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+rank_inc):
			# Use Joker Count for missing Cards in the run
			if joker_count > 0:
				rank_inc += 1
				joker_count -= 1
				continue
			else:
				# if No more Jokers left, then revert to regular comparison
				if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i-1].rank)]+1:
					return False
				else:
					break
	return True

def push_joker_toend(sequence):
	""" Push the Joker to the end of the sequence."""
		
	sort_sequence(sequence)
	joker_list = []
	for card in sequence:
		if card.is_joker()== True:
			sequence.remove(card)
			joker_list.append(card)
	sequence += joker_list
	return sequence

def get_object(arr, str_card):
	""" Get Card Object using its User Input string representation"""
	
	# Make sure the str_card has only a RANK letter and SUIT letter
	#		for example KH for King of Hearts.
	if len(str_card) != 2:
		return None

	for item in arr:
		if item.rank == str_card[0] and item.suit[0] == str_card[1]:
			return item

	return None

def print_cards(arr):
	""" Print Cards in a single line"""
		
	s = ""
	for card in arr:
		s = s + " " + str(card)
	return s

def sort_sequence(sequence):
	""" Sort the Cards in the sequence in the incresing order of RANK values"""
		
	is_sort_complete = False

	while is_sort_complete == False:
		is_sort_complete = True
		for i in range(0, len(sequence)-1):
			if RANK_VALUE[sequence[i].rank] > RANK_VALUE[sequence[i+1].rank]:
				a = sequence[i+1]
				sequence[i+1] = sequence[i]
				sequence[i] = a
				is_sort_complete = False
	return sequence
engine = pyttsx3.init('sapi5')
engine.setProperty('rate',178)
voices= engine.getProperty('voices') #getting details of current voice
engine.setProperty('voice', voices[0].id)

#f1=open("C:\\Users\\NAVODAYA VARMA\\Desktop\\FILES\\vsp\\CARDS\\presentation.txt",'r')
#content=f1.read()
#f1.close()
        
        



def wishme():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12 :
        speak("HELLO! GOOD MORNING!")
    elif hour>=12 and hour<18 :
        speak("HEY! GOOD AFTERNOON!")
    else :
        speak("HEY! GOOD EVENING!")
    
    #speak(content)

def main():
	""" Main Program """

	# Create Deck with 2 Packs
	deck = Deck(2)
	deck.shuffle()

	# Joker Logic is disabled currently.
	# deck.set_joker()

	# New game with 2 players
	g = Game(2, deck)

	# Deal Cards
	for i in range(13):
		for hand in g.players:
			card = deck.draw_card()
			hand.deal_card(card)

	# Create Pile
	first_card = deck.draw_card()
	g.add_pile(first_card)

	# Now let the Players begin
	g.play()

if __name__ == "__main__":
    wishme()
    main()
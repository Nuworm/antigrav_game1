# Game Architecture
This is a turn based game where the human player takes a turn moveing until it runs out of movement points. 
Then the AI takes a turn moving until it runs out of movement points. This cycle repeats until the human player wins or loses.

## Tile Rules
Green = 1 Movement Cost
Blue = Cannot Move Onto
Brown = 2 Movement Cost

## Movement Rules
Human controled player has 2 movement points per turn. If the Human controled player still has movement points left after 
moving to a tile, it can move again. If the Human controled player runs out of movement points, it is the AI's turn. 
The AI has 1 movement point per turn. If the AI still has movement points left after moving to a tile, it can move again. 
If the AI runs out of movement points, it is the Human controled player's turn.

## Victory Conditions

The Human controled player wins if it moves to 2 brown tiles. The AI wins if it moves to 2 brown tiles. 

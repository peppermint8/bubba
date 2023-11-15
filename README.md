# Bubba the Beholder
(A Xarnoz production)

 A "simple" top down shooter with RPG elements.  I was inspired by:
 * TRS-80 Color Computer: Temple of ROM (Rick Adams 1982), Dungeons of Daggorath
 * Doom
 * Dungeons & Dragons
 * Rogue
 * Diablo
 
Written in python, requires the pygame & pyyaml libraries.

Run the game with: `$ ./bubba.py`

Use W,A,S,D and the mouse to move around. "E" can open doors if you are facing them.  Yellow doors needs keys.  Clicking the mouse button fires your spells.  1,2,3 selects the different spells if you have those powers.  Firing spells costs mana.  No mana, no spells.  Mana regenerates over time.
 * some monsters are immune to certan attacks
 * some treasures give you special powers
 * orangish squares are lava - Bubba dislikes lava
 * blue-ish squares are water - Bubba hates water

"I" will turn you invisible if you have the invisibility ring.
Arrow keys can zoom around the map.  The "fog of war" hides areas until they are found or a spell is activated.



## To Do

 - [ ] Bubba increase level
 - [ ] Instructions on map making and customizing the monsters, treasures and traps. 
 - [ ] scale everything (beasts, player, treasure, traps) when the grid size changes (+/- keys).


## Developer Notes

The map, items and monsters are all customizable.  The first map is for testing and is very unbalanced.

I wanted to see what it took to create a game where the character and monsters were constrained by the boundaries of walls.  The monster intellegence is very basic.  I'd like to do something simple like this using a low-poly style graphics with better animation.

The code needs to be cleaned up and put into more files.

I am impressed with the speed it runs given how many things I do in the main loop.



## Credits

For the images I used: https://www.flaticon.com/
Thanks to the contributors:
Freepik, Iconikar, IconMarketPx, redempticon, Lovedat, Xinh, pongsakored

The beholder title comes from:
https://www.img2go.com/
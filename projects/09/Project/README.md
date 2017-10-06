# Nand 2 Tetris - Project 9

Hi! Thanks for reviewing my work.

## Program

This program draws a row based automata to the screen. Each square in the grid has a value of 0 or 1, and the values in each row are calculated in a progressive manner.

The automata is 'seeded' with the first row, which contains a single '1' value. The rest of the grid is calculated row-by-row according to a simple set of rules. The cool thing about this animation is how a complex shape arises from such simple rules.

See the following blog post for more details on the theory behind this animation:
    http://blog.stephenwolfram.com/2017/06/oh-my-gosh-its-covered-in-rule-30s/

## How To

To run this program
    * load the /build directory into the VM emulator
    * set 'Animate' to 'No animation'
    * set execution speed to 'Fast'
    * run the program - you should see a crazy pyramid printed to the screen

## Project Structure

* `source/` contains all of my Jack files
* `build/` contains all of the compiled VM bytecode 


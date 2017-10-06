// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Start event loop by clearing the screen
@CLEAR_SCREEN
0;JMP

// Listen to key press
(EVENT_LOOP)
    @KBD
    D=M

    // If a key is pressed then darken screen
    @DARKEN_SCREEN
    D;JGT

    // Else, if the screen is dark, clear it
    @screen_is_dark
    D=M
    @CLEAR_SCREEN
    D;JGT

    // Else repeat event loop
    @EVENT_LOOP
    0;JMP

// Set the whole screen to 1s
(DARKEN_SCREEN)
    // mark screen as 'dark'
    @screen_is_dark
    M=1

    // set color to all black for each 16px row
    @color
    M=-1

    // Write color to the screen
    @WRITE_SCREEN
    0;JMP


// Set the whole screen to 0s
(CLEAR_SCREEN)
    // mark screen as 'cleared'
    @screen_is_dark
    M=0

    // set color to all white for each 16px row
    @color
    M=0

    // Write color to the screen
    @WRITE_SCREEN
    0;JMP

(WRITE_SCREEN)
    // Reset screen index to the end of the screen
    @8191  // 8192 screen registers + off by one error
    D=A
    @SCREEN
    D=D+A
    @screen_idx
    M=D

    // Kick of write loop
    @WRITE_SCREEN_LOOP
    0;JMP


// Write contents of @color to the entire screen
(WRITE_SCREEN_LOOP)
    // Read color value into D
    @color
    D=M

    // Read current screen index
    @screen_idx
    A=M

    // Write color into location stored in screen_idx
    M=D

    // Decrement screen index
    @screen_idx
    M=M-1
    D=M

    // Loop if screen index is not 0
    @WRITE_SCREEN_LOOP
    D;JGT

    // Back to event loop
    @EVENT_LOOP
    0;JMP
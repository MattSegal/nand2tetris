// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_0
D;JEQ
@0
D=A
@FALSE_0
0;JMP
(TRUE_0)
@1
D=-A
(FALSE_0)
@SP
A=M-1
M=D

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_1
D;JEQ
@0
D=A
@FALSE_1
0;JMP
(TRUE_1)
@1
D=-A
(FALSE_1)
@SP
A=M-1
M=D

// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1

// eq
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_2
D;JEQ
@0
D=A
@FALSE_2
0;JMP
(TRUE_2)
@1
D=-A
(FALSE_2)
@SP
A=M-1
M=D

// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_3
D;JLT
@0
D=A
@FALSE_3
0;JMP
(TRUE_3)
@1
D=-A
(FALSE_3)
@SP
A=M-1
M=D

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_4
D;JLT
@0
D=A
@FALSE_4
0;JMP
(TRUE_4)
@1
D=-A
(FALSE_4)
@SP
A=M-1
M=D

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1

// lt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_5
D;JLT
@0
D=A
@FALSE_5
0;JMP
(TRUE_5)
@1
D=-A
(FALSE_5)
@SP
A=M-1
M=D

// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_6
D;JGT
@0
D=A
@FALSE_6
0;JMP
(TRUE_6)
@1
D=-A
(FALSE_6)
@SP
A=M-1
M=D

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_7
D;JGT
@0
D=A
@FALSE_7
0;JMP
(TRUE_7)
@1
D=-A
(FALSE_7)
@SP
A=M-1
M=D

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1

// gt
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
D=M-D
@TRUE_8
D;JGT
@0
D=A
@FALSE_8
0;JMP
(TRUE_8)
@1
D=-A
(FALSE_8)
@SP
A=M-1
M=D

// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1

// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1

// add
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
M=D+M

// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1

// sub
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
M=M-D

// neg
@SP
A=M-1
M=-M

// and
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
M=M&D

// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1

// or
@SP
M=M-1
D=M
@R13
M=D-1
A=D
D=M
@R13
A=M
M=M|D

// not
@SP
A=M-1
M=!M

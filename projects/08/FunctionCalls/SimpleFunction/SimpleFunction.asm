// function SimpleFunction.test 2
(SimpleFunction.test)
@0
D=A
@SP
A=M
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
M=D
@SP
M=M+1

// push local 0
@0
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// push local 1
@1
D=A
@LCL
A=D+M
D=M
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

// not
@SP
A=M-1
M=!M

// push argument 0
@0
D=A
@ARG
A=D+M
D=M
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

// push argument 1
@1
D=A
@ARG
A=D+M
D=M
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

// return
@LCL
D=M
@FRAME
M=D
@FRAME
D=M
@5
D=D-A
A=D
D=M
@RET
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
D=A
@SP
M=D+1
@FRAME
D=M
@1
D=D-A
A=D
D=M
@THAT
M=D
@FRAME
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
@FRAME
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
@FRAME
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
@RET
A=M
0;JMP

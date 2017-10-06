$programs = @(
    "ProgramFlow/BasicLoop",
    "ProgramFlow/FibonacciSeries",
    "FunctionCalls/SimpleFunction",
    "FunctionCalls/StaticsTest",
    "FunctionCalls/FibonacciElement",
    "FunctionCalls/NestedCall"
)
foreach ($program in $programs)
{
    Write-Host "`nCalling $program"
    py VMTranslator.py "../$($program)"
}



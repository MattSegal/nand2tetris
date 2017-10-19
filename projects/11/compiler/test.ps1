
$DIRS = @(
    '../Average',
    '../ComplexArrays',
    '../ConvertToBin',
    '../Pong',
    '../Seven',
    '../Square'
)

ForEach ($dir in $DIRS)
{
    Write-Host "Running compiler on $dir"
    py JackCompiler.py $dir
}

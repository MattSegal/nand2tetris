$SUBMISSION_DIR = 'project11'
$SUBMISSION_ITEMS = @(
    './compiler/constants.py',
    './compiler/jack_parser.py',
    './compiler/lang.txt',
    './compiler/JackCompiler.py',
    './compiler/tokenizer.py',
    './compiler/code_generator.py'
)

New-Item -Type Directory $SUBMISSION_DIR -Force

ForEach ($item in $SUBMISSION_ITEMS)
{
    Copy-Item $item $SUBMISSION_DIR
}

Compress-Archive "${SUBMISSION_DIR}/*" "${SUBMISSION_DIR}.zip" -Force
Remove-Item $SUBMISSION_DIR -Recurse
$SUBMISSION_DIR = 'project10'
$SUBMISSION_ITEMS = @(
    './analyzer/constants.py',
    './analyzer/jack_parser.py',
    './analyzer/lang.txt',
    './analyzer/JackAnalyzer.py',
    './analyzer/tokenizer.py'
)

New-Item -Type Directory $SUBMISSION_DIR -Force

ForEach ($item in $SUBMISSION_ITEMS)
{
    Copy-Item $item $SUBMISSION_DIR
}

Compress-Archive "${SUBMISSION_DIR}/*" "${SUBMISSION_DIR}.zip" -Force
Remove-Item $SUBMISSION_DIR -Recurse
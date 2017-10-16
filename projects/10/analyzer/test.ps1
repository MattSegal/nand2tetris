param ([String]$targetDir)

Write-Host "Running analyser on $targetDir"
py JackAnalyzer.py $targetDir

$testFiles = Get-ChildItem $targetDir | 
    Where {$_.name.EndsWith('.xml')} |
    Where {-Not ($_.name.EndsWith('T.xml'))} |
    Where {-Not ($_.name.EndsWith('matt.xml'))}

ForEach ($testFile in $testFiles)
{
    Write-Host "Comparing $testFile"
    $testedFile = $testFile.name.Replace('.xml', '.matt.xml')
    Compare-Object (Get-Content (Join-Path $targetDir $testFile)) (Get-Content (Join-Path $targetDir $testedFile))
}

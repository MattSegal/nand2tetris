param([String]$name)

function Compile() {
    param([String]$file)
    $output = $file.replace('.jack','.vm')
    $dest = $file.replace('.jack', 'Test')
    rm (Join-Path $dest *.vm)
    ../../tools/JackCompiler.bat $dest
    ../../tools/JackCompiler.bat $file 
    mv $output $dest
}

if ($name -eq 'all') {
    $jacks = Get-ChildItem . | Where {$_ -like "*.jack"} 
    foreach ($jack in $jacks) {
        Compile $jack
    }
} else {
    Compile $name  
}

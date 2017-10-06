
if (!(Test-Path project08)) {
    mkdir project08
}

if (Test-Path project08.zip) {
    rm project08.zip
}
cp lang.txt project08/lang.txt
cp VMTranslator.py project08/VMTranslator.py

 Compress-Archive .\project08\* project08.zip
set scripts=%cd%

@REM Generate Czech MO file
cd %scripts%\..\source\locales\cs\LC_MESSAGES
python %scripts%\msgfmt.py -o base.mo base

@REM Generate English MO file
cd %scripts%\..\source\locales\en\LC_MESSAGES
python %scripts%\msgfmt.py -o base.mo base

@REM Generate Slovak MO file
cd %scripts%\..\source\locales\sk\LC_MESSAGES
python %scripts%\msgfmt.py -o base.mo base

title MO language files generation completed
pause
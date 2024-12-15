set scripts=%cd%

@REM Generate Czech MO file
cd %scripts%\..\source\locale\cs\LC_MESSAGES
python %scripts%\msgfmt.py -o nvda.mo nvda

@REM Generate Slovak MO file
cd %scripts%\..\source\locale\sk\LC_MESSAGES
python %scripts%\msgfmt.py -o nvda.mo nvda

cd %scripts%

title MO language files generation completed
pause
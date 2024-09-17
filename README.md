# Thunderbird-Sieve-Converter
This Python script converts Thunderbird email filter rules (from `msgFilterRules.dat`) to Sieve script format, which can be used with email systems supporting Sieve filtering, such as Roundcube.

# Usage
```
python filter_converter.py /path/to/msgFilterRules.dat [output_file.sieve]
```
- The first argument is the path to the Thunderbird filter file (msgFilterRules.dat).
- The second argument (optional) specifies the output Sieve file. If omitted, it defaults to roundcube.sieve.

# Common Bug to Watch Out For
When reviewing the generated Sieve script, please ensure the following header format is correct:
```
header :contains "<header>" "<value>"
```

* If the header contains more than one pair of quotation marks, for example, `header :contains ""received""`, this is incorrect.
* The script aims to clean and format headers correctly, but in case you encounter extra or misaligned quotes in the Sieve file, you may need to double-check the msgFilterRules.dat format or notify me of the issue.

# Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements or find any bugs.

# License
This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.


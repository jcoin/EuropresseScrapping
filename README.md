# EuropresseScrapping

This is a  selenium test script to generate a PDF file from a newspaper specific edition.
Remember that this PDF falls under international copyrights laws.
I am not responsible for the use you make of this script or of its result.

This is meant to be a proof of concept and was a hobby to start coding in python and use selenium.

## Prerequisites 

- You'll need a reader card from the BNF (Bibliotheque Nationale de France) for this to work  
- This script uses a selenium docker image (chromium)
- PyPDF2, selenium and telegram bot python library (see requirements.txt)

## Configuration

- Create a copy of the example_config.ini and rename it config.ini
- Modify following lines from config.ini to be in line with your data

| section     | key |  Description |
| ----------- | ----------- | ----------- |
| bnf |  username  | user account at BNF.FR       |
| bnf | password   | user account password at BNF.FR        |
| env | download_dir   | the download path for individual pages download   |
| env | result_dir   | directory where the merged pdf will be generated  |

## Args

	-j;--journal : name of the newspaper -- optional, reverts to "Le Monde" by default
	-e;--edition : date of publication -- optional, reverts to current day by default

## Newspaper value

The newspaper names are listed in the config.ini file. 

They are chosen to enable searching for the last edition available

Some newspapers are available on europesse only 24h after public release 

## Todo 

- A lot
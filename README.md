# EuropresseScrapping

This is a  selenium test script to generate a PDF file from a newspaper specific edition.
Remember that this PDF falls under international copyrights laws.
I am not responsible for the use you make of this script or of its result.

This is meant to be a proof of concept and was a project for me to start coding in python and use selenium.

## Prerequisites 

- You'll need a reader card from the BNF (Bibliotheque Nationale de France) for this to work  
- This script uses the selenium geckodriver  
- You'll need to create a specific profile in Firefox (or any gecko based browser) 
	- Download directory should be set to an empty directory
	- Preference for handling application/pdf mime type files should be set to download
	- Uncheck the box to confirm download location
- PyPDF2 and selenium python library (see requirements.txt)

## Configuration

- Create a copy of the example_config.ini and rename it config.ini
- Modify following lines from config.ini to be in line with your data

| section     | key |  Description |
| ----------- | ----------- | ----------- |
| bnf |  username  | user account at BNF.FR       |
| bnf | password   | user account password at BNF.FR        |
| env | profile_path   | the path where your Firefox profile is located        |
| env | download_dir   | the download path specified in your Firefox profile   |
| env | service   | location of the geckodriver   |
| env | result_dir   | directory where the pdf will be generated   |

## Args

	-j;--journal : name of the newspaper -- optional, reverts to "Le Monde" by default
	-e;--edition : date of publication -- optional, reverts to current day by default

## Newspaper value

The newspaper names are listed in the config.ini file.

Note that the correct date of publication for evening newspapers is handled by the script 

## Todo 

- Exception handling
- Configure wait time
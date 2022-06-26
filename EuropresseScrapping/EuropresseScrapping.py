
import os,sys,getopt,configparser,glob
from PyPDF2 import PdfFileReader, PdfFileWriter
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import   FirefoxProfile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from time import sleep
from selenium.common.exceptions import TimeoutException
from datetime import date, timedelta

def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)

def ScrappingTest(journalID,tomorrow_date,profile_path,gecko_path,auth_url,user,pwd):
    
    ser = Service(gecko_path)
    opt = FirefoxOptions()
    opt.add_argument("-profile")
    opt.add_argument(profile_path)
    opt.headless=True
    opt.set_preference("general.warnOnAboutConfig", False)

    ff_driver = webdriver.Firefox(service=ser,options=opt)

    ff_driver.get(auth_url)
    ff_driver.maximize_window()
    sleep(15)
    username=ff_driver.find_element(by=By.NAME, value="username")
    username.send_keys(user)
    password=ff_driver.find_element(by=By.NAME, value="password")
    password.send_keys(pwd)
    password.submit()
    sleep(3)
    ff_driver.set_page_load_timeout(10)
    ff_driver.get("https://nouveau-europresse-com.bnf.idm.oclc.org/WebPages/Pdf/SearchResult.aspx?DocName=pdf%C2%B7"+tomorrow_date+"%C2%B7"+journalID+"_P%C2%B71")
    ff_driver.switch_to.frame('ListDoc')
    list_of_links = ff_driver.find_elements(by=By.XPATH,value='//a')
    to_scrape=[]
    for link in list_of_links:
        to_scrape.append(link.get_attribute('href'))

    for click in to_scrape:
        print(click)
        try:
            ff_driver.get(click)
        except TimeoutException:
            pass
    ff_driver.quit()

def main(argv):
   journalname = ''
   editiondate = ''
   try:
      opts, args = getopt.getopt(argv,"hj:e:",["journal=","edition="])
   except getopt.GetoptError:
      print ('EuropesseScrapping.py -j <journalname> -e <editiondate>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('EuropesseScrapping.py -j <journalname> -e <editiondate>')
         sys.exit()
      elif opt in ("-j", "--journal"):
         journalname = arg
      elif opt in ("-e", "--edition"):
         editiondate = arg
   

   conf= configparser.ConfigParser(interpolation=None)
   conf.read('.\config.ini')
   download_dir=conf['env']['download_dir']
   result_dir=conf['env']['result_dir']
   profile_path =conf['env']['profile_path']
   service =conf['env']['service']
   auth_url=conf['bnf']['auth_url']
   bnf_user=conf['bnf']['username']
   bnf_pwd=conf['bnf']['password']

   
   press_code={} 
   for option in conf.options('europresse'):
        press_code[option] = conf.get('europresse', option)
   
   journalID=''
   if journalname == '':
       journalID='LM'
   elif journalname in press_code:
       journalID=press_code.get(journalname)
   else :
       print('journal should be one of the following')
       print(press_code.keys())
       sys.exit(2)

   if editiondate=='':
        journal_date=date.today()
        if journalID=='LM':
            journal_date=journal_date+timedelta(days=1)
            
        date_string=journal_date.strftime('%Y%m%d')
   else :
        date_string=editiondate

   print("Recupere edition du " + date_string)
   ScrappingTest(journalID,date_string,profile_path,service,auth_url,bnf_user,bnf_pwd)

   print("Merge PDF")
   sleep(5)

   glob_pattern    ="\pdf?"+date_string+"?"+journalID+"_p*[!)].pdf"
   glob_pattern_del="\pdf?"+date_string+"?"+journalID+"_*.pdf"


   pdfs_to_merge = filter( os.path.isfile,
                        glob.glob(download_dir + glob_pattern) )
    
    # Sort list of files based on last modification time in ascending order
   pdfs_to_merge = sorted( pdfs_to_merge,
                        key = os.path.getmtime)
   merge_pdfs(pdfs_to_merge,output=result_dir + "\pdf_"+date_string+"_"+journalID+".pdf")

   print("Merge PDF OK - Nettoyage")
   pdfs_to_del = filter( os.path.isfile,
                        glob.glob(download_dir + glob_pattern_del) )
   for pdf in pdfs_to_merge:
      print(pdf)
      os.remove(pdf)
   print("Finished")


if __name__ == "__main__":
   main(sys.argv[1:])
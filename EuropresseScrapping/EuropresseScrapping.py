#!/srv/selenium/bin/python3
import os,sys,getopt,configparser,glob
import asyncio

from telegram import InlineQueryResultArticle, InputTextMessageContent , Bot
from telegram.ext import Application, CommandHandler, InlineQueryHandler

from time import sleep

from PyPDF2 import PdfReader, PdfWriter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains

async def doc_tel(api_key,channel_id,pdf_file):

   bot = Bot(api_key)
   with open(pdf_file, "rb") as f:
     await  bot.send_document(channel_id, f)

async def msg_tel(api_key,channel_id,message):
   bot = Bot(api_key)
   await  bot.send_message(channel_id, message)


def find_last_pdf(dir, id) :
   print("Find Last PDF -- Start")  
   glob_pattern_rename="/pdf_????????_"+id+".pdf"

   pdfs_downloaded = sorted(filter( os.path.isfile,
                            glob.glob(dir + glob_pattern_rename) ))

   print(pdfs_downloaded)
   if pdfs_downloaded :
      return((pdfs_downloaded[-1])[30:38])
   else: 
      return ('')
      
   print("Find Last PDF -- End") 

def rename_pdfs(paths):
    for file in paths:
      new_file=file[:-5]+"0"+file[-5:]
      print("Rename to:"+new_file)
      os.rename(file,new_file)


def merge_pdfs(paths, output):
    pdf_writer = PdfWriter()

    for path in paths:
        pdf_reader = PdfReader(path)
        for page in range(len(pdf_reader.pages)):
            # Add each page to the writer object
            pdf_writer.add_page(pdf_reader.pages[page])

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)

def testFinished(files):
  result = False 
  for file in files:
    if (result == False):
       result = file.endswith(".crdownload")
  return (result)
    
def BNF_auth(auth,user,pwd,drv_add):
   opt = ChromeOptions()
   opt.enable_downloads = True
   opt.add_argument("--headless=new")
   opt.add_experimental_option('prefs', {
      "download.prompt_for_download": False, #To auto download the file
      "download.directory_upgrade": True,
      "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    })
   print("BNF_auth -- Opt OK")


   remote_driver = webdriver.Remote(
      command_executor=drv_add,
      options=opt)
      
      
   print("BNF_auth -- Driver OK")

   remote_driver.get(auth)

   print("Wait+auth")
   sleep(15)
   username=remote_driver.find_element(by=By.NAME, value="username")
   username.send_keys(user)
   password=remote_driver.find_element(by=By.NAME, value="password")
   password.send_keys(pwd)
   password.submit()
   sleep(10)
   remote_driver.set_page_load_timeout(10)

   return (remote_driver)
  
def ScrappingPdf(eDate,journalID,ff_driver,directory):
   print("ScrappingPdf -- Start")
  
   print(ff_driver.current_url) 
   url_pub='https://nouveau-europresse-com.bnf.idm.oclc.org/Pdf'

   ff_driver.get(url_pub)
   sleep(2)

   summaryPage="https://nouveau-europresse-com.bnf.idm.oclc.org/WebPages/Pdf/SearchResult.aspx?DocName=pdf%C2%B7"+eDate+"%C2%B7"+journalID+"_P%C2%B71"

   print(summaryPage)

   ff_driver.get(summaryPage)
   ff_driver.switch_to.frame('ListDoc')
   list_of_links = ff_driver.find_elements(by=By.XPATH,value='//a')
   to_scrape=[]
   for link in list_of_links:
        to_scrape.append(link.get_attribute('href'))

   for click in to_scrape:
        print(click)
        #TODO : don't download if file exists
        try:
            ff_driver.get(click)
            sleep(2)
        except TimeoutException:
            pass

   files = ff_driver.get_downloadable_files()
   not_finished=True 
   while (not_finished == True):
       not_finished = testFinished(files)
       files = ff_driver.get_downloadable_files()
 
   for file in files:
       ff_driver.download_file(file, directory)
 
   print("ScrappingPdf -- Finished")

def find_edition(name,date_arg,edition,ff_driver):
  print("Find Edition -- Start")
  edition_string=''
  if '' != date_arg : 
   edition_string=date_arg
  else :
   url_pub='https://nouveau-europresse-com.bnf.idm.oclc.org/Pdf'
   ff_driver.get(url_pub)
   sleep(2)
   try: 
      sel_search=ff_driver.find_element(By.ID,'sources-search')
      ActionChains(ff_driver)\
         .send_keys_to_element(sel_search,name)\
         .perform()
      sleep(6)
      css_selectorString='[id="sourceLastEdition"][pubid="'+edition+'_P"]'
      sel_docs=ff_driver.find_element(By.ID, 'docList')
      sel_edition=sel_docs.find_element(By.CSS_SELECTOR,css_selectorString) 
      edition_string=sel_edition.get_attribute("lastedition").replace("-","")
   except selenium.common.exceptions.NoSuchElementException:
      print("Find Edition -- No element")
 
   return (edition_string) 
   print("Find Edition -- End")

def main(argv):
   print("Main -- Start")
   print("Main -- Args reading")
   
   journalname = ''
   editiondate = ''
   scrapPDF=True

   try:
      opts, args = getopt.getopt(argv,"shj:e:",["journal=","edition="])
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
      elif opt in ("-s" ):
         scrapPDF=False

   print("Main -- Read Config")
   conf= configparser.ConfigParser(interpolation=None)
   conf.read(sys.path[0]+'/config.ini')

   auth_url=conf['bnf']['auth_url']
   bnf_user=conf['bnf']['username']
   bnf_pwd=conf['bnf']['password']
   download_dir=conf['env']['download_dir']
   result_dir=conf['env']['result_dir']

   press_code={} 
   for option in conf.options('europresse'):
        press_code[option] = conf.get('europresse', option)
   print(press_code)


   # TODO : effacement avant dernier fichier telechargé. 
   if journalname=='' :    
      journalID="LM"
      journalname="monde"
   elif journalname in press_code:
       journalID=press_code.get(journalname)
       print("ID:"+journalID)
       print("Name:"+journalname)
   else :
       print('journal should be one of the following')
       print(press_code.keys())
       sys.exit(2)

   download_dir=conf['env']['download_dir']
   result_dir=conf['env']['result_dir']
   Tel_api_key=conf['telegram']['api']
   Tel_channel_id=conf['telegram']['channel']
   drv_ad=conf['selenium']['url']


   print("Main -- Scrap") 

   selenium_driver=BNF_auth( auth_url,bnf_user,bnf_pwd,drv_ad)

   last_date_downloaded = find_last_pdf(result_dir, journalID)
  

   print("Main -- Last Download:" +last_date_downloaded) 
   date_string=find_edition(journalname,editiondate,journalID,selenium_driver)
   
   print("Main -- Edition :"+date_string) 
   if (date_string != '') and ((last_date_downloaded != date_string) or (last_date_downloaded == '' )) : 
      
       output_file=result_dir + "/pdf_"+date_string+"_"+journalID+".pdf"

       if scrapPDF:
          ScrappingPdf(date_string,journalID,selenium_driver,download_dir)
          print("Main -- Merge")

          glob_pattern    ="/pdf?"+date_string+"?"+journalID+"_p*[!)].pdf"
          glob_pattern_del="/pdf?"+date_string+"?"+journalID+"_*.pdf"
          glob_pattern_rename="/pdf?"+date_string+"?"+journalID+"_p?[!)].pdf"

          pdfs_to_rename = filter( os.path.isfile,
                            glob.glob(download_dir + glob_pattern_rename) )

          rename_pdfs(pdfs_to_rename)
          print("Main -- Rename OK")
          
          pdfs_to_merge = filter( os.path.isfile,
                            glob.glob(download_dir + glob_pattern) )
         
          pdfs_to_merge = sorted( pdfs_to_merge )
          print("Main -- Merge OK")
          
          merge_pdfs(pdfs_to_merge,output=output_file)

          pdfs_to_del = filter( os.path.isfile,
                            glob.glob(download_dir + glob_pattern_del) )

          for pdf in pdfs_to_del:
             print(pdf)
             os.remove(pdf)

          print("Main -- Send")
          asyncio.run(doc_tel(Tel_api_key,Tel_channel_id,output_file))
   elif (date_string == '') : 
          asyncio.run(msg_tel(Tel_api_key,Tel_channel_id,"Pb Recuperation Edition"))

   selenium_driver.quit()
   print("Main -- Finished")
   
if __name__ == "__main__":
   main(sys.argv[1:])

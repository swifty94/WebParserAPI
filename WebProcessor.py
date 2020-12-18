import requests
from bs4 import BeautifulSoup
from collections import Counter
import subprocess as sp
import logging
import sqlite3
from tld import get_tld
FORMAT = '%(asctime)s  %(levelname)s : %(module)s -> %(funcName)s -> %(message)s'
logging.basicConfig(filename="application.log", level=logging.INFO, format=FORMAT)

class WebProcessor():
    
    @staticmethod
    def getTags(url):
        tag_list = []
        try:
            logging.info('Started processing URL: ' + url)
            response = requests.get(url)
            page = BeautifulSoup(response.text, 'html.parser')
            for child in page.recursiveChildGenerator():
                if child.name:
                    tag_list.append(child.name)

            tags = Counter(tag_list)
            return dict(tags)
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            logging.info('Finished processing URL: ' + url)
    
    @staticmethod
    def getInfo(url):
        try:
            logging.info('Started processing URL: ' + url)
            get_domain = get_tld(f"{url}", as_object=True)
            domain = get_domain.fld
            ipaddr = sp.getoutput(f"dig A {domain} +short|head -n1")
            registrar = sp.getoutput(f"whois {domain}|grep 'Registrar:'|tail -n 1|sed -e 's/Registrar://g'")
            ipaddr_owner = sp.getoutput(f"whois {ipaddr}"+"|grep 'OrgName:'|awk '{print $2}'")
            info = {
                "Domain name": domain,
                "Registrar": registrar,
                "IP address": ipaddr,
                "IP address owner": ipaddr_owner
            }
            return info
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            logging.info('Finished processing URL: ' + url)


    @staticmethod
    def getTechStack(url):
        try:
            logging.info('Started processing URL: ' + url)
            response = requests.get(url)
            header = dict(response.headers)
            header = {k.lower(): v for k, v in header.items()}
            techstack = {}
            if 'server' in header:
                webserver = header['server']
                techstack['Web-server'] = webserver
            if 'x-powered-by' in header:
                program_lang = header['x-powered-by']
                techstack['Programming language'] = program_lang            
            return techstack
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            logging.info('Finished processing URL: ' + url)

    @staticmethod
    def generateResult(url):
        try:
            logging.info('BEGIN')
            tags = WebProcessor.getTags(url)
            info = WebProcessor.getInfo(url)
            techstack = WebProcessor.getTechStack(url)
            domain  = info['Domain name']
            ipaddr = info['IP address']
            ipaddr_owner = info['IP address owner']
            registrar = info['Registrar']
            if 'Web-server' in techstack:
                webserver = techstack['Web-server']
            else:
                webserver = 'Not found'
            if 'Programming language' in techstack:
                program_lang = techstack['Programming language']
            else:
                program_lang = 'Not found'
            html = str(tags)
            data = (domain, ipaddr, ipaddr_owner, registrar, webserver, program_lang, html)
            return data
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            logging.info('END')
    
    @staticmethod
    def insertData(url):        
        try:
            data = WebProcessor.generateResult(url)
            connection = sqlite3.connect('app.db')
            cursor = connection.cursor()
            sql = """
            INSERT INTO websiteData (domain, ipaddr, ipaddr_owner, registrar, webserver, program_lang, html)
            VALUES (?,?,?,?,?,?,?)
            """
            cursor.execute(sql,data)
            connection.commit()
            identifier = cursor.lastrowid
            cursor.close()
            logging.info(f'Data processing using SQL \n {sql}')
            return identifier
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            if (connection):
                connection.close()

    @staticmethod
    def selectList():
        try:
            connection = sqlite3.connect('app.db')
            cursor = connection.cursor()
            sql = "SELECT id, domain FROM websiteData ORDER BY id ASC"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            logging.info(f'Processing data with SQL \n {sql}')
            return dict(result)
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            if (connection):
                connection.close()
    
    @staticmethod
    def selectById(id):
        try:
            connection = sqlite3.connect('app.db')
            cursor = connection.cursor()
            sql = f"""
            SELECT domain, ipaddr, ipaddr_owner, registrar, webserver, program_lang, html
            FROM websiteData
            WHERE id={id}
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            for value in result:
                outcome = {
                    "Domain name": value[0],
                    "IP address": value[1],
                    "IP address owner": value[2],
                    "Registrar": value[3],
                    "Web-server": value[4],
                    "Programming language": value[5],
                    "HTML tags": value[6]
                }
            cursor.close()
            logging.info(f'Processing data with SQL \n {sql}')
            return outcome
        except Exception as e:
            logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        finally:
            if (connection):
                connection.close()
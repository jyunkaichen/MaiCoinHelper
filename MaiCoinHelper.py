import time
import requests
import smtplib  
from email.mime.text import MIMEText  
from bs4 import BeautifulSoup
from datetime import datetime

smtpHost = 'smtp.gmail.com'
sender = '*****@gmail.com'
password = "********"
receiver = '*****@gmail.com'

# send E-mail to yourself
def sendgmail(content):
    msg = MIMEText(content, 'plain', 'utf-8') 
    msg['Subject'] = "Maicoin currency value changes!"
    msg['From'] = sender
    msg['To'] = receiver

    smtpServer = smtplib.SMTP_SSL(smtpHost, 465)    # SMTP_SSL          
    smtpServer.ehlo()
    smtpServer.login(sender, password)          
    smtpServer.sendmail(sender, receiver, msg.as_string()) 
    smtpServer.quit()

class Currency:
    def __init__(self, soup, curid):
        self.soup = soup
        self.curid = curid # currency's id
        self.temp_currency = self.getprice()
        self.temp_currency_time = 0
        self.up_currency = True
        self.name = curid.split('_')[1] #latest_***_price
    def getprice(self): # get currency's price
        str = self.soup.find(id = self.curid).get_text().strip().split("NT$")[1].split(',') # NT$2,000
        tmp = ' '
        for i in str:
            tmp += i
        return float(tmp)
    def update(self, base_currency, n):
        self.base_currency = base_currency
        self.temp_currency_time += n
        # change the base_price and reset timer in three conditions
          #1.Previously up, then go down (Relatively high)
          #2.Previously up, then go down (Relatively low)
          #3.The timer goes over 24hrs
        if self.temp_currency_time < 60*60*24: # 24hrs
            if self.temp_currency >= self.base_currency:
                self.up_currency = True
                persent = (self.temp_currency - self.base_currency) / base_currency *100
                if persent >= 5: # bigger than 5% (up)
                    content = self.name + 'went up' + str('%.2f' %persent) + '%' + 'in 24 hrs!' # Two digits after the decimal point
                    sendgmail(content)
                    self.base_currency = self.temp_currency
                    self.temp_currency_time = 0
            elif self.temp_currency < self.base_currency:
                self.up_currency = False
                persent = (base_currency - self.temp_currency) / self.base_currency *100
                if persent >= 5: # bigger than 5% (down)
                    content = self.name + 'went down' + str('%.2f' %persent) + '%' + 'in 24 hrs!' # Two digits after the decimal point
                    sendgmail(content)
                    self.base_currency = self.temp_currency
                    self.temp_currency_time = 0
        else:
            self.base_currency = self.temp_currency
            self.temp_currency_time = 0
        print(self.name, "price =", self.temp_currency, "\n")
        return self.base_currency

# execute every n seconds
def timer(n):
        # initial btc, usdt, eth, ltc base_price
        res = requests.get("https://www.maicoin.com/users/sign_in")
        soup = BeautifulSoup(res.text, 'html.parser')

        base_btc = Currency(soup, "latest_btc_price").getprice()
        base_usdt = Currency(soup, "latest_usdt_price").getprice()
        base_eth = Currency(soup, "latest_eth_price").getprice()
        base_ltc = Currency(soup, "latest_ltc_price").getprice()

        while True:
            res = requests.get("https://www.maicoin.com/users/sign_in")
            soup = BeautifulSoup(res.text, 'html.parser')
            # btc
            bb = Currency(soup, "latest_btc_price").update(base_btc, n)
            base_btc = bb
            # usdt
            bu = Currency(soup, "latest_usdt_price").update(base_usdt, n)
            base_usdt = bu
            # eth
            be = Currency(soup, "latest_eth_price").update(base_eth, n)
            base_eth = be
            # ltc
            bl = Currency(soup, "latest_ltc_price").update(base_ltc, n)
            base_ltc = bl

            time.sleep(n)

# update every 60 seconds
timer(60)
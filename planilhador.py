#%%
from datetime import datetime
import json
from pynubank import Nubank, MockHttpClient
import re
import gspread
import os
from google.oauth2 import service_account
import os
import locale

class PlanilhaUpdater():
	def __init__(self, user_folder):
		self.set_br()
		# login google sheets
		self.gc = self.login_gc(json_file=os.path.join(user_folder, "credentials.json"))

		# saved user params 
		with open(os.path.join(user_folder, "params.json")) as f:
			self.user_params = json.loads(f.read())

		# sheet
		self.sheet = self.gc.open(self.user_params["sheet"])

		# Nubank client
		self.nu = Nubank()
		self.nu_cert_file = os.path.join(user_folder, "cert.p12")
		
	def set_br(self):
		# Set locale
		# nt = windows, posix=linux
		if os.name=="nt":
			locale.setlocale(locale.LC_ALL,"pt_BR")
		elif os.name=="posix":
			locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")

	def login_gc(self, json_file):
		scopes = ["https://www.googleapis.com/auth/spreadsheets",
			"https://www.googleapis.com/auth/drive"]
		credentials = service_account.Credentials.from_service_account_file(json_file)
		scoped_credentials = credentials.with_scopes(scopes)
		return gspread.authorize(scoped_credentials)

	
	def get_entry(self, statement):
		#SAÍDA	data	valor	cartão	tipo	Detalhe
		typ = statement.get("__typename")
		date = datetime.strptime(statement.get("postDate"), "%Y-%m-%d") #2021-04-21T10:01:48Z
		ammount = f"{str(statement.get('amount')).replace('.',',')}"
		entry = ["", date.strftime("%d/%m"), ammount]

		isDebit=True

		try:
			if typ=="TransferInEvent": #ENTRADA	data	valor	tipo
				isDebit=False
				entry[0] = f'Transferencia de {statement.get("originAccount").get("name")}'
				entry.append("")
			elif typ=="DebitPurchaseEvent":
				entry[0] = re.split("(.*) - (.*)", statement.get("detail"))[1]
				entry.append("débito")
				entry.append("")
				entry.append("")
			elif typ=="PixTransferOutEvent":
				name = re.split("(.*)\n(.*)", statement.get("detail"))[1]
				entry[0] = f"Pix {name}"
				entry.append("débito")
				entry.append("")
				entry.append("")
			elif typ=="BillPaymentEvent":
				bill = re.split("(.*) - (.*)", statement.get("detail"))[1]
				entry[0] = f"Boleto {bill}"
				entry.append("débito")
				entry.append("")
				entry.append("")
			elif typ=="TransferOutEvent":
				name = re.split("(.*) - (.*)", statement.get("detail"))[1]
				entry[0] = f"Tranferencia p/: {name}"
				entry.append("débito")
				entry.append("")
				entry.append("")
			elif typ=="BarcodePaymentEvent":
				bill = re.split("(.*) - (.*)", statement.get("detail"))[1]
				entry[0] = f"Boleto {bill}"
				entry.append("débito")
				entry.append("")
				entry.append("")
		except:
			# shouldnt get here
			entry[0] = str(statement)
			entry.append("ERROR")

		return isDebit, entry

	def insert_statements(self, last_date=None, include_credit=True, include_debit=True, **kwargs):
		# Auth
		nu = Nubank()
		nu.authenticate_with_refresh_token(self.user_params["token"], self.nu_cert_file)

		# Since when
		if last_date is None:
			last_date = self.user_params.get("last_update", datetime(2021, 6, 14))

		# List of entries to post
		entries = []

		if include_credit:
			for statement in nu.get_card_statements():
				date = datetime.strptime(statement["time"], "%Y-%m-%dT%H:%M:%SZ") #2021-04-21T10:01:48Z

				if date > last_date:
					entry = [statement["description"],date.strftime("%d/%m"), f"{str(statement['amount']/100).replace('.',',')}", "crédito", "",statement["title"] ]
					entries.append((True, date.strftime("%B"), entry))
		
		if include_debit:
			for statement in nu.get_account_statements():
				try:
					date = datetime.strptime(statement.get("postDate"), "%Y-%m-%d") #2021-04-21T10:01:48Z
				except:
					print("did not get postDate... dont know what to do")
					continue

				if date >= last_date:
					isDebit, entry = self.get_entry(statement)
					if entry[0] == "Boleto Cartão Nubank":
						continue
					entries.append((isDebit, date.strftime("%B"), entry))

		entries = sorted(entries, key=lambda x:x[2][1])
		table = None
		for isDebit, month, entry in entries:
			if  (table is None) or (table.title != month):
				try:
					table = self.sheet.worksheet(month)
				except gspread.WorksheetNotFound:
					self.sheet.add_worksheet(month, 11, 67)
					table = self.sheet.worksheet(month)
					table.insert_row(['ENTRADA', 'data', 'valor', 'tipo', "  ", 'SAÍDA', 'data', 'valor', 'cartão', 'tipo', 'detalhe'])

			range_out = f"F1:J{table.row_count-2}"
			range_in = f"A1:D{table.row_count-2}"
			if isDebit:
				table.append_row(entry, table_range=range_out, value_input_option='USER_ENTERED')
			else:
				table.append_row(entry, table_range=range_in, value_input_option='USER_ENTERED')

# %%
pedro = PlanilhaUpdater(r"C:\Users\Pedro\Desktop\planilhador\users\Pedro")
pedro.insert_statements(last_date=datetime(2021,6,1))
# %%

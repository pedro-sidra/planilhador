#%%
import shutil
from pynubank import Nubank
import json
import pynubank.cli
import os

if __name__=="__main__":
	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(dname)

	# Inicial
	name = input("Digite o nome do usuário")
	os.mkdir(f"users/{name}")
	os.chdir(f"users/{name}")

	# NUBANK
	print("Iniciando geração de certificado do nubank...")
	pynubank.cli.main()

	print("Certificado geardo... fazer login mais uma vez para finalizar")
	nu = Nubank()
	cpf = input("Digite o CPF:")
	senha = input("Digite a senha:")
	refresh = nu.authenticate_with_cert(cpf, senha, 'cert.p12')

	print("login nubank finalizado")

	# GOOGLE
	print("========================")
	print("Siga as etapas para autorizar o google: https://medium.com/pyladiesbh/gspread-trabalhando-com-o-google-sheets-f12e53ed1346")
	creds_path = input("Digite aqui o caminho do arquivo credentials.json:")
	shutil.copyfile(creds_path, "credentials.json")
	with open("credentials.json","r") as f:
		creds = json.loads(f.read())
	print("compartilhe a planilha desejada com esse email (permissao de editor):")
	print("===========")
	print(f"{creds['client_email']}")
	print("===========")
	sheet_name = input("Digite aqui o nome da planilha(incluindo pastas)")

	# SAVE
	user_params = dict(token=refresh, sheet=sheet_name)
	with open("params.json", "w") as f:
		f.write(json.dumps(user_params))
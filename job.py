from planilhador import PlanilhaUpdater
import argparse
import os
import glob

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Update sheets in google drive from nubank interface')
	args = parser.parse_args()

	abspath = os.path.abspath(__file__)
	dname = os.path.dirname(abspath)
	os.chdir(dname)

	users = glob.glob("users/*")
	for user_folder in users:
		handler = PlanilhaUpdater(user_folder)
		handler.insert_statements()
		handler.save_state()

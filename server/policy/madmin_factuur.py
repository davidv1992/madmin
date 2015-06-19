from madmin_products import query_product
from madmin_vereniging import query_vereniging
from madmin_budget import budget_query
from os import system
import os
from smtplib import SMTP
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from math import copysign
import logging

log = logging.getLogger(__name__)

#factuur types
factuur_type_inkoop  = 1
factuur_type_verkoop = 2

factuur_name_mapping = {
	factuur_type_inkoop: 'inkoop',
	factuur_type_verkoop: 'verkoop'
}

factuur_type_mapping = {
	'inkoop': factuur_type_inkoop,
	'verkoop': factuur_type_verkoop
}

factuur_pdf_dir = os.path.dirname(os.path.abspath(__file__))+'/../../../writable/facturen/'
factuur_log = os.path.dirname(os.path.abspath(__file__))+'/../../../writable/texlog.txt'
factuur_sender = 'www-madmin@science.ru.nl'
default_receiver = 'olympusfacturen@science.ru.nl'

template = R"""
\documentclass[a4paper]{article}
\usepackage{graphicx}
\usepackage{marvosym}
\usepackage{ifthen}
\usepackage[utf8]{inputenc}

\newcommand{\euro}{\EUR\ }
\newcommand{\ibannetje}{NL19 ABNA 0448 1916 28}

\usepackage[dutch]{babel}
\pagestyle{empty}

\textwidth = 13cm

\date{}

\begin{document}
\flushright
\includegraphics[width=5cm]{olympuslogo} \\

Heyendaalseweg 135\\
6525 AJ\ Nijmegen \\
olympus@science.ru.nl \\
Bank: \ibannetje
\flushleft

\begin{tabular}{l l}
\textit{Vereniging:} & %(vereniging)s \\
\textit{Factuurnummer:} & %(factuurnummer)s  \\
\textit{Factuurdatum:} & %(factuurdatum)s  \\
\textit{Afnamedatum:} & %(afnamedatum)s  \\
\textit{Verantwoordelijke:} & %(verantwoordelijke)s \\
\textit{Speciale saldo:} & %(speciaalsaldo)s \\
\end{tabular}

\vspace{1cm}

\begin{tabular}{p{6cm} c c r r}
\emph{Specificatie} & \emph{Aantal} & \emph{Stukprijs} & \emph{Prijs} \\
\hline
%(factuurregels)s
\hline
{\bf Totaal:} & & & \euro %(totaal).2f \\
\end{tabular}
\vspace{0.3cm}

Na deze factuur bedraagt het borrelsaldo nog \EUR %(borrelsaldo).2f, en het speciale saldo nog \EUR %(speciaalsaldona).2f. Extra borrelsaldo kan overgemaakt worden naar rekeningnummer \ibannetje\ t.n.v. Olympus te Nijmegen.

\vfill

\begin{tabular}{p{14cm}}
\hline
\end{tabular}

\begin{center}
\footnotesize
Olympus - Koepel van studieverenigingen van de Faculteit NWI te Nijmegen\\
Rekeningnummer \ibannetje\ t.n.v. Olympus te Nijmegen
\end{center}
\end{document}
"""


def _moneyConvert(value):
	cents = value % 100
	value /= 100
	if cents < 10:
		return str(value)+ ",0" + str(cents)
	return str(value) + "," + str(cents)

def process_factuur(factuur, fac_id):
	#process regels
	
	log.debug("Start email generation")
	regels = ""
	totaal = 0
	indx = 0
	for regel in factuur['regels']:
		indx+=1
		log.debug("factuurregel processing %s of %s", indx, len(factuur['regels']))
		if 'naam' in regel:
			naam = regel['naam']
		else:
			naam = query_product(regel['product_id'])[0]['naam']
		regels += naam + " & " + str(regel['aantal']) + " & " 
		regels += _moneyConvert(regel['stukprijs']) + " & " + _moneyConvert(regel['totaalprijs']) + "\\\\\n"
		totaal += copysign(regel['totaalprijs'], regel['aantal'])
	
	
	log.debug("Querying global info")
	
	info = {}
	
	info['factuurregels'] = regels
	if 'vereniging' in factuur:
		info['vereniging'] = query_vereniging(factuur['vereniging'])[0]['naam']
	else:
		info['vereniging'] = factuur['leverancier']
	info['factuurnummer'] = factuur['volgnummer']
	info['factuurdatum'] = factuur['factuurdatum']
	info['afnamedatum'] = factuur['leverdatum']
	info['totaal'] = totaal / 100.0
	if 'verantwoordelijke' in factuur:
		info['verantwoordelijke'] = factuur['verantwoordelijke']
	else:
		info['verantwoordelijke'] = ""
	
	if 'saldo_basis_na' in factuur:
		info['borrelsaldo'] = factuur['saldo_basis_na']/100.0
	else:
		info['borrelsaldo'] = 0.0
	
	if 'saldo_speciaal' in factuur:
		info['speciaalsaldo'] = budget_query(factuur['saldo_speciaal'])[0]['naam']
		info['speciaalsaldona'] = factuur['saldo_speciaal_na'] / 100.0
	else:
		info['speciaalsaldo'] = ""
		info['speciaalsaldona'] = 0.0
	

	log.debug("formatting")
	texCode = template % info
	
	log.debug("producing pdf")
	
	texFilename = factuur_pdf_dir + "factuur" + str(fac_id) + ".tex"
	pdfFilename = factuur_pdf_dir + "factuur" + str(fac_id) + ".pdf"
	
	texfile = open(texFilename, "w")
	texfile.write(texCode)
	texfile.close()
	
	os.chdir(os.path.dirname(__file__) + "/../../../writable/facturen")

	if system("pdflatex " + texFilename + " >>" + factuur_log) <> 0:
		log.warning("Kon geen pdf produceren.")
		return
	
	log.debug("Pdf produced")

	pdfFile = open(pdfFilename, "rb")
	pdfAttachment = MIMEApplication(pdfFile.read())
	pdfFile.close()
	pdfAttachment.add_header('Content-Disposition', 'attachment', filename=pdfFilename)
	
	emailContentTemplate = R"""Dit is een automatisch gegenereerde mail met de factuur %(vereniging)s %(factuurnummer)s, %(verantwoordelijke)s."""
	emailSubjectTemplate = R"""Madmin factuur %(vereniging)s %(factuurnummer)s"""

	emailText = MIMEText(emailContentTemplate % info, 'plain')
	
	if 'vereniging' in factuur:
		receiver = query_vereniging(factuur['vereniging'])[0]['email']
	else:
		receiver = default_receiver
	
	email = MIMEMultipart()
	email['Subject'] = emailSubjectTemplate % info
	email['To'] = receiver
	email['From'] = factuur_sender
	email.attach(emailText)
	email.attach(pdfAttachment)
	
	s = SMTP()
	s.connect()
	s.sendmail(factuur_sender, receiver, email.as_string())
	s.quit()

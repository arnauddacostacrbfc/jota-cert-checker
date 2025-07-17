#!/usr/bin/env python3
"""
Author        :Julio Sanz
Website       :www.elarraydejota.com
Email         :juliojosesb@gmail.com
Description   :Script to check validity of a list of sites
Dependencies  :Python 3.x
Usage         :./jota-cert-checker.py
License       :GPLv3
"""

import ssl
import socket
from datetime import datetime
from tabulate import tabulate
import argparse
import re
 
warning_days = 80
alert_days = 40
table = []
# Email setup
sender = "jota-cert-checker@example.com"
subject = "SSL Certs expiration check"

def verify_ssl_certificate(hostname, port):
    context = ssl.create_default_context()
 
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.do_handshake()
            cert = ssock.getpeercert()
            expiry_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.utcnow()).days
            #print("Certificate is valid.")
            #print(f"SSL certificate for {hostname} expires on: {expiry_date}")
            #print(days_remaining)

            if days_remaining > warning_days:
                cert_status = "\033[92mOk\033[0m"
            elif days_remaining <= warning_days and days_remaining > alert_days:
                cert_status = "\033[0;33mWarning\033[0m"
            elif days_remaining <= alert_days and days_remaining > 0:
                cert_status = "\033[0;31mAlert\033[0m"
            elif days_remaining < 0:
                cert_status = "\033[1;31mExpired\033[0m"
            else:
                cert_status = "\033[1;30mUnknown\033[0m"
            
            new_row = [hostname, expiry_date, days_remaining, cert_status]
            table.append(new_row)
            return table

def output_terminal():
    print(tabulate(table, headers=["Site", "Expiration date", "Days left", "Status"], tablefmt="grid"))

    print("STATUS LEGEND")
    print(f"\033[0;32mOk\033[0m        - More than {warning_days} days left until the certificate expires")
    print(f"\033[0;33mWarning\033[0m   - The certificate will expire in less than {warning_days} days")
    print(f"\033[0;31mAlert\033[0m     - The certificate will expire in less than {alert_days} days")
    print(f"\033[1;31mExpired\033[0m   - The certificate has already expired")
    print(f"\033[1;30mUnknown\033[0m   - The site with defined port could not be reached")

def output_html():
    # Remove code colors to print the HTML table status column correctly
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    column_index = 3
    for i, row in enumerate(table):
        if i == 0:
            continue  # Skip header
        row[column_index] = ansi_escape.sub('', row[column_index])

    # Build HTML table
    rows = ""
    for row in table[1:]:
        if row[2] > warning_days:
            row_html = "".join(f"<td style=\"padding: 8px;background-color: #33FF4F;\">{cell}</td>" for cell in row)
            rows += f"<tr style=\"padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;\">{row_html}</tr>\n"
        elif row[2] <= warning_days and row[2] > alert_days:
            row_html = "".join(f"<td style=\"padding: 8px;background-color: #FFE032;\">{cell}</td>" for cell in row)
            rows += f"<tr style=\"padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;\">{row_html}</tr>\n"
        elif row[2] <= alert_days and row[2] > 0:
            row_html = "".join(f"<td style=\"padding: 8px;background-color: #FF8F32;\">{cell}</td>" for cell in row)
            rows += f"<tr style=\"padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;\">{row_html}</tr>\n"
        elif row[2] < 0:
            row_html = "".join(f"<td style=\"padding: 8px;background-color: #EF3434;\">{cell}</td>" for cell in row)
            rows += f"<tr style=\"padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;\">{row_html}</tr>\n"
        else:
            row_html = "".join(f"<td style=\"padding: 8px;background-color: #999493;\">{cell}</td>" for cell in row)
            rows += f"<tr style=\"padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;\">{row_html}</tr>\n"

    # Build HTML including the previous table
    html = f"""
	<!DOCTYPE html>
	<html>
			<head>
			<title>SSL Certs expiration</title>
			</head>
			<body style="background-color: lightblue;">
					<h1 style="color: navy;text-align: center;font-family: 'Helvetica Neue', sans-serif;font-size: 20px;font-weight: bold;">SSL Certs expiration checker</h1>
					<a href="https://github.com/juliojsb/jota-cert-checker" style="position: absolute; top: 0; right: 0px"><img loading="lazy" width="100" height="100" src="https://github.blog/wp-content/uploads/2008/12/forkme_right_darkblue_121621.png?resize=100%2C100" class="attachment-full size-full" alt="Fork me on GitHub" data-recalc-dims="1"></a>
					<table style="background-color: #C5E1E7;padding: 10px;box-shadow: 5px 10px 18px #888888;margin-left: auto ;margin-right: auto ;border: 1px solid black;">
					<tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;">
					<th style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;font-weight: bold;">Site</th>
					<th style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;font-weight: bold;">Expiration date</th>
					<th style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;font-weight: bold;">Days left</th>
					<th style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;font-weight: bold;">Status</th>
					</tr>
                    {rows}
	            <table style="background-color: #C5E1E7;padding: 10px;box-shadow: 5px 10px 18px #888888;margin-left: auto ;margin-right: auto ;border: 1px solid black;">
	                <tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;">
	                    <td style="padding: 8px;background-color: #33FF4F;">Ok</td> 
                        <td style="padding: 8px;background-color: #33FF4F;">More than {warning_days} days left until the certificate expires</td>
                    </tr> 
                    <tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;">
                        <td style="padding: 8px;background-color: #FFE032;">Warning</td>
                        <td style="padding: 8px;background-color: #FFE032;">The certificate will expire in less than {warning_days} days</td>
                    </tr> 
                    <tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;">
                        <td style="padding: 8px;background-color: #FF8F32;">Alert</td>
                        <td style="padding: 8px;background-color: #FF8F32;">The certificate will expire in less than {alert_days} days</td>
                    </tr> 
                    <tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;"> 
                        <td style="padding: 8px;background-color: #EF3434;">Expired</td> 
                        <td style="padding: 8px;background-color: #EF3434;">The certificate has already expired</td>
                    </tr> 
                    <tr style="padding: 8px;text-align: left;font-family: 'Helvetica Neue', sans-serif;"> 
                        <td style="padding: 8px;background-color: #999493;">Unknown</td> 
                        <td style="padding: 8px;background-color: #999493;">The site with defined port could not be reached</td>
                    </tr> 
                </table>
    </body>
    </html>
    """

    # Write to file
    with open("output.html", "w") as f:
        f.write(html)

    return html

def send_mail(html,email):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = email

    # Attach HTML body
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)

    print("HTML email sent.")

#
# MAIN
# 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, help='Path to sitelist file')
    parser.add_argument('-o', choices=['terminal', 'html'], required=True, help='Output, either "terminal" or "html"')
    parser.add_argument('-m', help='Destination mail address to send the report')
    args = parser.parse_args()

    with open(args.f) as urllist:
      for line in urllist:
        if ':' in line:
            parts = line.split(':', 1)  # Split into two parts only
            hostname = parts[0].strip()
            port = parts[1].strip()
        #print (line)
        verify_ssl_certificate(hostname, port)

    if args.o == 'terminal':
        output_terminal()
    if args.o == 'html':
        html = output_html()
    if args.o == 'html' and args.m:
        email = args.m
        send_mail(html,email)
    if args.o == 'terminal' and args.m:
        raise ValueError("Mail argument should not be used when using terminal output")

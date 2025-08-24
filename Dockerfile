FROM alpine:3.22.1

RUN apk add bash openssl mutt coreutils ssmtp && \
    mkdir /home/jota
COPY jota-cert-checker.sh /home/jota/
COPY html2img.py /home/jota/
COPY sitelist /home/jota/
COPY crontab.txt /home/jota/
COPY entry.sh /home/jota/
COPY ssmtp.conf /etc/ssmtp/
RUN chmod 755 /home/jota/*.sh
WORKDIR /home/jota
CMD ["/home/jota/entry.sh"]

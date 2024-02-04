FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN mkdir /root/scripts
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y openssh-server
RUN echo "PermitRootLogin yes" > /etc/ssh/sshd_config
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
RUN rm -rf /root/.ssh
RUN mkdir /root/.ssh
COPY id_rsa /root/.ssh/.
COPY id_rsa.pub /root/.ssh/.
COPY authorized_keys /root/.ssh/.
COPY config.sh /root/scripts/.
RUN cat /root/scripts/config.sh >> /root/.bashrc
COPY start-ssh.sh /root/scripts/.
CMD /root/scripts/start-ssh.sh

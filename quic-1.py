import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["figure.autolayout"] = True
fig = plt.figure()
# Using the Handshake trace on Nov 23, 2021

servers = ['aioquic', 'google', 'lsquic', 'mvfst', 'ngtcp2', 'picoquic', 'quic-go', 'quiche', 'quicly', 'quinn']
ackfreq_min = [2,2,2,10,2,2,2,1,2,1]
ackfreq_max = [8,10,8,10,4,6,9,38,2,17]
ackfreq_delta = ackfreq_max
for i in range(len(ackfreq_max)):
  ackfreq_max[i]=ackfreq_max[i]-ackfreq_min[i]+0.5
plt.xticks(ticks=range(len(servers)), labels=servers, rotation=90)
plt.yticks(ticks=[0,5,10,15,20,25,30,35,40])
#plt.boxplot(servers,ackfreq,whis='range')

plt.ylabel('Ack Frequency')
plt.bar(servers, ackfreq_max, bottom=ackfreq_min)
plt.title('Ack frequencies of different QUIC servers')
plt.show()
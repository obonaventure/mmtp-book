import matplotlib.pyplot as plt
plt.rcParams["figure.autolayout"] = True
fig = plt.figure()
# Using the Handshake trace on Nov 23, 2021

servers = ['cloudflare-quic.com','f5quic.com', 'h2o.example.net', 'h3.stammw.eu', 'http3-test.litespeedtech.com', 'ietf.akaquic.com','mew.org','nghttp2.org','quic.aiortc.org','quic.tech','test.privateoctopus.com']
cids = [20,8,9,8,8,8,8,18,8,20,8]
plt.xticks(ticks=range(len(servers)), labels=servers, rotation=90)
plt.yticks(ticks=[0,4,8,12,16,20])
plt.bar(servers,cids)
plt.ylabel('Bytes')
plt.title('Length of the CIDs advertised by different QUIC servers')
plt.show()
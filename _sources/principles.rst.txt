Principles of multipath transport
*********************************



   

Datagrams and Streams
=====================

Transport protocols are designed to provide a specific service to the application that uses them.

The simplest transport protocol is UDP :cite:`rfc768`. UDP enables applications to exchange datagrams. A datagram is a sequence of bytes that is sent as a message. In theory, applications should be able to send datagrams of up to 64 KBytes by leveraging IP's fragmentation capabilities. In practice, most applications try to avoid IP fragmentation and only exchange datagrams that are smaller than the MTU of their underlying network, typically about 1500 bytes.

Applications can use UDP to send an isolated datagram or a series of datagrams. These datagrams can be sent without any a priori exchange between the source and the destination applications. UDP does not guarantee that the sent datagrams will be delivered to their destination nor preserve ordering. UDP can detect transmission errors and discard the affected datagrams.

DCCP provides a different service to the applications. With DCCP, applications first open a connection and then use it to exchange sequences of datagrams. DCCP does not ensure a reliable delivery, but out-of-sequence datagrams can be reorder. Furthermore, DCCP includes congestion control schemes that rely on the measured round-trip-times and packet losses to adjust the transmission rate to the current network conditions.

TCP provides a reliable bytestream service to applications. The client must initiate a connection with a remote server to be able to exchange data. Once the connection is established, there is a bidirectionnal bytestream from the client to the server and another bytestream in the opposite direction. As long as the connection remains active, TCP ensures that the bytes pushed on the bytestream are delivered correctly and in-sequence to the distant peer. TCP also uses congestion and flow control to adjust the transmission rate to the current network conditions.

SCTP goes one step further than TCP by supporting multiple streams in both directions of a connection. SCTP is a message oriented protocol. The applications use SCTP to exchange messages that are composed of a variable number of bytes. SCTP applications can define several streams that are transported over a given association. Over a given stream, SCTP ensures that all messages are delivered in sequence. SCTP also supports unordered messages which can be delivered without waiting for other messages sent on the same stream. SCTP also uses congestion and flow control like TCP.


Middleboxes
===========

IP networks contain a variety of devices. Besides the endhosts, networking students are familiar with the switches and access points that relay layer-2 frames and the routers that relay packets. :numref:`fig-switches-routers` illustrates a network with two hosts communicating through one switch and one router. 


.. _fig-switches-routers:
.. tikz:: Routers and switches in the reference model
   :libs: fit, positioning
	  
   % inspired by https://newbedev.com/tikz-draw-simplified-ble-stack 	  
   \begin{tikzpicture}[
   node distance = 1mm and 0mm,
   box/.style = {draw, text width=40mm, inner sep=2mm, align=center}
   ]
		 
   \node (phy1) [box]                   {Phys.};
   \node (dl1) [box, above = of phy1]   {Data Link};
   \node (net1) [box, above = of dl1]   {Network};
   \node (transport1) [box, above = of net1]   {Transport};
   \node (app) [box, above = of transport1]   {Application};

   \node (phys) [box, right = of phy1] {\hspace{1cm}};
   \node (dls) [box, above = of phys]   {\hspace{1cm}};

   \node (phyr) [box, right = of phys] {\hspace{1cm}};
   \node (dlr) [box, above = of phyr]   {\hspace{1cm}};
   \node (netr) [box, above = of dlr]   {\hspace{1cm}};
   
   \node (phy2) [box, right = of phyr]                   {Phys.};
   \node (dl2) [box, above = of phy2]   {Data Link};
   \node (net2) [box, above = of dl2]   {Network};
   \node (transport2) [box, above = of net2]   {Transport};
   \node (app2) [box, above = of transport2]   {Application};
   

   
   \end{tikzpicture}



   

:cite:t:`sherry2012making` show that deployed networks contain a variety of devices besides the traditional layer-2 switches and the layer-3 routers :cite:`sherry2012making`. These middleboxes include firewalls, Network Address Translators, transparent proxies, VPN gateways, network caches, ... Each of these middleboxes processes the packets at different layers. From a reference model viewpoint, they can be depicted as shown in :numref:`fig-middlebox`.


.. _fig-middlebox:
.. tikz:: Middleboxes in the reference model
   :libs: fit, positioning
	  
   % inspired by https://newbedev.com/tikz-draw-simplified-ble-stack 	  
   \begin{tikzpicture}[
   node distance = 1mm and 0mm,
   box/.style = {draw, text width=40mm, inner sep=2mm, align=center}
   ]
		 
   \node (phy1) [box]                   {Phys.};
   \node (dl1) [box, above = of phy1]   {Data Link};
   \node (net1) [box, above = of dl1]   {Network};
   \node (transport1) [box, above = of net1]   {Transport};
   \node (app) [box, above = of transport1]   {Application};


   \node (phym) [box, right = of phy1,color=red] {};
   \node (dlm) [box, above = of phym,color=red]   {};
   \node (netm) [box, above = of dlm,color=red]   {};
   \node (transportm) [box, above = of netm,color=red]   {};
   \node (appm) [box, above = of transportm,color=red]   {};
   
   \node (phy2) [box, right = of phym]                   {Phys.};
   \node (dl2) [box, above = of phy2]   {Data Link};
   \node (net2) [box, above = of dl2]   {Network};
   \node (transport2) [box, above = of net2]   {Transport};
   \node (app2) [box, above = of transport2]   {Application};
      
   \end{tikzpicture}


A detailed review of the operation of all these middleboxes is outside the scope of this document. However, it is interesting to analyze in more details three representative middleboxes. Our first middleboxes are the firewalls. Several types of firewalls have been deployed. The simplest ones are stateless. They analyze several fields of the packets and decide, on a per-packet basis, which packets are forwarded and which packets are discarded. More advanced firewalls can track transport connections or application-level sessions and deal with out-of-order packets or retransmissions.

Stateless firewalls are often configured by network engineers with `white lists`, i.e. lists of destination addresses and ports of the services that are exposed outside the firewall. The packets that match one of these white lists are accepted while the others are rejected. These whitelists typically contain the list of the IP addresses of the public facing servers, the transport protocols they use (i.e. TCP or UDP) and the corresponding port numbers. Measurements indicate that there are unfortunately many Internet paths where other protocols than TCP, UDP and ICMP are simply blocked :cite:`barik2020usability`. DCCP seems to be more often blocked than SCTP. Many of these firewalls simply filter packets based on the IPv4 protocol field or the IPv6 Next Header information. Unfortunately, the deployment of such firewalls ossifies the Internet by making it more difficult to deploy other protocols above IP than TCP, UDP and ICMP. Concerning UDP, :cite:t:`barik2020usability` shows that UDP-Lite :cite:`rfc3828`, a small modification to UDP, is more often blocked on Internet paths than UDP. 

Stateful firewalls go one step further and maintain state for the transport-level network flows passing through them. A stateful firewall can check that an ICMP message corresponds to an existing TCP connection. When it receives a TCP packet that carries data, it checks whether the packet belongs to an active connection. Otherwise the packet is dropped. Such a firewall can also verify that TCP packets are sent in sequence. It may discard packets that are severely out-of-sequence to protect servers from packet injection attacks. Some firewalls also verify the transport-level options carried by the connection establishment and the data packets. Some of them only support a limited number of options and discard or remove the options that they considered as unknown :cite:`honda2011still`. This behaviour restricts the extensibility of transport protocols and the deployment of a new transport extension requires cooperation from three types of devices:
 - the clients
 - the servers
 - the middleboxes that are present in the client and the server's networks


:cite:t:`fukuda2011analysis` analyzes packet traces collected on the Internet and reports the slow deployment of TCP options. In 2002, the TCP selective acknowledgements :cite:`rfc2018`, standardized in 1996, were only used by 10% of the observed connections in 2001. In 2010, this number grew to 90%. Unfortunately, the timestamps and large windows extensions :cite:`rfc1323`, standardized in 1993, were only used by 60% of the connections in 2010. The main reason was that Microsoft Windows client did not implement these extensions. Nowadays, this popular TCP implementation supports large windows but still not the timestamps option.

      
Network Address Translators (NAT) :cite:`rfc3022` are widely used in home and enterprise networks to reduce the utilization of scarce public IPv4 addresses. The hosts in the home/enterprise networks use private addresses. The packets that they send to the public Internet pass through a NAT that translates their IP addresses and ports. A NAT maps private addresses to one or more public IP addresses. Some NATs map each internal IP address to a public address. In this case, the NAT simply needs to change the source and destination addresses fields of the IP packets that it forwards. Note that for TCP and UDP it also needs to update the transport layer checksum since its computation also includes the source and destination IP addresses. Most NATs map multiple private addresses on a public one. In this case, they also need to change port numbers in the transport header. Some protocols such as the file transfer protocol (FTP) :cite:`rfc959` encode IP addresses in the application messages. To support such application layer protocols, NAT must include Application Level Gateways (ALGs) that translate these application messages. To perform this translation, these ALGs need to change, add or remove bytes in the transport bytestream. 


Measurement studies performed in 2010 :cite:`hatonen2010experimental` showed that some deployed NATs do not support all standardized transport protocols and their recent extensions. Unfortunately, recent measurements :cite:`barik2020usability` confirm that today's NATs still limit the deployment of new transport protocols and the extensibility of widely deployed protocols. Many of these problems were anticipated by the IETF :cite:`rfc3027`.

Another important class of middleboxes are the load-balancers. Several types of load-balancers exist. For this section, we focus on a simple load-balancer that is placed in front of a group of servers as illustrated in :numref:`fig-load-balancer`. The simplest design is a load-balancer that receives all packets from clients and servers. When a connection attempt arrives, the load-balancer selects one server (e.g. the less loaded one) and then forwards the packet and all the other packets of the connection to this specific server. If all packets exchanged by the client and the servers pass through the load-balancer, it could become a bottleneck. Some designs allow the servers to send back their replies directly to the client without passing through the load-balancers. With other designs, it becomes possible for the load-balancer to only see the first packets of each connection. With such designs, most of the packets exchanged by the clients and the servers bypass the load-balancer. We will discuss how multipath protocols enable some of these designs later in this document.


.. _fig-load-balancer:
.. tikz:: Load-balancers

   todo	  

Surprisingly, the high-speed network adapters used mainly on servers, but also on some laptops, can also interfere with the transport protocols. Network adapters are more efficient when sending large than small packets. The main reason is that there is a fixed cost for the operating system to prepare the transmission of a packet. This cost is rouglhy independent of the size of the packet that needs to be transferred. On the other hand, given network constraints with IPv4 :cite:`kent1995fragmentation` and IPv6 :cite:`rfc8900`, hosts only send network packets that fit in Ethernet's MTU size, i.e. 1500 bytes. To efficiently support such small packet size, high performance network adapters implement Segmentation Offload and Receive Offload. There are variants of these techniques that are specific to protocols such as TCP and UDP. TCP Segmentation Offload :cite:`freimuth2005server` is widely used and can be described as follows. To encourage the TCP stack to use large packets, the network adapter exposes a large MTU, e.g. 16 KBytes. When the TCP stack passes a 16 KBytes packet containing a TCP segment, the adapter automatically segments it in packets that are not longer than 1500 bytes. To perform this segmentation, the adapter creates the IP and TCP headers that are required for each 1500 Bytes packet with the correct sequence numbers. It copies other fields such as the receive window and also the TCP options :cite:`honda2011still`. The adapter also computes the checksums required by each packet. The receiver side performs the opposite and gathers several 1500 bytes packets in a larger one that is passed to the TCP stack. Without these optimizations, servers would not be able to reach throughputs of multiple tens or Gbps that are achievable today.

.. todo:: figure example TSO ?

Our last middlebox is the transparent proxy. Transparent proxies are deployed in enterprise or mobile networks for security or performance reasons. Some enterprise networks use transparent proxies on their firewalls to observe all the data exchanged over transport connections and detect any attack or leak of information. Some mobile network providers have deployed transparent proxies to improve the performance of transport protocols in the wireless network compared to the classical client stacks :cite:`zullo2019hic`. 

.. _fig-transparent-proxy:
.. tikz:: Transparent proxies in the reference mode

   \begin{tikzpicture}[	  
   node distance = 1mm and 0mm,
   box/.style = {draw, text width=40mm, inner sep=2mm, align=center}
   ]
		 
   \node (phy1) [box]                   {Phys.};
   \node (dl1) [box, above = of phy1]   {Data Link};
   \node (net1) [box, above = of dl1]   {Network};
   \node (transport1) [box, above = of net1]   {Transport};
   \node (app) [box, above = of transport1]   {Application};


   \node (phym) [box, right = of phy1,color=red] {};
   \node (dlm) [box, above = of phym,color=red]   {};
   \node (netm) [box, above = of dlm,color=red]   {};
   \node (transportm) [box, above = of netm,color=red]   {};
   \node (appm) [box, above = of transportm,color=red]   {};
   
   \node (phy2) [box, right = of phym]                   {Phys.};
   \node (dl2) [box, above = of phy2]   {Data Link};
   \node (net2) [box, above = of dl2]   {Network};
   \node (transport2) [box, above = of net2]   {Transport};
   \node (app2) [box, above = of transport2]   {Application};


   
   \end{tikzpicture}


Transparent proxies usually support TCP. With a transparent proxy, TCP is not anymore an end-to-end protocol. It becomes and end-proxy-end protocol. When a client initiates a TCP connection, the ``SYN`` packet is intercepted by the proxy that transparently terminates the connection. There is one connection between the client and the proxy. The proxy then initiates a connection towards the server. All the data sent by the client is carried over the first connection and then sent over the second one towards the server.


From the application's viewpoint, the connection continues to carry one bytestream in each direction. However, from a TCP viewpoint, this is different. If the client negotiates TCP extensions on the connection with the proxy, there is no guarantee that the proxy will negotiate the same extensions with the server. Furthermore, an extension supported by both the client and the server will only be used independently over the two proxied connections provided that the proxy also supports the extension. If we observe the TCP packets sent by the client and received by the server, we will extract the same bytestream. However, it is unlikely that the sequence and acknowledgement numbers will be preserved when they reach the server. Furthermore, the size of some packets might change as well as proxies can fragment and reassemble data.
Measurement studies have analyzed the deployed proxies in more details :cite:`xu2015investigating,honda2011still,zullo2019hic`. 
   
Although middleboxes are usually designed to improve network performance or provide additional services, they often interfere with transport protocols in various ways. Transport protocols such as TCP were designed according to the end-to-end principle :cite:`saltzer1984end`. When a client and a server are logically associated with a transport connection, they both maintain some state. In the early days, some of the information found in the client's state (e.g. the IP addresses and port numbers or the sequence and acknowledgement numbers) was also contained in the server's state. The protocol ensured that these states remained synchronized during the entire connection. Unfortunately, with middleboxes, this assumption is not valid anymore. For a protocol such as TCP, middleboxes preserve the bytestream [#fbytestream]_ ., but some middleboxes may interfere with all the fields of the packet headers and thus the connection's state. This has a profound impact on the deployment of extensions to transport protocols in the Internet :cite:`honda2011still`.


Representing Packets
====================


How to describe packets ? classical packet notation or QUIC notation ?


Transport protocols exchange control information and data produced by the applications that use them. Protocols such as UDP, DCCP and TCP use simple packet formats that are composed of two parts:

 - a (usually variable) length header carrying the control information such as port numbers, sequence numbers, acknowledgements, windows, ...
 - a variable length payload carrying the data supplied by the application


The specifications for these protocols usually represents the different types of packets that they exchange using ASCII art. For example the format of the TCP header is usually described as shown in :numref:`fig-tcp-header`.

.. _fig-tcp-header:
.. code-block:: console
   :caption: Graphical representation of the TCP header
	     
    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Data |           |U|A|P|R|S|F|                               |
   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
   |       |           |G|K|H|T|N|N|                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Checksum            |         Urgent Pointer        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+



This representation works well for protocols like TCP or UDP, but becomes cumbersome for security protocols such as TLS. More recent protocols such as QUIC have opted for a textual representation of the format of a packet.   

.. _fig-tcp-header-text:
.. code-block:: console
   :caption: Textual representation of the TCP header 

   TCP Header {
     Source Port (16),
     Destination Port (16),
     Sequence Number (32),
     Acknowledgment Number (32),
     Data Offset (4),
     Reserved (6),
     URG (1),
     ACK (1),
     PSH (1),
     RST (1),
     SYN (1),
     FIN (1),
     Window (16),
     Checksum (16),
     Urgent Pointer (16)
   }


.. rubric:: Footnotes

.. [#fbytestream] There are middleboxes that modify the bytestream, e.g. the Application Level Gateways used by NATs or some transparent web proxies.

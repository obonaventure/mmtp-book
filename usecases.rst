Use cases
*********


.. todo:: Explain the main use cases for Multipath TCP and why it brings benefits

Before looking at how Multipath TCP works in details, it is interesting to first analyze the different use cases where Multipath TCP is used. Some of these use cases have motivated the design of Multipath TCP. Others appeared after the design was complete. Other uses cases will likely appear in the coming years.

As explained in the previous section, with Multipath TCP, hosts can exchanged data over different paths. At a high level, a Multipath TCP implementation lies between an application that uses the socket layer to exchange data over a connection. With TCP, a client establishes a connection with a server. It then uses it to send and receive data reliably thanks to the retransmission, flow and congestion control mechanisms that are included inside TCP. This TCP connection is identified by using four fields that are present in each packet exchanged over the connection:
 - client IP address
 - server IP address
 - client TCP port
 - server TCP port

All packets contain these four fields that are often called the four-tuple. 
   
At a high-level, the main difference between TCP and Multipath TCP is that a Multipath TCP connection is in fact a group of one or more TCP connections. These different TCP connections are entirely managed by Multipath TCP and are transparent to the application. The application interacts through the socket layer as if there was a single underlying TCP connection. Multipath TCP manages the underlying TCP connections. More precisely, Multipath TCP includes two different algorithms to control the underlying connections:

 - a path manager that decides when an underlying TCP connection should be created or terminated
 - a packet scheduler that decides over which underlying connection each new data is transmitted

The path manager and the packet scheduler play a key role in each use case as we will see shortly. To illustrate them, let us consider a very simple an naive application that runs on a dual-stack client and interacts with a dual-stack server. There are two "paths" that the client and the server can use to exchange data : IPv4 and IPv6. Although both the client and the server are attached using a single link to the network, their end-to-end paths might differ through the network and pass through different intermediate routers.

When web browsers run on dual-stack hosts, they usually rely on the Happy Eyeballs mechanism to select between IPv6 and IPv4. In a nutshell, they typically try first to initiate a TCP connection to the server using IPv6. If after some time, e.g. 50 msec, the connection is not established, the client also tries using IPv4. In the end, the first connection to be established is selected and used to exchanged data.

Multipath TCP would also use Happy Eyeballs, but once one connection has been established, say IPv6, the client and the server will exchange their IPv4 addresses over the Multipath TCP connection. A simple path manager running on the client would then establish a second TCP connection using IPv4. This new TCP connection will be part of the Multipath TCP connection that was established over IPv6. The client and the server can now use two different TCP connections to exchange data: a first connection that uses IPv6 and a second connection that uses IPv4. If these connections have similar performance, a simple packet scheduler such as round-robin can be used to distribute the data over them. Such a scheduler alternatively sends data over the IPv4 and the IPv6 connections.

.. todo: extension is robust establishment, to be discussed later

.. todo:: include figure MPTCP architecture

	  
	  

.. todo:: simplified and high level model, we have two or more underlying tcp connections that use different paths and we used them to meet specific application needs	  

Improving resilience
====================

.. todo:: Apple, but also the use case from irland with different providers

.. todo:: for apple: automatic failover from Wi-Fi to cellular or the opposite with simple examples and use cases


.. todo:: irland, explain the firemen in a truck and multiple cellular connections for coverage
   
	  
Improving quality of experience
===============================

.. todo:: Apple and the automatic switch from wifi to cellular when wifi fails

	  


	  

Improving bandwidth
===================

.. todo:: Tessares and ATSSS, GigaLTE with SOCKS


.. todo:: datacenter with sigcomm

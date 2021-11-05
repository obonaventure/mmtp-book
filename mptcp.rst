Multipath TCP
*************


.. todo:: all the nitty details behind MPTCP

.. todo:: focus on mptcp version 1 and briefly explain version 0

Multipath TCP :cite:`rfc793` is an extension to the TCP protocol :cite:p:`rfc793` that was presented earlier. We start with an overview of Multipath TCP. Then we explain how a Multipath TCP connection can be established. Then we analyze how data is exchanged over different paths and explain the multipath congestion control schemes. Finally, we explain how Multipath TCP connections can be terminated.



An overview of Multipath TCP
============================



 

Connection establishment
========================

A Multipath TCP connection starts with a three-way handshake like a regular TCP connection. To indicate that it wishes to uze Multipath TCP, the client adds the ``MP_CAPABLE`` option to the ``SYN`` segment. In the ``SYN`` segment, this option only contains some flags and occupies 4 bytes. The server replies with a ``SYN+ACK`` segment than contains an ``MP_CAPABLE`` option including a server generated 64 bits random key that will be used to authenticate connections over different paths. The client concludes the handshake by sending an ``MP_CAPABLE`` option in the ``ACK`` segment containing the random keys chosen by the client and the server.

.. _fig-tcp-handshake-mptcp:
.. tikz:: Negotiating the utilization of Multipath TCP during the three-way handshake
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=6; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MPC[flags]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MPC[flags,$Server_{key}$]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}\\\small{MPC[flags,$Client_{key}$,$Server_{key}$]}};


.. note:: Multipath TCP version 0
   
   The first version of Multipath TCP used a slightly different handshake :cite:p:`rfc6824`. The ``MP_CAPABLE`` option sent by the client contains the 64 bits key chosen by the client. The ``SYN+ACK`` segment contains an ``MP_CAPABLE`` option with 64 bits key chosen by the server. The client echoes the client and server keys in the third ``ACK`` of the handshake. 

          
   .. _fig-tcp-handshake-mptcp-v0:
   .. tikz:: Negotiating the utilization of Multipath TCP version 0
      :libs: positioning, matrix, arrows, math

      \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=6; }
   
      \tikzstyle{arrow} = [thick,->,>=stealth]
      \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
      \node [black, fill=white] at (\c1,\max) {Client};
      \node [black, fill=white] at (\s1,\max) {Server};
   
      \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
      \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
      \tikzmath{\y=\max-1;}
   
      \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MPC[flags,$Client_{key}$]}};
      \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MPC[flags,$Server_{key}$]}};
      \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}\\\small{MPC[flags,$Client_{key}$,$Server_{key}$]}};


The 64 bits random keys chosen by the client and the server play three different roles in Multipath TCP. Their first role is to identify the Multipath TCP connection to which an additional connection must be attached. Since a Multipath TCP connection can combine several TCP connections, Multipath TCP cannot use the IP addresses and port numbers to identify a TCP connection. Multipath TCP uses a specific identifier that is called a token. For technical reasons, this token is derived from the 64 bits key as the most significant 32 bits of the SHA-256 :cite:p:`rfc6234` hash of the key. The second role of the 64 bits keys is to authenticate the establishment of additional connections as we will see shortly. Finally, the keys are also used to compute random initial sequence numbers.

The main benefit of Multipath TCP is that a Multipath TCP connection can combine different TCP connections that potentially use different paths. Starting from now on, we will consider a client with two network interfaces and a server with one network interface. This could for example correspond to a client application running on a smartphone that interacts with a server. We explore more complex scenarios later.

.. In the figures below, the blue arrows correspond to the segments sent over the first interface while the red arrows represent the segments sent over the second interface. In practice, these "interfaces" do not need to be physical interfaces. For example, the red arrows could correspond to IPv6 while the blue arrows correspond to IPv4.

We can know how a Multipath TCP connection can combine different TCP connections. According to the Multipath TCP specification, these connections are called subflows :cite:p:`rfc8684`. We also adopt this terminology in this document. :numref:`fig-mptcp-join` shows a Multipath TCP that combines two subflows. To establish the Multipath TCP connection, the client initiates the initial subflow by using the ``MP_CAPABLE`` option during the three-way handshake. At the end of the initial handshake, the client and the server have exchanged their keys. Based on their keys, they have both computed the token that the remote host uses to identify the Multipath TCP connection.

To attach a second subflow to this Multipath TCP connection, the client needs to create it. For this, it starts a three-way handshake with the server by sending a ``SYN`` segment containing the ``MP_JOIN`` option. This option indicates that the client uses Multipath TCP and wishes to attach this new connection to an existing Multipath TCP connection. The ``MP_JOIN`` option contains two important fields:

 - the token that the server uses to identify the Multipath TCP connection
 - a random nonce

The client has derived the token from the key announced by the server in the ``MP_CAPABLE`` option of the ``SYN+ACK`` segment on the initial subflow. Thanks to this token, the server knows to which Multipath TCP connection the new subflow needs to be attached.

.. todo:: discuss security concerns

The server uses the random nonce sent by the client and its own random nonce to prove its knowledge of the keys exchanged during the initial handshake. The server computes :math:`HMAC(Key=(Server_{key}||Client_{key}), Msg=(nonce_{Server}||nonce_{Client}))`, where ``||`` denotes the concatenation operation. It then returns the high order 64 bits of this HMAC in the ``MP_JOIN`` option of the ``SYN+ACK`` segment together with its 32 bits nonce. The client computes :math:`HMAC(Key=(Client_{key}||Server_{key}), Msg=(nonce_{Client}||nonce_{Server}))` and sends the 160 bits HMAC in the ``ACK`` segment. 
         


   

.. _fig-mptcp-join:
.. tikz::
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=8; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \draw[red,very thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MPC[flags]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MPC[flags,$S_{key}$]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}\\\small{MPC[flags,$C_{key}$,$S_{key}$]}};

   
   \tikzmath{\y=\max-4.5;}
   
   \draw[red,thick, ->] (\c2,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MP\_JOIN[$S_{token}$,$nonce_{C}$]}};
   \draw[red,thick, ->] (\s1,\y-1) -- (\c2,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MP\_JOIN[$HMAC_{S}$,$nonce_{S}$]}};
   \draw[red,thick, ->] (\c2,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}\\\small{MP\_JOIN[$HMAC_{C}$]}};
 
.. note:: Generating random keys

   Voir papier NSDI       
   
Data transfert
==============
	  
Congestion control
==================

.. todo:: explain basic idea and the problem of having 

.. Why we need coupled congestion control
	  
LIA
---

OLIA
----

BALIA
-----

MPCC
----


Connection release
==================

	  
Coping with middlebox interference
==================================

	  
.. todo: classify the different types of middleboxes and their impact

   

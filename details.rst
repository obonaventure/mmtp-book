The Multipath TCP protocol in details
*************************************


.. todo:: all the nitty details behind MPTCP

.. todo:: focus on mptcp version 1 and briefly explain version 0

Multipath TCP is an extension to the TCP protocol :cite:p:`rfc8684`. Before looking at Multipath TCP is details, it is important to understand the basics of TCP. The reader who already knows TCP can skip this section.


TCP is a connection-oriented transport protocol. This means that a TCP connection must be established before communicating hosts can exchange data. A connection is a logical relation between the two communication hosts. Each hosts maintains some state about the connection and uses it to manage the connection.


TCP uses the three-way handshake as shown in :numref:`fig-tcp-handshake`. To initiate a connection, the client sends a TCP segment with the ``SYN`` flag set. Such a segment is usually called a ``SYN`` segment. It contains a random sequence number (`x` in :numref:`fig-tcp-handshake`). If the server accepts the connection, it replies with a ``SYN+ACK`` segment whose ``SYN`` and ``ACK`` flags are set. The acknowledgement number of this segment is set to ``x+1`` to confirm the reception of the ``SYN`` segment sent by the client. The server selects a random sequence number (`y` in :numref:`fig-tcp-handshake`). Finally, the client replies with an `ACK` segment that acknowledges the reception of the ``SYN+ACK`` segment. 

.. _fig-tcp-handshake:
.. tikz:: Establishing a TCP connection using the three-way handshake
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=5; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {SYN\small{[seq=x]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}};
   \draw[blue,thick, ->] (\c1,\y-2) -- (\s1,\y-3) node [midway, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};


TCP was designed to be extensible. The TCP header contains a TCP Header Length (THL) field that indicates the total length of the TCP header in four-bytes words. For the normal header, this field is set to 5, which corresponds to the 20 bytes long TCP header. Larger values of the THL field indicate that the segment contains one or more TCP options. TCP options are encoded as a Type-Length-Value field. The first byte specifies the Type, the second byte indicates the length of the entire TCP option in bytes. The utilization of TCP options is usually negotiated during the three-way-exchange. The client adds a TCP option in the ``SYN`` segment. If the server does not recognize the option, it simply ignores it. If the server wants to utilize the extension for the connection, it simply adds the corresponding option in the ``SYN+ACK`` segment. This is illustrated in :numref:`fig-tcp-handshake-sack` with the Selective Acknowledgments extension :cite:p:`rfc2018` as an example.

.. _fig-tcp-handshake-sack:
.. tikz:: Negotiating the utilization of Selective Acknowledgements during the three-way handshake
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=4.5; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{SACK-Permitted}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{SACK-Permitted}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};

A TCP connection is identified by using four fields that are included inside each TCP packet:
 - the client IP address
 - the server IP address
 - the client-selected port
 - the server port

All TCP packets that belong to a connection contain these four fields in the IP and TCP header. When a host receives a packet, it uses them to match the connection to which it belongs. A TCP implementation maintains some state for each established TCP connection. This state is a data structure that contains fields which can vary from one implementation to another. The TCP specification defines some state variables that any implementation should remember. On the sender side, these include:
 - ``snd.una``, the oldest unacknowledged sequence number
 - ``snd.nxt``, the next sequence number of be sent
 - ``rcv.win``, the latest window advertised by the remote host

A TCP sender also stores the data that has been sent but has not yet been acknowledged. It also measures the round-trip-time and its variability to set the retransmission timer and maintains several variables that are related to the congestion control scheme.

A TCP receiver also maintains state variables. These include ``rcv.next``, the next expected sequence number. Data received in sequence can be delivered to the application while out-of-sequence data must be queued.

Finally, TCP implementations store the state of the connection according to the TCP state machine :cite:p:`rfc0793`.

TCP implementations include lots of optimizations that are outside the scope of this brief introduction. Let us know briefly describe how TCP sends data reliably. Consider a TCP connection established between a client and a server. :numref:`fig-tcp-simple-data` shows a simple data transfert between these two hosts. The sequence number of the first segment starts at ``1234``, the current value of ``snd.nxt``. For TCP, each transmitted byte consumes one sequence number. Thus, after having sent the first segment, the client's ``snd.nxt`` is set to ``1238``.  The server receives the data in sequence and immediately acknowledges it. A TCP receiver always sets the acknowledgement number of the segments that it sends with the next expected sequence number, i.e. ``rcv.nxt``. 


.. _fig-tcp-simple-data:
.. tikz:: TCP Reliable data transfert
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=4; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   %\node [black, fill=white] at (\c1,\max) {Client};
   %\node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {\small{[seq=1234,data="abcd"]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {ACK\small{[ack=1237]}};
   \draw[blue,thick, ->] (\c1,\y-1) -- (\s1,\y-2) node [midway, align=left, fill=white] {\small{[seq=1238,data="efgh"]}};
   \draw[blue,thick, ->] (\s1,\y-2) -- (\c1,\y-3) node [midway, align=left, fill=white] {ACK\small{[ack=1224]}};


In practice, TCP implementations use the Nagle algorithm :cite:p:`rfc896` and thus usually try to send full segments. They use the Maximum Segment Size (MSS) option during the handshake and PathMTU discovery the determine the largest segment which can be safely sent over a connection. Furthermore, TCP implementations usually delay acknowledgements and only acknowledge every second segment when these are received in sequence. This is illustrated in :numref:`fig-tcp-data-delack`.


.. _fig-tcp-data-delack:
.. tikz:: TCP Reliable data transfert with delayed acknowledgements.
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=5.0; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   %\node [black, fill=white] at (\c1,\max) {Client};
   %\node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {\small{[seq=1000,len=1460,data="x...x"]}};
   \draw[blue,thick, ->] (\c1,\y-0.5) -- (\s1,\y-1.5) node [midway, align=left, fill=white] {\small{[seq=2460,len=1460,data="x...x"]}};
   \draw[blue,thick, ->] (\s1,\y-1.6) -- (\c1,\y-2.6) node [midway, align=left, fill=white] {ACK\small{[ack=3920]}};


TCP uses a single segment type and each segment contains both a sequence number and an acknowledgement number. The sequence number is mainly useful when a segment contains data. A receiver only processes the acknowledgment number if the ``ACK`` flag is set. In practice, TCP uses cumulative acknowledgements and all the segments sent on a TCP connection have their ``ACK`` flag set. The only exception is the ``SYN`` segment sent by the client to initiate a connection.


.. _fig-tcp-piggyback:
.. tikz:: TCP piggybacking.
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=5.0; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }

   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {ACK\small{[seq=1234,ack=5678,len=4,data="abcd"]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, fill=white] {ACK\small{[seq=5678,ack=1238,len=2,data="ef"]}};
   \draw[blue,thick, ->] (\c1,\y-2) -- (\s1,\y-3) node [midway, fill=white] {ACK\small{[seq=1238,ack=5680,len=4,data="ghij"]}};
   
   
TCP uses different techniques to retransmit errored or lost data. The TCP header contains a 16 bits checksum that is computed over the entire TCP segment and a part of the IP header. The value of this checksum is computed by the sender and checked by the receiver to detect transmission errors. TCP copes with these errors by retransmitting data. The simplest technique is to rely on a retransmission timer. TCP continuously measure the round-trip-time, i.e. the delay between the transmission of a segment and the reception of the corresponding acknowledgment. It then sets a per-connection retransmission timer based on its estimations of the mean rtt and its variance :cite:p:`rfc6298`. This is illustrated in :numref:`fig-tcp-retrans` where the arrow terminated with red cross corresponds to a lost segment. Upon expiration of the retransmission timer, the client retransmits the unacknowledged segment. 

.. _fig-tcp-retrans:
.. tikz:: TCP protects data by a retransmission timer
   :libs: positioning, matrix, arrows, math, arrows.meta

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=7; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   %\node [black, fill=white] at (\c1,\max) {Client};
   %\node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick,-{Rays[color=red]}] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {ACK\small{[seq=1234,ack=5678,len=4,data="abcd"]}};
   \draw[black,thick,<->]  (\c1-0.5,\y) -- (\c1-0.5,\y-3) node [midway, fill=white] {retransmission timer};
   \draw[blue,thick, ->] (\c1,\y-3) -- (\s1,\y-4) node [midway, fill=white]  {ACK\small{[seq=1234,ack=5678,len=4,data="abcd"]}};
   \draw[blue,thick, ->] (\s1,\y-4.1) -- (\c1,\y-5) node [midway, fill=white] {ACK\small{[seq=5678,ack=1238]}};

For performance reasons, TCP implementations try to avoid relying on the retransmission timer to retransmit the lost segments. Modern TCP implementations use selective acknowledgements which can be negotiated during the handshake. This is illustrated in :numref:`fig-tcp-retrans-sack`. A selective acknowledgement reports blocks of sequence number that have been received correctly by the receiver. Upon reception of the ``SACK`` option, the sender knows that sequence numbers ``1234-1237`` have not been received while sequence numbers ``1238-1250`` have been correctly received.

.. _fig-tcp-retrans-sack:
.. tikz:: TCP leverages selective acknowledgements to retransmit lost data
   :libs: positioning, matrix, arrows, math, arrows.meta

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=8; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }

   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick,-{Rays[color=red]}] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {\small{[seq=1234,ack=5678,data="abcd"]}};
   \draw[blue,thick, ->] (\c1,\y-1) -- (\s1,\y-2) node [midway, fill=white]  {\small{[seq=1234,data="efgh"]}};
   \draw[blue,thick, ->] (\c1,\y-2) -- (\s1,\y-3) node [midway, fill=white]  {\small{[seq=1238,data="ijkl"]}};
    \draw[blue,thick, ->] (\c1,\y-2) -- (\s1,\y-3) node [midway, fill=white]  {\small{[seq=1242,data="mnop"]}};  
   \draw[blue,thick, ->] (\c1,\y-3) -- (\s1,\y-4) node [midway, fill=white]  {\small{[seq=1246,data="qrst"]}};
   \draw[blue,thick, ->] (\s1,\y-4.1) -- (\c1,\y-5) node [midway, fill=white] {ACK\small{[ack=1234]}SACK[1238:1250]};
   \draw[blue,thick, ->] (\c1,\y-5.1) -- (\s1,\y-6) node [midway, fill=white]  {\small{[seq=1234,ack=5678,data="abcd"]}};

When the client and the sender have exchanged all the required data, they can terminate the connection. TCP supports two different methods to terminate a connection. The reliable manner is that each host closes its direction of data transfer by sending a segment with the ``FIN`` flag set. The sequence number of this segment marks the end of the data transfer and the recipient of the segment acknowledges it once it has delivered all the data up to the sequence number of the ``FIN`` segment to its application. The release of a TCP connection is illustrated in :numref:`fig-tcp-fin`. To reduce the size of the figure, we have set the ``FIN`` flag in segments that contains data. The server considers the connection to be closed upon reception of the ``FIN+ACK`` segment. It discards the state that it maintained for this now closed TCP connection. The client also considers the connection to be closed when it sends the ``FIN+ACK`` segment since all data has been acknowledged. However, it does not immediately discard the state for this connection because it needs to be able to retransmit the ``FIN+ACK`` segment in case it did not reach the server.

.. _fig-tcp-fin:
.. tikz:: Closing a TCP connection using the ``FIN`` flag
   :libs: positioning, matrix, arrows, math, arrows.meta

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=6; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }

   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick,->] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {FIN\small{[seq=1234,data="abcd"]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, fill=white]  {ACK \small{[ack=1239]}};

   \draw[blue,thick, ->] (\s1,\y-3) -- (\c1,\y-4) node [midway, fill=white]  {FIN\small{[seq=5678,date="xyz"]}};
   \draw[blue,thick,->] (\c1,\y-4) -- (\s1,\y-5) node [midway, fill=white] {FIN+ACK\small{[seq=1239,ack=5681]}};


   
.. _fig-tcp-rst:
.. tikz:: Closing a TCP connection using a ``RST`` segment
   :libs: positioning, matrix, arrows, math, arrows.meta

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=4; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }

   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick,->] (\c1,\y) -- (\s1,\y-1) node [midway, fill=white] {\small{[seq=1234,data="abcd"]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, fill=white]  {RST\small{[ack=1239]}};

 

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

   

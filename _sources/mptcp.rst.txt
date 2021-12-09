Multipath TCP
*************


.. todo:: all the  details behind MPTCP

.. todo:: focus on MPTCP version 1 and briefly explain version 0

Multipath TCP :cite:`rfc8684` is an extension to the TCP protocol :cite:p:`rfc793` that was presented earlier. We start with an overview of Multipath TCP. Then we explain how a Multipath TCP connection can be established. Then we analyze how data is exchanged over different paths and explain the multipath congestion control schemes. Finally, we explain how Multipath TCP connections can be terminated.



A brief overview of Multipath TCP
=================================

The main design objective for Multipath TCP :cite:`rfc6824` was to enable hosts to exchange the packets that belong to a single TCP connection over different network paths. Several definitions are possible for a network path. Considering a TCP connection between a client and a server, a network path can be defined as the succession of the links and routers that create a path between the client and the server. For example, in :numref:`fig-simple-network`, there are many paths between the client host `C` and the server `S`, e.g. :math:`C \rightarrow R1 \rightarrow R2 \rightarrow R4 \rightarrow S` and :math:`C \rightarrow R1 \rightarrow R3 \rightarrow R4 \rightarrow S`, but also :math:`C \rightarrow R1 \rightarrow R3 \rightarrow R5 \rightarrow R4 \rightarrow S` or even :math:`C \rightarrow R1 \rightarrow R2 \rightarrow R4 \rightarrow R3 \rightarrow R5 \rightarrow R4 \rightarrow S`.   

.. _fig-simple-network:
.. tikz:: A simple network
   :libs: positioning, matrix, arrows, math

   \tikzset{router/.style = {rectangle, draw, text centered, minimum height=2em}, }
   \tikzset{host/.style = {circle, draw, text centered, minimum height=2em}, }
   \node[host] (A) {C};
   \node[router, right of=A] (R1) {R1};
   \node[router, right=of R1] (R3) {R3};
   \node[router, right=of R3] (R5) {R5};
   \node[router, below=of R1] (R2) {R2};
   \node[router, below=of R3] (R4) {R4};
   \node[host, right of=R4] (C) {S};

   \path[draw,thick]
   (A) edge (R1)
   (R1) edge (R2)
   (R3) edge (R1)
   (R2) edge (R4)
   (R4) edge (R3)
   (R4) edge (R5)
   (R3) edge (R5)
   (R4) edge (C);


During the first discussions on Multipath TCP within the IETF, there was a debate on the types of paths that Multipath TCP could use in IP networks. Although networks provide a wide range of paths between a source and a destination, it is not necessarily simple to use all these paths in a pure IP network. Looking a :numref:`fig-simple-network` and assuming that all links have the same IGP weigth, packets sent by `C` will follow one of the two shortest paths, i.e. :math:`C \rightarrow R1 \rightarrow R2 \rightarrow R4 \rightarrow S` or :math:`C \rightarrow R1 \rightarrow R3 \rightarrow R4 \rightarrow S`. Since routers usually use hash-hased load-balancing :cite:`rfc2992` to distribute packets over equal cost paths, all the packets from a given connection will follow either the first or the second shortest path. In most networks, the path followed by a TCP connection will only change if there are link or router failures on this particular path.

When Multipath TCP was designed, the IETF did not want to design techniques to enable the transport layer to specify the paths that packets should follow. They opted for a very conservative definition of the paths that Multipath TCP can use :cite:`rfc6182`. Multipath TCP assumes that the endpoints of a TCP connection are identified by their IP addresses. If two hosts want to exchange packets over different paths, then at least one of them must have two or more IP addresses. This covers two very important use cases:

 - mobile devices like the smartphones that have a cellular and a Wi-Fi network interface each identified by its own IP address
 - dual-stack hosts that have both an IPv4 and an IPv6 address


In this document, we will often use smartphones to illustrate Multipath TCP client hosts. This corresponds to a widely deployed use case that simplifies many of the examples, but is not the only possible deployment.


.. note:: Using non-equal cost paths with Multipath TCP
	  
   When Multipath TCP was designed, there was no standardized solution that enabled a host to control the path followed by its packets inside a network. This is slowly changing. First, the IETF has adopted the Segment Routing architecture :cite:`rfc8402`. This architecture is a modern version of source routing which can be used in MPLS and IPv6 networks. In particular, using the IPv6 Segment Routing Header :cite:`rfc8754`, a host can decide the path that its packets will follow inside the network. This opens new possibilities for Multipath TCP. Some of these possibilities are explored by the Path Aware Networking Research Group of the Internet Research Task Force.

A second important design question for the Multipath TCP designers was how use two or more paths for a single connection ? As an example, let us consider a smartphone that interacts with a server. This smartphone has two different IP addresses: one over its Wi-Fi interface and one over its cellular interface. Assume that the smartphone initiates a TCP connection over its Wi-Fi interface. This handhsake is illustrated in blue in :numref:`fig-mptcp-naive`. It sends a data packet over this interface and the next one over the cellular one (shown in red). 

.. _fig-mptcp-naive:
.. tikz:: A naive approach to create a Multipath TCP connection 
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=7; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};
   \draw[blue,thick, ->] (\c1,\y-3) -- (\s1,\y-4) node [midway, align=left, fill=white] {Data\small{[seq=x+1]}};
   \draw[red,thick, ->] (\c2,\y-4) -- (\s1,\y-5) node [midway, align=left, fill=white] {Data\small{[seq=x+2]}};
   



This utilization of the two paths between the smartphone and the server pose two different problems. First, the server must be able to accept the packet sent by the smarphone, that uses another source IP address than the address used during the handshake and associate it with an existing Multipath TCP connection. If the server blindingly accept this packet from another address than the one used during the handshake, then there are two main security risks. An attacker could inject a packet inside an existing connection. Furthermore, he could cause a denial of service attack by sending a spoofed packet in an existing connection that requests the server to send a large volume of data to the spoofed address. Second, a middlebox such as a firewall on the cellular path between the smartphone and the server could block the packet because it does not belong to a TCP connection created on the cellular path.


To cope with this problem, the Multipath TCP designers opted for an architecture where a Multipath TCP connection combines several TCP connections that are called subflows over the different paths. A Multipath TCP connection starts with a three-way handshake like a regular TCP connection. A client that wishes to use Multipath TCP sends a ``SYN`` with the ``MP_CAPABLE`` option to negotiate a Multipath TCP connection with a server. If the server replies with the same option, the handshake succeeds and creates the first subflow belonging to this Multipath TCP connection. The client and the server can send data over this connection as over any TCP connection. To use a second path, the client (or the server), must initiate another TCP handshake over the new path. The ``SYN`` sent over this second path uses the ``MP_JOIN`` option to indicate that this is an additional subflow that must be linked to an existing Multipath TCP connection. This is illustrated in :numref:`fig-mptcp-capable-join`.
   

.. _fig-mptcp-capable-join:
.. tikz:: A Multipath TCP connection with two subflows
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=10; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {SYN\small{[seq=x]}\\\small{MP\_Capable}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MP\_Capable}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=center, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};
   \draw[blue,thick, ->] (\c1,\y-3) -- (\s1,\y-4) node [midway, align=center, fill=white] {Data\small{[seq=x+1]}};
   \draw[red,thick, ->] (\c2,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {SYN\small{[seq=p]}\\\small{MP\_Join}};
   \draw[red,thick, ->] (\s1,\y-5) -- (\c2,\y-6) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=q,ack=p+1]}\\\small{MP\_Join}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {ACK\small{[seq=p+1,ack=q+1]}};
   \draw[red,thick, ->] (\c2,\y-7) -- (\s1,\y-8) node [midway, align=center, fill=white] {Data\small{[seq=p+1]}};   


These two three-way handshakes create two TCP connections called subflows in the Multipath TCP terminology. It is interesting to analyze how these two connections are identified on the server. A host identifies a TCP connection using four identifiers that are present in all the packets of this connection:

 - the local IP address
 - the remote IP address
 - the local port
 - the remote port

Assume that the client uses IP address :math:`IP_{\alpha}` on its Wi-Fi intefance and :math:`IP_{\beta}` on its cellular interface and that :math:`p` is the port used by the server. If the client used port :math:`p_1` to create the initial subflows, then the identifier of this subflow on the server is :math:`<IP_{S},IP_{\alpha},p,p_{1}>`. Similarly, the second subflow is identified by the :math:`<IP_{S},IP_{\beta},p,p_{2}>` tuple on the server. Note that these two connection identifiers differ by at least one IP address as specified in :cite:`rfc6182`.

A server usually manages a large number of simulatenous connections. When it receives the ``SYN`` for the second subflow, it must be able to link this new subflow with the corresponding Multipath TCP connection. For this, the client must include an identifier of associated Multipath TCP connection in its ``MP_JOIN`` option. This identifier must unambiguously identify the corresponding Multipath TCP connection on the server.

A first possible identifier is the four tuple that identifies the initial subflow, i.e. :math:`<IP_{S},IP_{\alpha},p,p_{1}>`. If the server received this identifier in the ``MP_JOIN`` option, it could link the new subflow to the previous one. Unfortunately, this solution does not work in today's Internet. The main concern comes from the middleboxes such as NATs and transparent proxies. To illustrate the problem, consider a simple NAT, such as the one used on most home Wi-Fi access points. :numref:`fig-nat-interference` illustrates a handshake in such an evnrionment. If we assume that the NAT only changes the client's IP address, then the connection is identified by the :math:`<IP_{A},IP_{S},p,p_{1}>` tuple on the smartphone and :math:`<IP_{S},IP_{N},p,p_{1}>` on the server. Note that a NAT could also change the client port. If the smartphone places its local connection identifier inside an ``MP_JOIN`` option, the server might not be able to recognise the corresponding connection in the ``SYN`` packets that it received.
   

.. _fig-nat-interference:
.. tikz:: With Network Address Translation, A naive approach to create a Multipath TCP connection 
   :libs: positioning, matrix, arrows, math

   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=5; \nat=4.5;}
   
   
   \node [red, fill=white,align=center] at (\nat,\max) {NAT \\$IP_{N}$};
   \node [black, fill=white,align=center] at (\c1,\max) {Smartphone \\ $IP_{A}$};
   \node [black, fill=white,align=center] at (\s1,\max) {Server \\$IP_{S}$};

   
   \draw[black,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \draw[red,dashed,very thick,-] (\nat,\max-0.5) -- (\nat,0.5);
   
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\nat,\y-0.5) node [midway, align=center, fill=white] {$IP_{\alpha}\rightarrow IP_{S}$\\SYN};
   \draw[blue,thick, ->] (\nat,\y-0.5) -- (\s1,\y-1) node [midway, align=center, fill=white] {$IP_{N}\rightarrow IP_{S}$\\SYN};   
   \draw[blue,thick, ->] (\s1,\y-1.5) -- (\nat,\y-2) node [midway, align=center, fill=white] {$IP_{S}\rightarrow IP_{N}$\\SYN+ACK};
   \draw[blue,thick, ->] (\nat,\y-2) -- (\c1,\y-2.5) node [midway, align=center, fill=white] {$IP_{S}\rightarrow IP_{A}$\\SYN+ACK};   
   \draw[blue,thick, ->] (\c1,\y-3) -- (\nat,\y-3.5) node [midway, align=center, fill=white] {$IP_{A}\rightarrow IP_{S}$\\ACK};
   \draw[blue,thick, ->] (\nat,\y-3.5) -- (\s1,\y-4) node [midway, align=center, fill=white] {$IP_{N}\rightarrow IP_{S}$\\ACK};


To cope with this problem, Multipath TCP uses a local identifier, called `token` in the Multipath TCP specification, to identify each Multipath TCP connection. The client assigns its token when it initiates a new Multipath TCP connection. A server assigns its token when it accepts a new Multipath TCP connection. These two tokens are chosen idependently by the client and the server. For security reasons, they should be random. The ``MP_JOIN`` option contains the token assigned by the remote host. This is illustrated in :numref:`fig-mptcp-capable-join-token`. The server assigns token `456` to the Multipath TCP connection created as the first subflow. It informs the smartphone by sending this token in its ``MP_CAPABLE`` option in the ``SYN+ACK``. When the client creates the second subflow, it includes this token in the ``MP_JOIN`` option of its ``SYN``.

.. _fig-mptcp-capable-join-token:
.. tikz:: A Multipath TCP connection with two subflows
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=10; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {SYN\small{[seq=x]}\\\small{MP\_Capable[token=123]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MP\_Capable[token=456]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=center, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};
   \draw[blue,thick, ->] (\c1,\y-3) -- (\s1,\y-4) node [midway, align=center, fill=white] {Data\small{[seq=x+1]}};
   \draw[red,thick, ->] (\c2,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {SYN\small{[seq=p]}\\\small{MP\_Join[token=456]}};
   \draw[red,thick, ->] (\s1,\y-5) -- (\c2,\y-6) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=q,ack=p+1]}\\\small{MP\_Join[\ldots]}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {ACK\small{[seq=p+1,ack=q+1]}};

   

.. note:: Multipath TCP in datacenters   
   
   The Multipath TCP architecture :cite:`rfc6182` assumes that at least one of the communicating hosts will use different IP addresses to identify the different paths used by a Multipath TCP connection. In practice, this architectural requirement is not always enforced by Multipath TCP implementations. A Multipath TCP implementation can combine different subflows into one Multipath TCP connection provided that each subflow is identified by a different four-tuple. Two subflows between two communicating hosts can differ in their client-selected ports. This solution has been chosen when Multipath TCP was proposed to mitigate congestion in datacenter networks :cite:`Raiciu_Datacenter:2011`.

   Several designs exist for datacenter networks, but the fat-tree architecture shown in :numref:`fig-fat-tree` is a very popular one.	  

   .. _fig-fat-tree:
   .. tikz:: A simple datacenter network
      :libs: positioning, matrix, arrows, math

       \begin{tikzpicture}[node distance=4cm]
       \tikzset{router/.style = {rectangle, draw, text centered, minimum height=2em}, }
       \tikzset{host/.style = {circle, draw, text centered, minimum height=2em}, }
       \node[router] (C1) {C1};
       \node[router, right= 6cm of C1] (C2) {C2};
       \node[router, below left=1cm of C1] (A1) {A1};
       \node[router, below right= 1cm of C1] (A2) {A2};
       \node[router, below left= 1cm of C2] (A3) {A3};
       \node[router, below right= 1cm of C2] (A4) {A4};
       \node[router, below= 1cm of A1] (E1) {E1};
       \node[router, below= 1cm of A2] (E2) {E2};
       \node[router, below= 1cm of A3] (E3) {E3};
       \node[router, below= 1cm of A4] (E4) {E4};
       \node[host, below left= 0.5cm of E1] (P1) {$\alpha$};
       \node[host, below right= 0.5cm of E1] (P2) {$\beta$};
       \node[host, below left= 0.5cm of E2] (P3) {$\gamma$};
       \node[host, below right= 0.5cm of E2] (P4) {$\delta$};
       \node[host, below left= 0.5cm of E3] (P5) {$\kappa$};
       \node[host, below right= 0.5cm  of E3] (P6) {$\nu$};
       \node[host, below left= 0.5cm of E4] (P7) {$\mu$};
       \node[host, below right= 0.5cm of E4] (P8) {$\pi$};
       \path[draw,thick]
       (P1) edge (E1)
       (P2) edge (E1)
       (P3) edge (E2)
       (P4) edge (E2)
       (P5) edge (E3)
       (P6) edge (E3)
       (P7) edge (E4)
       (P8) edge (E4)
       (E1) edge (A1)
       (E1) edge (A2)
       (E2) edge (A1)
       (E2) edge (A2)
       (E3) edge (A3)
       (E3) edge (A4)
       (E4) edge (A3)
       (E4) edge (A4)
       (A1) edge (C1)
       (A1) edge (C2)
       (A2) edge (C1)
       (A2) edge (C2)
       (A3) edge (C1)
       (A3) edge (C2)
       (A4) edge (C1)
       (A4) edge (C2);

       \end{tikzpicture}


       
   This network topology exposes a large number of equal cost paths between the servers that are shown using circles in :numref:`fig-fat-tree`. For example, consider the paths between the :math:`\alpha` and :math:`\pi` hosts. The paths start at :math:`E1`. This router can reach :math:`E4` and :math:`\pi` via :math:`A1` or :math:`A2`. Each of these two aggregation routers can reach :math:`\pi` via one of the two core routers. These two routers can then balance the flows via both :math:`A3` and :math:`A4`. There are :math:`2^{4}=16` different paths between :math:`\alpha` and :math:`\pi` in this very small network. If each of these routers balance the incoming packets using a hash function that takes as input their source and destination addresses and ports, then the subflows of a Multipath TCP connection that use different client problems will be spread evenly accross the network topology.  Raiciu et al. provide simulations and measurements showing the benefits of using Multipath TCP in datacenters :cite:`Raiciu_Datacenter:2011`.


..  explain architecture and show that an MPTCP connection manages several subflows    

Once a Multipath TCP connection and the additional subflows have been established, we can use them to exchange data. An important point to remember is that a Multipath TCP connection offers a bidirectional bytestream service like a regular TCP connection. This service does not change even if Multipath TCP uses different subflows to carry the data between the sender and the receiver. As an example, consider a sender that sends ``ABCD`` one byte at a time over a Multipath TCP connection composed of two subflows. A naive approach to sedn these bytes would be to simply placed them in TCP segments. This is illustrated in :numref:`fig-mptcp-data-naive` where we assume that the two TCP subflows have already been established.
    
.. _fig-mptcp-data-naive:
.. tikz:: A naive approach to send data over a Multipath TCP connection 
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=10; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {DATA\small{[seq=x,A]}};
   \draw[black,thick, ->] (\s1,\y-1) -- (\s1+4,\y-1) node [midway, align=center, fill=white] {DATA.ind(A)};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white] {ACK\small{[ack=x+1]}};
   \draw[red,thick, ->] (\c2,\y-2) -- (\s1,\y-3) node [midway, align=center, fill=white] {DATA\small{[seq=p,B]}};
   \draw[black,thick, ->] (\s1,\y-3) -- (\s1+4,\y-3) node [midway, align=center, fill=white] {DATA.ind(B)};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c2,\y-4) node [midway, align=center, fill=white] {ACK\small{[ack=p+1]}};
   \draw[blue,thick, ->] (\c1,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {DATA\small{[seq=x+1,C]}};
      \draw[black,thick, ->] (\s1,\y-5) -- (\s1+4,\y-5) node [midway, align=center, fill=white] {DATA.ind(C)};
   \draw[blue,thick, ->] (\s1,\y-5) -- (\c1,\y-6) node [midway, align=center, fill=white] {ACK\small{[ack=x+2]}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {DATA\small{[seq=p+1,D]}};
      \draw[black,thick, ->] (\s1,\y-7) -- (\s1+4,\y-7) node [midway, align=center, fill=white] {DATA.ind(D)};
   \draw[red,thick, ->] (\s1,\y-7) -- (\c2,\y-8) node [midway, align=center, fill=white] {ACK\small{[acl=p+2]}};

In this example, the Smartphone slowly sends data in sequence. The server receives the data in sequence over the two subflows and the server could simply deliver the data as soon as it arrives over each subflow. This is illustrated with the ``DATA.ind(\ldots)`` primitives that represent the delivery of the data to the server application. However, consider now that the first packet sent on the red subflow is lost and is retransmitted together with the fourth byte as shown in :numref:`fig-mptcp-data-naive-2`.


.. _fig-mptcp-data-naive-2:
.. tikz:: A naive approach to send data over a Multipath TCP connection 
   :libs: positioning, matrix, arrows.meta, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=10; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {DATA\small{[seq=x,A]}};
   \draw[black,thick, ->] (\s1,\y-1) -- (\s1+4,\y-1) node [midway, align=center, fill=white] {DATA.ind(A)};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white] {ACK\small{[ack=x+1]}};
   \draw[red,thick, -Circle] (\c2,\y-2) -- (\s1-1,\y-2.8) node [midway, align=center, fill=white] {DATA\small{[seq=p,bseq=1,B]}};

   \draw[blue,thick, ->] (\c1,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {DATA\small{[seq=x+1,C]}};
   \draw[black,thick, ->] (\s1,\y-5) -- (\s1+4,\y-5) node [midway, align=center, fill=white] {DATA.ind(C) ????};
   \draw[blue,thick, ->] (\s1,\y-5) -- (\c1,\y-6) node [midway, align=center, fill=white] {ACK\small{[ack=x+2]}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {DATA\small{[seq=p,BD]}};
   \draw[black,thick, ->] (\s1,\y-7) -- (\s1+4,\y-7) node [midway, align=center, fill=white] {DATA.ind(BD) ????};
   \draw[red,thick, ->] (\s1,\y-7) -- (\c2,\y-8) node [midway, align=center, fill=white] {ACK\small{[acl=p+2]}};


In :numref:`fig-mptcp-data-naive-2`, it is clear that the server cannot simply deliver the data as soon as it receives it to its application. If the server behaves this way, it will deliver ``ACBD`` to its application instead of the ``ABCD`` bytestream send by the smartphone. To cope with the reordering of the data sent over the different subflows, Multipath TCP includes bytestream-level data sequence numbers that enable it to preserve the ordering of the data sent over the bytestream. This is illustrated in :numref:`fig-mptcp-data-seq` with the bytestream-level sequence number shown as ``bseq``. We will detail later how this sequence number is exactly transported by Multipath TCP.

.. _fig-mptcp-data-seq:
.. tikz:: A naive approach to send data over a Multipath TCP connection 
   :libs: positioning, matrix, arrows.meta, math

   \tikzmath{\c1=1; \c2=1.5; \s1=8; \s2=8.5; \max=10; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Smartphone};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {DATA\small{[seq=x,bseq=0,A]}};
   \draw[black,thick, ->] (\s1,\y-1) -- (\s1+4,\y-1) node [midway, align=center, fill=white] {DATA.ind(A)};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white] {ACK\small{[ack=x+1]}};
   \draw[red,thick, -Circle] (\c2,\y-2) -- (\s1-1,\y-2.8) node [midway, align=center, fill=white] {DATA\small{[seq=p,bseq=1,B]}};

   \draw[blue,thick, ->] (\c1,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {DATA\small{[seq=x+1,bseq=2,C]}};

   \draw[blue,thick, ->] (\s1,\y-5) -- (\c1,\y-6) node [midway, align=center, fill=white] {ACK\small{[ack=x+2]}};
   \draw[red,thick, ->] (\c2,\y-5.5) -- (\s1,\y-6.5) node [midway, align=center, fill=white] {DATA\small{[seq=p,bseq=1,BC]}};
   \draw[black,thick, ->] (\s1,\y-6.5) -- (\s1+4,\y-6.5) node [midway, align=center, fill=white] {DATA.ind(BC)};   
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {DATA\small{[seq=p,bseq=3,D]}};
   \draw[black,thick, ->] (\s1,\y-7) -- (\s1+4,\y-7) node [midway, align=center, fill=white] {DATA.ind(D)};   
   \draw[red,thick, ->] (\s1,\y-7) -- (\c2,\y-8) node [midway, align=center, fill=white] {ACK\small{[acl=p+2]}};

   
Thanks to the bytestream sequence number, the server can reorder the data received over the different subflows and preserve the ordering in the bytestream.



Creating a Multipath TCP connection
===================================

Before delving into the details of how a Multipath TCP connection is created, let use first analyze the main requirements of this establishment and how they can be met without considering all the protocol details. During the three-way handshake, TCP hosts agree to establishment a connection, select the initial sequence number in each direction and negotiate the utilization of TCP extensions. In addition to these objectives, the handshake used by Multipath TCP also allows the communicating hosts to:

 - agree to use the Multipath TCP extension
 - exchange the tokens used to identify the connection
 - agree on initial bytestream sequence numbers



To meet the first objective, the client simply needs to send a Multipath TCP option (``MPO```) in its ``SYN``. If the server supports Multipath TCP, it will respond with a ``SYNC+AC`` that carries this option.

To meet the second objective, the simplest solution is reserve some space, e.g. 64 bits, in the ``MPO`` option to encode the token chosen by the host that sends the ``SYN`` or ``SYN+ACK``. With this approach, each host can autonomously select the token that it uses to identify each Multipath TCP connection. To meet the third objective, the simplest solution is also to place the initial sequence number in the ``MPO`` option. :numref:`fig-tcp-handshake-mpo` illustrates a handshake using the ``MPO`` option. 


.. _fig-tcp-handshake-mpo:
.. tikz:: Opening a Multipath TCP connection with a MPO option
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=6; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
	  
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MPO[$Client_{token}$,$Client_{bseq}$]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MPO[$Server_{token}$,$Server_{bseq}$]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};

   \draw[red,thick, ->] (\c2,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {SYN\small{[seq=p]}\\\small{MP\_Join[token=$Server_{token}$]}};
   \draw[red,thick, ->] (\s1,\y-5) -- (\c2,\y-6) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=q,ack=p+1]}\\\small{MP\_Join[\ldots]}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {ACK\small{[seq=p+1,ack=q+1]}};
   
The Multipath TCP working group was worried about the risk of attacks with this approach. When the smartphone creates an additional subflow, it includes the token allocated by the server inside the ``MP_JOIN`` option. This token serves two different purposes. First, it identifies the relevant Multipath TCP connection on the server. Second, it also "authenticates" that the ``SYN`` also originates from this client. Authenticating the client is a key concern from a security viewpoint. The main risk is that an on-path attacker who has observed the token in the ``MP_JOIN`` option can reuse it to create additional subflows from any other source. To cope with this problem, Multipath TCP relies on a shared secret that the client and the server exchange during the initial handshake. The client proposes one halve of the secret and the server the other halve. This is illustrated in :numref:`fig-tcp-handshake-mpo-secret`. The client proposes its part of the shared secret in the ``SYN`` (:math:`Client_{secret}`). The server replies with its part of the secret in the ``SYN+ACK``.
   

.. _fig-tcp-handshake-mpo-secret:
.. tikz:: Creating a Multipath TCP connection with a MPO option
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=9; }
   
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[blue,very thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[blue,very thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \draw[red,thick,->] (\c2,\max-0.5) -- (\c2,0.5);
	  
   \tikzmath{\y=\max-1;}
   
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=left, fill=white] {SYN\small{[seq=x]}\\\small{MPO[$Client_{token}$,$Client_{bseq}$,$Client_{secret}$]}};
   \draw[blue,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=left, fill=white] {SYN+ACK\small{[seq=y,ack=x+1]}\\\small{MPO[$Server_{token}$,$Server_{bseq}$,$Server_{secret}$]}};
   \draw[blue,thick, ->] (\c1,\y-2.1) -- (\s1,\y-3) node [midway, align=left, fill=white] {ACK\small{[seq=x+1,ack=y+1]}};

   \draw[red,thick, ->] (\c2,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white] {SYN\small{[seq=p]}\\\small{MP\_Join[$Server_{token}$,$Client_{random}$]}};
   \draw[red,thick, ->] (\s1,\y-5) -- (\c2,\y-6) node [midway, align=center, fill=white] {SYN+ACK\small{[seq=q,ack=p+1]}\\\small{MP\_Join[$Server_{random}$,HMAC1]}};
   \draw[red,thick, ->] (\c2,\y-6) -- (\s1,\y-7) node [midway, align=center, fill=white] {ACK\small{[seq=p+1,ack=q+1]}\\\small{MP\_Join[HMAC2]}};

   \node[black,fill=white,align=right] at (\c1,0) {HMAC1=HMAC(key=$Server_{secret}$||$Client_{Secret}$,\\msg=$Server_{random}||Client_{random}$)};
   \node[black,fill=white,align=right] at (\c1,-1)  {HMAC2=HMAC(key=$Client_{secret}$||$Server_{Secret}$,\\msg=$Client_{random}||Server_{random}$)};
   
   
Using these two components of the shared secret, the client and the server must be able to authenticate the additional subflows without revealing the shared secret to an attacker who is able to capture packets on the path of the additional subflow. Multipath TCP requires each host to perform a HMAC :cite:`rfc2104` of a random number to confirm their knowledge of the shared secret. This is illustrated in the second part of :numref:`fig-tcp-handshake-mpo-secret`. To create the additional subflow, the client send a ``SYN`` with the ``MP_JOIN`` option containing the :math:`Server_{token}` and a random nonce, :math:`Client_{random}`. The server confirms the establishment of the subflow by sending a ``SYN+ACK`` containing the HMAC computed using the :math:`Client_{random}` and the :math:`Client_{secret}` and :math:`Server_{secret}` input. Thanks to this HMAC computation, the server can reveal that it knows :math:`Client_{secret}` and :math:`Server_{secret}` without explictly sending them. The server also places a random number, :math:`Server_{random}` in the ``MP_JOIN`` option of the ``SYN+ACK``. The client computes a HMAC and returns it in the third ``ACK``. With these two HMACs, the client and the server can authenticate the establishment of the additional subflow without revealing the shared secret.


.. note:: The security of Multipath TCP depends on the security of the initial handshake

   The ability of correctly authenticate the addition of new subflows to a Multipath TCP connection depends on the secrecy of the :math:`Client_{secret}` and :math:`Server_{secret}` exchanged in the ``SYN`` and ``SYN+ACK`` of the initial handshake. An on-path attacker which is able to capture this initial handshake has all the information required to attach a new subflow to this Multipath TCP connectionat any time. Multipath does not include the strong cryptographic techniques (besides HMAC) that would have been required to completely secure the establishment the protocol and the establishment of additional subflows in particular. This threat was considered acceptable for Multipath TCP :cite:`rfc6181` because an attacker who can capture the packets of a single path TCP connection can also inject data inside this connection. To be fully secure Multipath TCP would need to rely on cryptographic techniques that are similar to those used in Transport Layer Security :cite:`rfc8446`. 


The solution described above meets the requirements of the Internet Engineering Task Force. From a security viewpoint, the :math:`Client_{secret}`, :math:`Server_{secret}` and the random nonces should be as large as possible to prevent attacks where their values are simply guessed. Unfortunately, since Multipath TCP uses TCP options to exchange all this information, we need to ensure that it fits inside the extended header of a TCP ``SYN``. The TCP specification :cite:`rfc793` reserves up to 40 bytes to place the TCP options in a ``SYN``. Today's TCP stacks already consume 4 bytes for the ``MSS`` option :cite:`rfc793`, 3 for the ``Window Scale`` option :cite:`rfc1323`, 2 for ``SACK Permitted`` :cite:`rfc2018` and 10 for the timestamp option :cite:`rfc1323`. This leaves only 20 bytes to encode a Multipath TCP option that must contain an initial sequence number, a token and a secret. Multipath TCP solves this problem by deriving these three values from a single field encoded in a TCP option. Let us now analyze the Multipath TCP handshake in more details.

The Multipath TCP handshake
---------------------------

	  
A Multipath TCP connection starts with a three-way handshake like a regular TCP connection. To indicate that it wishes to use Multipath TCP, the client adds the ``MP_CAPABLE`` option to the ``SYN`` segment. In the ``SYN`` segment, this option only contains some flags and occupies 4 bytes. The server replies with a ``SYN+ACK`` segment than contains an ``MP_CAPABLE`` option including a server generated 64 bits random key that will be used to authenticate connections over different paths. The client concludes the handshake by sending an ``MP_CAPABLE`` option in the ``ACK`` segment containing the random keys chosen by the client and the server.

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
.. tikz:: MPTCP Join
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

   Explained in NSDI paper :cite:`Raiciu_Hard:2012`       
   
Data transfer
=============
	  
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

   

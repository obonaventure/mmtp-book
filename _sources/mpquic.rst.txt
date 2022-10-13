Multipath QUIC
**************

As the development of QUIC progressed within the IETF, academic researchers have started to explore how QUIC could be extended with multipath capabilities. The first approaches built upon Google's version of QUIC. The first prototype was implemented inside ``quic-go`` :cite:`de2017multipath`. A second version of the protocol which can be easily extended using plugins was then proposed inside ``picoquic`` :cite:`de2019pluginizing`. An alternative approach was proposed in parallel :cite:`viernickel2018multipath`. The most recent solutions :cite:`de2021multiflow,zheng2021xlink` leverage the most recent QUIC specification as described in this document.

Discussions within the IETF took some time to start, despite early proposals :cite:`draft-deconinck-multipath-quic-00`. Recently, the QUIC working group adopted :cite:`draft-lmbdhk-quic-multipath` as a starting point for the development of an IETF specification for multipath QUIC. It combines the ideas initially proposed in three different drafts :cite:`draft-liu-multipath-quic,draft-deconinck-quic-multipath,draft-huitema-quic-mpath-option`.

In this chapter, we explain the two "levels" of Multipath support that exist for QUIC. We start with the connection migration facility which is supported by QUIC :cite:`rfc9000`. This feature was included in the initial specification to cope with NAT rebindings but also provides support for handovers. Connection migration mainly enables a QUIC connection to switch from one path to another. We then describe in more details the ongoing effort to define Multipath QUIC which provides the ability to use two or more paths simultaneously.



.. intro to connection migration   

QUIC connection migration
-------------------------


.. connection migration as a multipath features, discuss its limitations

As explained in :ref:`chapter-quic`, QUIC uses connection identifiers. These connection identifiers are used for different purposes. On the server side, they were intially proposed to allow load-balancers to spread the packets of different connections to different servers without having to maintain any state. In addition, QUIC 's connection identifiers also enable clients to migrate connections from one path to another or even on the same path.

QUIC connection migrations occur in two steps. As an example, we consider client triggered migrations. These are the most important from a deployment viewpoint. A client can decide to migrate its connection for various reasons, including privacy and performance. A common scenario is a smartphone that moves and goes progressively out of reach of its Wi-Fi access point. When the smartphone notices a decrease in performance of the Wi-Fi network (lower signal to noise ratio, more losses or retransmissions, ...), it can decide to migrate the QUIC connection over the cellular interface. A naive solution would be to simply move the QUIC packets from one interface to another using the same connection identifiers. This is illustrated in :numref:`fig-quic-naive-migration`. The QUIC connection was established from the client IP address, :math:`IP_{\alpha}`, to the server's IP address, :math:`IP_S`. The first two packets show a simple exchange over this connection. Before sending its second packet, the client decides to switch to the cellular interface. This interface is illustrated in red and its IP address is :math:`IP_{\beta}`. 

.. _fig-quic-naive-migration:
.. tikz:: A naive approach to migrate a QUIC connection from Wi-Fi to cellular
   :libs: positioning, matrix, arrows, math


   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=6; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1-0.5,\max-0.5) -- (\c1-0.5,0.5);
   \draw[red,dashed,thick,->] (\c1+0.5,\max-0.5) -- (\c1+0.5,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \node [black, fill=white] at (\c1-0.5,\max-0.5) {$IP_{\alpha}$};
   \node [red, fill=white] at (\c1+0.5,\max-0.5) {$IP_{\beta}$};
   \node [black, fill=white] at (\s1,\max-0.5) {$IP_{S}$};
	  
   \tikzmath{\y=\max-1;}
   \draw[black,thick, ->] (\c1-0.5,\y) -- (\s1,\y-1) node [midway, align=center, fill=white]  {src=$IP_{\alpha}$,dst=$IP_S$,DCID=$\mu$\\1-RTT(...)};
   \draw[black,thick, ->] (\s1,\y-1) -- (\c1-0.5,\y-2) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_{\alpha}$\\1-RTT(...)};
   \draw[red,thick, ->] (\c1+0.5,\y-2) -- (\s1,\y-3) node [midway, align=center, fill=white]  {src=$IP_{\beta}$,dst=$IP_S$,DCID=$\mu$\\1-RTT(...)};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c1+0.5,\y-4) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_{\beta}$\\1-RTT(...)};

   
Unfortunately, this naive approach is not secure. Consider a server that receives a QUIC packet from the smartphone's cellular interface. This packet originates from a different IP address, but contains the same connection identifier. If the server accepts this packet and decides to reply over the cellular path, this creates several security risks. First, consider an attacker who managed to capture a packet sent by the client over the Wi-Fi network. By sending again this unmodified QUIC packet from its own IP address, the attacker could disrupt the ongoing connection by forcing the server to send replies to its own IP address. Furthermore, this also opens a risk of denial of service attacks if the packet copied by the attacker contains a request for a large object. QUIC copes with these problems by using path-specific connection identifiers and the path validation mechanism.

A QUIC connection identifier is always bound to a specific IP address. When a QUIC host receives a QUIC packet, it verifies that the packet originates from the associated source. The QUIC specification does not prescribe how this verification can be done, but a simple approach is to encode a hash of the source IP address inside the connection identifier.

When a QUIC connection starts the server verifies that the client receives the packets that it sends to prevent attacks from spoofed addresses. This verification is part of the handshake and may in some cases involve the utilization of ``RETRY`` packets. Consider a malicious client using address :math:`IP_{\alpha}` but wishes to create a denial of service attack against address :math:`IP_{\mu}`. This client could initiate a connection with a server using address :math:`IP_{\alpha}`, request a large object and send a packet spoofing address :math:`IP_{\mu}` to force the server to send all reply packets to the victim. To cope with this attack, a QUIC server must first validate a new client address before sending a large number of packets. To validate a new client address, the server simply needs to send a ``PATH_CHALLENGE`` frame that contains a random number. This frame is encrypted using the connection keys, like all QUIC frames. Upon reception of this frame, the client can extract the random number and return it in a ``PATH_RESPONSE`` frame to the server. Upon reception of this frame, the server has the confirmation that the client can also receive packets on the new address and thus it can safely be used. The client can also validate a path as shown below. 


To enable a client to migrate a QUIC connection, the server must first advertise at least one different connection identifier. This is done with the ``NEW_CONNECTION_ID`` frame. The client uses this additional connection identifier to try to move the connection to a new path. The client cannot use a new path before having the guarantee that the server can reply over the new path. To verify that the new path is bidirectional, the client sends a ``PATH_CHALLENGE`` frame in a QUIC packet that uses the new connection identifier over the new path. This frame mainly contains a 64 bits random nonce that must be echoed by the server. It also includes some padding to check the path's MTU as done during the handshake. Upon reception of this packet, the server detects an attempt to use a new path with the new connection identifier. It replies with a ``PATH_RESPONSE`` frame that echoes the client nonce. The server may also perform its own path validation by sending a ``PATH_CHALLENGE`` with a different nonce in the same packet as the ``PATH_RESPONSE``. The client considers that the path has been validated upon reception of the valid ``PATH_RESPONSE`` frame. The packets that contain the ``PATH_CHALLENGE`` and ``PATH_RESPONSE`` frames are usually padded with ``PADDING`` frames. The client then switches to the new connection identifier and the new path for all the frames that it sends. It may still continue to receive packets over the former path for some time. The server will switch to the new path once it has received a response to its ``PATH_CHALLENGE`` if it decided to validate the new path. Otherwise, the reception of a QUIC packet that contains other frames than ``PATH_CHALLENGE``, ``PATH_RESPONSE``, ``NEW_CONNECTION_ID`` or ``PADDING`` also indicates that the path is active. The client could send a ``NEW_CONNECTION_ID`` frame together with the ``PATH_CHALLENGE`` frame if the client uses a non-null connection identifier and it has not sent a ``NEW_CONNECTION_ID`` frame before. This is illustrated in :numref:`fig-quic-client-migration`.

.. _fig-quic-client-migration:
.. tikz:: A QUIC connection migration initiated by the client
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=8; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1-0.5,\max-0.5) -- (\c1-0.5,0.5);
   \draw[red,dashed,thick,->] (\c1+0.5,\max-0.5) -- (\c1+0.5,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
	  
   \tikzmath{\y=\max-1;}
   \draw[black,thick, ->] (\c1-0.5,\y) -- (\s1,\y-1) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\alpha$\\1-RTT(...)};
   \draw[black,thick, ->] (\s1,\y-1) -- (\c1-0.5,\y-2) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_C$\\1-RTT(...)};
   \draw[red,thick, ->] (\c1+0.5,\y-2) -- (\s1,\y-3) node [midway, align=center, fill=white]  {src=$IP_X$,dst=$IP_S$,DCID=$\beta$\\1-RTT(PATH\_CHALLENGE($x$))};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c1+0.5,\y-4) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_X$\\1-RTT(PATH\_RESPONSE($x$),PATH\_CHALLENGE($y$)};   
   \draw[red,thick, ->] (\c1+0.5,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white]  {src=$IP_X$,dst=$IP_S$,DCID=$\beta$\\1-RTT(PATH\_RESPONSE($y$),...)};
   \draw[red,thick, ->] (\s1,\y-5) -- (\c1+0.5,\y-6) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_X$\\1-RTT(...)};
   

  
The examples above showed a connection that migrates from one network interface to another. This is expected to be a frequent situation for smartphones that move. However, there are also scenarios where the client can trigger a connection migration even if it uses a single network interface. First, the client application can decide to migrate its QUIC connection every :math:`n` minutes. This could be useful for an application that provides a VPN-like service as proposed :cite:`de2019pluginizing`. By regularly changing their connection identifiers, such VPN services could prevent some middleboxes from detecting and blocking them. Another scenario are the unintended migrations caused by NAT.


.. note:: Unintended QUIC connection migrations

   We have described how QUIC clients can trigger connection migrations. There are situations when connection migration occurs without being triggered by the client. A classical example is when there is a NAT on the path between the client and the server. The QUIC connection has been idle for some time and the NAT has removed the mapping from the client's private IP address to a public one. When the client sends the next packet over the connection, the NAT creates a new mapping and thus assigns a different IP address to the client. The server receives a packet that uses the same connection identifier but comes from a different IP address than the initial one. This is illustrated in :numref:`fig-quic-nat-migration`. Upon reception of the QUIC packet coming from the new IP address (shown in red in :numref:`fig-quic-nat-migration`, the server triggers a path validation. Once the path has been validated, the QUIC connection can continue.

   
.. _fig-quic-nat-migration:
.. tikz:: A QUIC connection migration triggered by a NAT
   :libs: positioning, matrix, arrows, math


   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=7; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
	  
   \tikzmath{\y=\max-1;}
   \draw[black,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\alpha$\\1-RTT(...)};
   \draw[black,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_C$\\1-RTT(...)};
   \draw[red,thick, ->] (\c1,\y-2) -- (\s1,\y-3) node [midway, align=center, fill=white]  {src=$IP_Y$,dst=$IP_S$,DCID=$\alpha$\\1-RTT(...)};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c1,\y-4) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_Y$\\1-RTT(PATH\_CHALLENGE($z$))};
   \draw[red,thick, ->] (\c1,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_Y$\\1-RTT(PATH\_RESPONSE($z$))};
	     


   
The previous examples have shown that a client can trigger a connection migration to improve performance or for privacy reasons. Our examples have considered that the clients can use different IP addresses while the servers have a stable IP address. This corresponds to most deployments, but not all of them. Today, many servers are dual-stack. They support both IPv4 and IPv6. When a client starts a QUIC connection over one address family, it could be useful for the client to learn the other server address to be able to switch to this address if the other fails. Another interesting type of deployments are the server farms where each server has both an anycast address and a unicast one. All servers use the same anycast address and this address is the one advertised using the DNS. When a client initiates a QUIC connection, it targets the anycast address. The ``Initial`` QUIC packet is load-balanced to one of the servers of the farm and all subsequent packets of this connection are load-balanced to the same server. In this deployment, all packets must be processed by the load-balancer before reaching the server. When the load is high, the load-balancer could become a bottleneck and it would be useful to allow QUIC connections to migrate to the unicast address of their servers since unicast address bypasses the load-balancer. The first version of QUIC provides partial support for this bypass by allowing the server to advertise its preferred unicast addresses (IPv4 and IPv6) using the ``preferred_address`` transport parameter during the handshake. However, according to QUIC specification :cite:`rfc9000`, a client SHOULD, but is not forced to, migrate to one of the preferred addresses announced by the server. This migration can only be triggered by the client, there is no way for the server to impose a migration.  

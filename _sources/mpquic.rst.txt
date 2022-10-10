Multipath QUIC
**************

As the development of QUIC progressed within the IETF, academic researchers have started to explore how QUIC could be extended with multipath capabilities. The first approaches built upon Google's version of QUIC. The first prototype was implemented inside ``quic-go`` :cite:`de2017multipath`. A second version of the protocol which can be easily extended using plugins was then proposed inside ``picoquic`` :cite:`de2019pluginizing`. An alternative approach was proposed in :cite:`viernickel2018multipath`. The most recent solutions :cite:`de2021multiflow,zheng2021xlink` leverage the most recent QUIC specification as described in this document.

Discussions within the IETF took some time to start, despite early proposals :cite:`draft-deconinck-multipath-quic-00`. Recently, the QUIC working group adopted :cite:`draft-lmbdhk-quic-multipath` as a starting point for the development of an IETF specification for multipath QUIC. It combines the ideas initially proposed in three different drafts :cite:`draft-liu-multipath-quic,draft-deconinck-quic-multipath,draft-huitema-quic-mpath-option`.



.. intro to connection migration   

Migrating QUIC connections   
--------------------------


.. connection migration as a multipath features, discuss its limitations

As explained above, QUIC uses connection identifiers. These connection identifiers are used for different purposes. On the server side, they can be used by load-balancers to spread the packets of different connections to different servers. But QUIC 's connection identifiers also enable clients to migrate connections from one path to another or even on the same path.


QUIC connection migrations occur in two steps. As an example, we consider client triggered migrations. These are the most important from a deployment viewpoint. A client can decide to migrate its connection for various reasons, including privacy and performance. A common scenario is a smartphone that moves and goes progressively out of reach of the Wi-Fi access point. When the smartphone notices a decrease in performance of the Wi-Fi network (lower signal to noise ratio, more losses or retransmissions, ...), it can decide to migrate the QUIC connections over the cellular interface. A naive solution would be to simply move the QUIC packets from one interface to another using the same connection identifiers. This is illustrated in :numref:`fig-quic-naive-migration`. The QUIC connection was established from the client IP address, :math:`IP_C`, to the server's IP address, :math:`IP_S`. The first two packets show a simple exchange over this connection. Before sending its second packet, the client decides to use its second interface to send the subsequent packets. This interface is illustrated in red on the figure and its IP address is :math:`IP_X`. The client sends its second packet over this interface.

.. _fig-quic-naive-migration:
.. tikz:: A naive approach to migrate a QUIC connection from Wi-Fi to cellular
   :libs: positioning, matrix, arrows, math


   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=5; }
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
   \draw[red,thick, ->] (\c1+0.5,\y-2) -- (\s1,\y-3) node [midway, align=center, fill=white]  {src=$IP_X$,dst=$IP_S$,DCID=$\alpha$\\1-RTT(...)};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c1+0.5,\y-4) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_X$\\1-RTT(...)};

   
Unfortunately, this naive approach has several problems. Consider the server that receives the first QUIC packet from the smartphone's cellular interface. This packet originates from a different IP address than the previous one, but still belongs to the same connection. If the server accepts this packet and moves the connection to the cellular path, this creates several security risks. First, consider an attacker who has captured a packet over the Wi-Fi network. By sending again this unmodified packet from another IP address, the attacker could disrupt the ongoing connection by forcing the server to send replies to its own IP address. This also opens a risk of denial of service attack as the server could send a large number of packets to the smartphone's new IP address. QUIC copes with these problems by using path-specific connection identifiers and the path validation mechanism.

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

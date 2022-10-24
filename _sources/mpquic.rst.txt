Multipath QUIC
**************

As the development of QUIC progressed within the IETF, academic researchers have started to explore how QUIC could be extended with multipath capabilities. The first approaches built upon Google's version of QUIC. The first prototype was implemented inside ``quic-go`` :cite:`de2017multipath`. A second version of the protocol which can be easily extended using plugins was then proposed inside ``picoquic`` :cite:`de2019pluginizing`. An alternative approach was proposed in parallel :cite:`viernickel2018multipath`. The most recent solutions :cite:`de2021multiflow,zheng2021xlink` leverage the most recent QUIC specification as described in this document.

Discussions within the IETF took some time to start, despite early proposals :cite:`draft-deconinck-multipath-quic-00`. Recently, the QUIC working group adopted :cite:`draft-lmbdhk-quic-multipath` as a starting point for the development of an IETF specification for multipath QUIC. It combines the ideas initially proposed in three different drafts :cite:`draft-liu-multipath-quic,draft-deconinck-quic-multipath,draft-huitema-quic-mpath-option`.


.. spelling:word-list::

   rebinding
   rebindings

In this chapter, we explain the two "levels" of Multipath support that exist for QUIC. We start with the connection migration facility which is supported by QUIC :cite:`rfc9000`. This feature was included in the initial specification to cope with NAT rebindings but also provides support for handovers. Connection migration mainly enables a QUIC connection to switch from one path to another. We then describe in more details the ongoing effort to define Multipath QUIC which provides the ability to use two or more paths simultaneously.



.. intro to connection migration   

QUIC connection migration
-------------------------


.. connection migration as a multipath features, discuss its limitations

As explained in :ref:`chapter-quic`, QUIC uses connection identifiers. These connection identifiers are used for different purposes. On the server side, they were initially proposed to allow load-balancers to spread the packets of different connections to different servers without having to maintain any state. In addition, QUIC 's connection identifiers also enable clients to migrate connections from one path to another or even on the same path.

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


To enable a client to migrate a QUIC connection, the server must first advertise at least one different connection identifier. This is done with the ``NEW_CONNECTION_ID`` frame. The client uses the additional connection identifier advertised by the server to try to move the connection to a new path. The client cannot use a new path before having the guarantee that the server can reply over the new path. To verify that the new path is bidirectional, the client sends a ``PATH_CHALLENGE`` frame in a QUIC packet that uses the new connection identifier over the new path. This frame mainly contains a 64 bits random nonce that must be echoed by the server. It also includes some padding to check the path's MTU as done during the handshake. Upon reception of this packet, the server detects an attempt to use a new path with the new connection identifier. It replies with a ``PATH_RESPONSE`` frame that echoes the client nonce. The server may also perform its own path validation by sending a ``PATH_CHALLENGE`` with a different nonce in the same packet as the ``PATH_RESPONSE``. The client considers that the path has been validated upon reception of the valid ``PATH_RESPONSE`` frame. The packets that contain the ``PATH_CHALLENGE`` and ``PATH_RESPONSE`` frames are usually padded with ``PADDING`` frames. The client then switches to the new connection identifier and the new path for all the frames that it sends. It may still continue to receive packets over the former path for some time. The server will switch to the new path once it has received a response to its ``PATH_CHALLENGE`` if it decided to validate the new path. Otherwise, the reception of a QUIC packet that contains other frames than ``PATH_CHALLENGE``, ``PATH_RESPONSE``, ``NEW_CONNECTION_ID`` or ``PADDING`` also indicates that the path is active. The client could send a ``NEW_CONNECTION_ID`` frame together with the ``PATH_CHALLENGE`` frame if the client uses a non-null connection identifier and it has not sent a ``NEW_CONNECTION_ID`` frame before. This is illustrated in :numref:`fig-quic-client-migration`.

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

Multipath extensions for QUIC
-----------------------------

.. spelling:word-list::

   failovers

QUIC's connection migration features mainly cope with unexpected network events such as NAT rebinding or failovers. There are however other types of events which could benefit from true multipath capabilities. These include `make before break` handovers or aggregating different paths to obtain higher bandwidth or lower latency.

The Multipath extensions to QUIC :cite:`draft-ietf-quic-multipath` provide all the protocol mechanisms that are required by these scenarios. As other QUIC extensions, the utilization of the multipath extensions is negotiated by using the ``enable_multipath`` transport parameter during the handshake. The client proposed this transport parameter and if the server supports the multipath extensions, replies with a non-zero value for this transport parameter. In addition, the ``active_connection_id_limit`` QUIC transport parameter also plays an important role for multipath. This transport parameter specifies the maximum number of connection identifiers that a QUIC implementation agrees to maintain during a connection. Since each path corresponds to a pair of connection identifiers, the ``active_connection_id_limit`` restricts the number of paths that a Multipath QUIC connection will be able to use. The QUIC specification :cite:`rfc9000` requires regular QUIC implementations to support at least two connection identifiers on each QUIC connection. :numref:`fig-mpquic-tp` illustrates the exchange of these transport parameters during a QUIC handshake. The client advertises its transport parameters in the ClientHello which is included in the CRYPTO frame of the Initial packet. The server returns its transport parameters in the TLS Encrypted Extensions that are included in its Handshake packet. By advertising ``y`` as its ``active_connection_id_limit``, the server indicates that it can manage up to ``y`` different connection identifies announced by the client. Similarly, the client can manage up to ``x`` connection identifiers announced by the server. Although the minimum value for the ``active_connection_id_limit`` transport parameter is 2 in the QUIC specification :cite:`rfc9000`, it can be expected that Multipath QUIC deployments will use large values.



.. _fig-mpquic-tp:
.. tikz:: During the multipath QUIC handshake, client and server exchange the ``enable_multipath`` and ``active_connection_id_limit`` transport parameters
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=5; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
	  
   \tikzmath{\y=\max-1;}
   \draw[red,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {Initial(CRYPTO[\ldots enable\_multipath=0x1,\\active\_connection\_id\_limit=x])};
   \draw[red,thick, ->] (\s1,\y-1) -- (\c1,\y-2) node [midway, fill=white]  {Initial(CRYPTO,ACK)};

   \draw[blue,thick, ->] (\s1,\y-1.75) -- (\c1,\y-2.75) node [midway, align=center, fill=white] {Handshake*(CRYPTO[\ldots enable\_multipath=0x1,\\active\_connection\_id\_limit=y)};


.. note:: Current values of the ``active_connection_id_limit`` transport parameters

	  
   As of October 2022, there is no real deployment of Multipath QUIC. A scan of some QUIC servers revealed the following utilization of this transport parameter:
   
   - ``facebook.com``, ``cloudflare.com``, ``google.com`` do not advertise the ``active_connection_id_limit`` parameter
   - ``msquic.net`` sets the ``active_connection_id_limit`` parameter to ``4``
   - ``quic.ngins.org`` sets the ``active_connection_id_limit`` parameter to ``2`` 
   - ``haproxy.org`` and ``litespeedtech.com`` set the ``active_connection_id_limit`` parameter to ``8``
   

.. todo:: what are the current active_connection_id_limit used . unclear picoquic et quiche


With the current version of Multipath QUIC :cite:`draft-ietf-quic-multipath` only the client can create additional paths on a QUIC connection. This restriction was placed in the first version of Multipath QUIC because it is expected that most clients will be behind firewalls or NATs that already block the establishment of server-initiated paths. However, this restriction could be lifted in a future version of the protocol. 

A Multipath QUIC connection can combine different paths. For Multipath QUIC, a network path is a four-tuple :math:`IP_{src}`, :math:`IP_{dst}`, :math:`Port_{src}`, :math:`Port_{dst}`. Two paths used on a Multipath QUIC connection must different by using at least one element of the four tuple. 


	  
The path used for the handshake is the initial path of a Multipath QUIC connection. This path is identified by using the connection identifiers chosen by the client and the server during the handshake. Once the QUIC connection has been established, both the client and the server can advertise additional connection identifiers using the ``NEW_CONNECTION_ID`` frame. Both the client and the server store the received connection identifiers in a table and can use them for connection migration and to create new paths for Multipath QUIC.

The ``NEW_CONNECTION_ID`` frame does not only advertises new connection identifiers. It allows to manage the set of connection identifiers that are stored by the remote host. The ``NEW_CONNECTION_ID`` frame contains several sub-fields as shown in :numref:`fig-mpquic-new-connection-id`. Each connection identifier is identified by its sequence number in the ``NEW_CONNECTION_ID`` frame.


.. code-block:: console
   :caption: The NEW_CONNECTION_ID frame
   :name: fig-mpquic-new-connection-id
	  
   NEW_CONNECTION_ID Frame {
	  Type (i) = 0x18,
	  Sequence Number (i),
	  Retire Prior To (i),
	  Length (8),
	  Connection ID (8..160),
	  Stateless Reset Token (128)
   }

QUIC also defines a ``RETIRE_CONNECTION_ID`` allowing a host to retire a connection identifier that it previously advertised to a peer. This frame only contains the sequence number of the connection identifier that needs to be removed.


.. code-block:: console
   :caption: The RETIRE_CONNECTION_ID frame
   :name: fig-mpquic-retire-connection-id
	  
   RETIRE_CONNECTION_ID Frame {
	  Type (i) = 0x19,
	  Sequence Number (i)
   }



During the handshake, the client and the server agree on the connection identifiers   they they use to identify the connection in the incoming packets. The client identifies the CID selected by the server with sequence number 0 and similarly for the server. :numref:`fig-mpquic-ncid-retire-cid` illustrates the utilization of the ``NEW_CONNECTION_ID`` and ``RETIRE_CONNECTION_ID`` frames.

.. _fig-mpquic-ncid-retire-cid:
.. tikz:: Thanks to the ``NEW_CONNECTION_ID`` and ``RETIRE_CONNECTION_ID`` frames, the client and the server can manage a list of available connection identifiers. 
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=9; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1,\max-0.5) -- (\c1,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
	  

   \node [black, fill=white, align=left] at (\c1-2, \max-1) {Local $List_{CID}$: $0:\alpha$\\Remote $List_{CID}$: $0:\beta$};
   \node [black, fill=white, align=left] at (\s1+2, \max-1) {Local $List_{CID}$: $0:\beta$\\Remote $List_{CID}$: $0:\alpha$};


   \tikzmath{\y=\max-2;}
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {NEW\_CONNECTION\_ID[seq=1,rp=0,$\delta$]};
   \node [black, fill=white, align=left] at (\c1-2, \y) {Local $List_{CID}$: $0:\alpha,1:\delta$\\Remote $List_{CID}$: $0:\beta$};
   \node [black, fill=white, align=left] at (\s1+2, \y-1) {Local $List_{CID}$: $0:\beta$\\Remote $List_{CID}$: $0:\alpha,1:\delta$};

   
   \tikzmath{\y=\max-5;}
   \node [black, fill=white, align=left] at (\s1+2, \y) {Local $List_{CID}$: $0:\beta,1:\gamma$\\Remote $List_{CID}$: $0:\alpha,1:\delta$};
   \draw[blue,thick, -
   >] (\s1,\y) -- (\c1,\y-1) node [midway, fill=white] {NEW\_CONNECTION\_ID[seq=1,rp=0,$\gamma$]};
   \node [black, fill=white, align=left] at (\c1-2, \y-1) {Local $List_{CID}$: $0:\alpha,1:\delta$\\Remote $List_{CID}$: $0:\beta,1:\gamma$};

   
   \tikzmath{\y=\max-7;}
   \node [black, fill=white, align=left] at (\c1-2, \y) {Local $List_{CID}$: $0:\alpha$\\Remote $List_{CID}$: $0:\beta,1:\gamma$};
   \draw[blue,thick, ->] (\c1,\y) -- (\s1,\y-1) node [midway, align=center, fill=white] {RETIRE\_CONNECTION\_ID[seq=1]};
   \node [black, fill=white, align=left] at (\s1+2, \y-1) {Local $List_{CID}$: $0:\beta,1:\gamma$\\Remote $List_{CID}$: $0:\alpha$};

.. spelling:word-list::

   hypergiants
   
.. note:: Support of zero-length connection identifiers with Multipath QUIC


   QUIC version is already a complex protocol that supports many optional features. One of these is the support for zero-length connection identifiers. This feature is used by servers operated by hypergiants to reduce the per packet overhead when a server interacts with a smartphone or laptop that supports a small number of QUIC connections. These clients can easily rely on the UDP port numbers to identify the QUIC connection to which a received QUIC packet belongs. During the design of Multipath QUIC, there was a debate on whether zero-length connection identifiers should also be supported by Multipath QUIC. This creates some problems that are outside the scope of this introduction :cite:`de2022packet`. In the end, zero-length connection identifiers are supported by Multipath QUIC :cite:`draft-ietf-quic-multipath`, but with some restrictions. In this document, we do not describe this restricted deployment and focus on the utilization of Multipath QUIC with real connection identifiers on both clients and servers. 



To illustrate the creation of a new path on a Multipath QUIC connection, let us consider a smartphone connected to both Wi-Fi and cellular. The client has created a QUIC connection with a server using its Wi-Fi address, but it would like to create an additional path over the cellular interface. For this, the client first needs a local and a remote connection identifier to identify the new path. These identifiers can be obtained from the local and remote :math:`List_{CID}` that are maintained for each connection. As for the connection migration feature, a new connection identifier cannot be used immediately. It must be validated. The client must perform path validation when it starts to use a new connection identifier on the cellular interface. Similarly, the server must validate the new path chosen by the client. This is illustrated on :numref:`fig-mpquic-create-path`. Once the path has been validated, it can be used to carry QUIC packets. To refuse the addition of a new path, the server simply refuses to respond to the ``PATH_CHALLENGE`` frame sent by the client. 


.. _fig-mpquic-create-path:
.. tikz:: To add a path to an existing connection, the client and the server select an available connection identifier and validate the new path. 
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
   \node [black, fill=white] at (\c1-0.5,\max-0.5) {$IP_{W}$};
   \node [red, fill=white] at (\c1+0.5,\max-0.5) {$IP_{C}$};
   \node [black, fill=white] at (\s1,\max-0.5) {$IP_{S}$};


   \tikzmath{\y=\max-1;}
   \node [black, fill=white, align=left] at (\s1+2, \y-0.5) {Local $List_{CID}$: $0:\beta,1:\gamma$\\Remote $List_{CID}$: $0:\alpha,1:\delta,2:\pi$};
   \node [black, fill=white, align=left] at (\c1-2, \y-0.5) {Local $List_{CID}$: $0:\alpha,1:\delta$\\Remote $List_{CID}$: $0:\beta,1:\gamma$};
   
   \draw[red,thick, ->] (\c1+0.5,\y-1) -- (\s1,\y-2) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\pi$\\PATH\_CHALLENGE($x$)};
   \draw[red,thick, ->] (\s1,\y-3) -- (\c1+0.5,\y-4) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_C$,DCID=$\gamma$\\PATH\_RESPONSE($x$),PATH\_CHALLENGE($y$)};
   \node [black, fill=white, align=left] at (\c1-2,\y-4) {path validated\\path\_id=2};
   
   \draw[red,thick, ->] (\c1+0.5,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\delta$\\1-RTT(PATH\_RESPONSE($y$),...)};
   \node [black, fill=white, align=left] at (\s1+2,\y-5) {path validated\\path\_id=1};


Once a path has been validated, it is identified by the sequence number of the connection identifier used to send packets on this path. This path identifier is important because it unambiguously identifies a path and is used a a reference in several frames. For example, the ``PATH_ABANDON`` frame, which carries a path identifier, an error code and some additional information allows a peer to close a path. This frame can be sent over any of the available paths. In the example of :numref:`fig-mpquic-create-path`, if the smartphone looses its cellular interface, it would send ``PATH_ABANDON(id=2,...)`` over the Wi-Fi path. Upon reception of this frame, the server would know that it should stop sending packets over the cellular path. 

.. code-block:: console
   :caption: The PATH_STATUS frame 
   :name: fig-mpquic-path_status
	  
   PATH_STATUS Frame {
       Type (i) = TBD-03 (experiments use 0xbaba06),
       Path Identifier (..),
       Path Status sequence number (i),
       Path Status (i),
   }

The current Multipath QUIC draft :cite:`draft-ietf-quic-multipath` also defines a ``PATH_STATUS`` frame that allows a peer to indicate the status of a path. When a path is created, its status is set to `Available`. This indicates that the path can be used to send data. Using the ``PATH_STATUS`` frame, a peer can set the status of a path to `Standby`. In this case, the path should not be used to send non-probing packets until another ``PATH_STATUS`` frame switches it back to the `Available` state. Each ``PATH_STATUS`` frame carries a sequence number to cope with the loss of a ``PATH_STATUS`` frame. 




.. note:: How does a client learn the server addresses ?

	  
   In the example above, the client created a path towards the address used by the server during the initial handshake. Many servers are dual-stack and have both an IPv4 and and IPv6 address. Given that the performance of the IPv4 and IPv6 paths sometimes differ and that they do not always fail simultaneously, it could be useful for a client to be able to create an additional path using the other address family. Furthermore, some servers have several IPv4 or IPv6 addresses, e.g. because they have several network interfaces in an enterprise network or because they belong to network that use IPv6 host-based multihoming :cite:`piraux2022multiple`. When interacting with dual-stack servers, the client could obtain the server address in the other address family using the `preferred_address` transport parameter supported by QUIC version 1 :cite:`rfc9000`. For multihomed servers, there are discussions on allowing servers to advertise their alternate addresses :cite:`draft-piraux-quic-additional-addresses`.

.. exchanging data

To exchange data, Multipath QUIC associates a packet sequence number space to each path and defines a new ``ACK_MP`` frame that acknowledges the packets received over a given path. The ``ACK_MP`` frame contains the same information as QUIC's ``ACK`` frame with a `Packet Number Space Identifier`. Thanks to this identifier, an ``ACK_MP`` frame can be sent over any path. For example, on a QUIC connection that uses a high bandwidth but long-delay satellite link and low delay but low bandwidth terrestrial link it is possible to send all the acknowledgment frames over the low delay link. Other policies to send acknowledgments are of course possible.

As QUIC version 1, Multipath QUIC adds a unique sequence number to each packet and acknowledges the packets received over each path using the ``ACK_MP`` frame :numref:`fig-mpquic-ack_mp`. 


.. code-block:: console
   :caption: The ACK_MP frame
   :name: fig-mpquic-ack_mp
	  
   ACK_MP Frame {
       Type (i) = TBD-00..TBD-01 (experiments use 0xbaba00..0xbaba01),
       Packet Number Space Identifier (i),
       Largest Acknowledged (i),
       ACK Delay (i),
       ACK Range Count (i),
       First ACK Range (i),
       ACK Range (..) ...,
       [ECN Counts (..)],
   }

A Multipath QUIC data exchange is illustrated in :numref:`fig-mpquic-data`. We consider a smartphone connected to a server using Wi-Fi and cellular. The initial path was created using the Wi-Fi interface (the smartphone uses CID=:math:`\alpha` and the server :math:`\beta`). This path corresponds to the Packet Number Space Identifier `0` on both the smartphone and the server. The smartphone has later created a second path on its cellular interface. On this second path, the smartphone sends packets using the :math:`\pi` CID and receives them with CID :math:`\delta`. This path uses PNSI `2` on the server and `1` on the smartphone. The smartphone sends three packets on the cellular path and the second is lost. It then sends one packet over the Wi-Fi path. The server returns two ``ACK_MP`` frames over the Wi-Fi path. The first acknowledges the packets received over the cellular path (PNSI `2`). The second acknowledges the packets received over the Wi-Fi path (PNSI `0`). Upon reception of these acknowledgments, the client retransmits the frames that we included in the packet lost over the cellular path.
   
   
.. _fig-mpquic-data:
.. tikz:: Multipath QUIC uses the ``ACK_MP`` frame to acknowledge packets on each path. The ``ACK_MP`` frame can be sent on any path since it carries a path identifier.
   :libs: positioning, matrix, arrows, math


   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5; \max=10; }
   \tikzstyle{every node}=[font=\small]
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
	  
   \node [black, fill=white] at (\c1,\max) {Client};
   \node [black, fill=white] at (\s1,\max) {Server};
   
   \draw[black,thick,->] (\c1-0.5,\max-0.5) -- (\c1-0.5,0.5);
   \draw[red,dashed,thick,->] (\c1+0.5,\max-0.5) -- (\c1+0.5,0.5);
   \draw[black,thick,->] (\s1,\max-0.5) -- (\s1,0.5);
   \node [black, fill=white] at (\c1-0.5,\max-0.5) {$IP_{W}$};
   \node [red, fill=white] at (\c1+0.5,\max-0.5) {$IP_{C}$};
   \node [black, fill=white] at (\s1,\max-0.5) {$IP_{S}$};


   \tikzmath{\y=\max-1;}
   \node [black, fill=white, align=left] at (\c1-2, \y-0.5) {Wi-Fi path: $0:\alpha \rightarrow 0:\beta$\\Cell path: $1:\delta \rightarrow 2:\pi$};
   
   \node [black, fill=white, align=left] at (\s1+2, \y-0.5) {Wi-Fi path: $0:\beta \rightarrow 0:\alpha$\\Cell path: $2:\pi \rightarrow 2:\delta$};
   
   \draw[red,thick, ->] (\c1+0.5,\y-1) -- (\s1,\y-2) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\pi$\\PACKET($x$)};
   \draw[red,thick, -Rays] (\c1+0.5,\y-2) -- (\s1-1,\y-3) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\pi$\\PACKET($x+1$)};
   \draw[red,thick, ->] (\c1+0.5,\y-3) -- (\s1,\y-4) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\pi$\\PACKET($x+2$)};
   
   \draw[black,thick, ->] (\c1-0.5,\y-4) -- (\s1,\y-5) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\beta$\\PACKET($z$)};
   
   \draw[black,thick, ->] (\s1,\y-5) -- (\c1-0.5,\y-6) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_W$,DCID=$\alpha$\\PACKET[ACK\_MP(PNSI=2,lack=x+2,...)]};
   \draw[black,thick, ->] (\s1,\y-6) -- (\c1-0.5,\y-7) node [midway, align=center, fill=white]  {src=$IP_S$,dst=$IP_W$,DCID=$\alpha$\\PACKET[ACK\_MP(PNSI=0,lack=z,...)]};
   
   \draw[red,thick, ->] (\c1+0.5,\y-7) -- (\s1,\y-8) node [midway, align=center, fill=white]  {src=$IP_C$,dst=$IP_S$,DCID=$\pi$\\PACKET($x+3$)};
 

   
Multipath QUIC is still being discussed within the IETF. This section is likely to change in the coming months.

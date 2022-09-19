Multipath TCP implementations
*****************************

.. spelling::

   Costin
   Raiciu
   Sébastien
   Barré
   Grégory
   Detal
   Christoph
   Paasch
   

A transport protocol extension such as Multipath TCP is only useful once it has been implemented and starts to be used by applications. The first Multipath TCP implementation was developed Costin Raiciu in a user-space Linux stack :cite:`raiciu2011opportunistic`. In parallel, Sébastien Barré started to develop an in-kernel implementation :cite:`barre2011multipath`. This implementation evolved quickly with contributions from Christoph Paasch, Grégory Detal and many others :cite:`mptcp-kernel`. It has been described in more details in a USENIX NSDI paper :cite:`raiciu2012hard`. In parallel with this effort, Nigel Williams worked on Multipath TCP patches for FreeBSD :cite:`williams2014design`. Unfortunately, this effort has not resulted in a complete implementation and it has been discontinued. Apple has also developed a Multipath TCP implementation which is included in iOS and MacOS. This implementation supports both Multipath TCP version 0 :cite:`rfc6824` and Multipath TCP version 1 :cite:`rfc8684`.

As of this writing, there are currently two different Multipath TCP implementations in the Linux kernel. The first one is an off-tree patch which is mainly available for long-term support Linux kernels. It builds upon the earlier research prototypes :cite:`mptcp-kernel`, supports version 0 of Multipath TCP :cite:`rfc6824` and is available from http://www.multipath-tcp.org. The second implementation is a major rewrite that is included in Linux kernels from version 5.6 onward. This version is included in the official Linux kernel and is enabled by default by several popular Linux distributions. It supports version 1 of Multipath TCP :cite:`rfc8684`.




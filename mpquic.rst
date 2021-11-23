Multipath QUIC
**************

As the development of QUIC progressed within the IETF, academic researchers have started to explore how QUIC could be extended with multipath capabilities. The first approaches built upon Google's version of QUIC. The first prototype was implemented inside quic-go :cite:`de2017multipath`. A second version of the protocol which can be easily extended using plugins was then proposed inside picoquic :cite:`de2019pluginizing`. An alternative approach was proposed in :cite:`viernickel2018multipath`. The most recent solutions :cite:`de2021multiflow,zheng2021xlink` leverage the most recent QUIC specification as described in this document.

Discussions within the IETF took some time to start, despite early proposals :cite:`draft-deconinck-multipath-quic-00`. Recently, the QUIC working group adopted:cite:`draft-lmbdhk-quic-multipath` as a starting point for the development of an IETF specification for multipath QUIC. It combines the ideas initially proposed in three different drafts :cite:`draft-liu-multipath-quic,draft-deconinck-quic-multipath,draft-huitema-quic-mpath-option`.


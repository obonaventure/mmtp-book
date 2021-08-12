Basic principles of Multipath TCP
*********************************


Before looking at the main principles behind Multipath TCP, it is important to understand TCP in details.

.. tikz::
   :libs: positioning, matrix, arrows, math

   \tikzmath{\c1=1;\c2=1.5; \s1=8; \s2=8.5;}
   \colorlet{lightgray}{black!20}
   \tikzstyle{arrow} = [thick,->,>=stealth]
   \tikzset{state/.style={rectangle, dashed, draw, fill=white} }
   \node [blue, fill=white] at (1,10) {Client};
   \node [blue, fill=white] at (\s1-1,10) {Server};
   \draw[very thick,->] (\c1,9.5) -- (\c1,0.5);
   \draw[very thick,->] (\s1,9.5) -- (\s1,0.5);

   \draw[black,thick, ->] (\c1,9.5) -- (\s1,9) node [midway, fill=white] {SYN};
   \draw[black,thick, ->] (\s1,9) -- (\c1,8.5) node [midway, fill=white] {SYN+ACK};
   \draw[black,thick, ->] (\c1,8.5) -- (\s1,8) node [midway, fill=white] {ACK};

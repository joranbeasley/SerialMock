Serial Terminal Programs
------------------------

there are several utilities available for different os's. some of the big ones are

Windows Options
_______________

      - `TeraTerm <https://ttssh2.osdn.jp/index.html.en>`_ (more complex, lots of options... doesnt handle :code:`\r` linefeeds very well)
      - `DecaTerm <http://software.decagon.com/DecaTerm.exe>`_ (recommended if your device mostly communicates in ascii, very easy to use)

Linux Options
_____________

      - :code:`screen` is a built in pts communication application that works pretty well

          - :code:`screen /dev/ttyS0 9600` would open up a terminal to /dev/ttyS0 device at 9600 baud

      - :code:`cu` is another built in nix utility for communicating with a subshell

          - :code:`cu -l /dev/ttyS0 -s 9600` would open up a terminal to /dev/ttyS0 device at 9600 baud

      - :code:`minicom` is a more robust application designed for port communication in linux. invoke with :code:`minicom` and follow on screen menu system

      - `CuteCom <http://cutecom.sourceforge.net/>`_ a graphical cross platform serial terminal

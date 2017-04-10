TOOLS
=====

Setting up a Null Modem
-----------------------

Windows : com0com
__________________

Download one of the two versions below (I recommend using the signed version)

    - `Download official unsigned com0com <https://sourceforge.net/projects/com0com/>`_

       - *there is a readme with directions on how to self-sign the driver*

    - `Download signed com0com 2.2.0 drivers (recommended) <https://sourceforge.net/projects/com0com/files/com0com/2.2.2.0/>`_


In windows you need to create a null modem serial port.

the easiest (read cheapest) way to do this is using com0com, however there are many other options out there, simply google "windows null modem software", and you should be able to find many alternatives.




Linux : socat
_____________

Install socat with :code:`apt-get install socat`

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


serial_mock.cli Tool
--------------------

.. toctree::
   :maxdepth: 1

   cli_util
Tutorial
========

Getting Started
---------------

We will go ahead and mock a complete instrument in this tutorial. we will start by "cloning" our existing device using the `cli_util`

.. rubric:: PreRequisites



you must have already created a null modem and have taken notes of the names of both endpoints. I have chosen COM99 and COM100,
as my two endpoints using windows.

.. note::

   in linux your endpoints should look more like :code:`/dev/ttyS0`

   .. seealso::

      .. toctree::
         :maxdepth: 2

         nullmodem


.. rubric:: "Cloning" an existing device

1. connect your device to a comport and make note of its identifier (something like :code:`COM2` in windows and :code:`/dev/ttyUSB0` in unix-like systems.


2. run the following cli command :code:`python -m serial_mock.cli bridge COM2 COM99 -L output_file_name.data` this will create a bridge between COM2 and COM99, in this case COM2 is our device and COM99 is one end of our null modem


3. now connect up to the other end of our null modem (I am using COM100) (remember i bound to COM99 in the above command and my null modem pair is COM99 <-> COM100), using a serial terminal program of your choice

.. seealso::

   .. toctree::
      :maxdepth: 2

      teminalprogs


4. once connected send a series of commands you would like to clone, the input and output will be recorded into our :code:`output_file_name.data` file that we specified before


5. once you are done simple exit our command line cli instruction with :code:`ctrl+c`, we now have our logfile that will serve as the foundation of our cloned device


6. to convert it into a serial_mock object we will simply use our cli command to :code:`build` our instance, with :code:`python -m serial_mock.cli bridge output_file_name.data --out=MySer.py`

  - this will create a new file MySer.py that we can run to mimic our recorded device

7. Finally serve up our mocked device with :code:`python MySer.py COM99` which will serve our mocked port on the other half of the null modem (ie. connect to COM100 to interact with it)



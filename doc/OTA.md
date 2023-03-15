clone https://github.com/pycom/pycom-micropython-sigfox.git

"make" is used to build the components, or "gmake" on BSD-based systems.
You will also need bash and Python (at least 2.7 or 3.3).

The ESP32 version
-----------------

The "esp32" port requires an xtensa gcc compiler, which can be downloaded from
the Espressif website:

- for 64-bit Linux::

    https://dl.espressif.com/dl/xtensa-esp32-elf-linux64-1.22.0-80-g6c4433a-5.2.0.tar.gz

- for 32-bit Linux::

    https://dl.espressif.com/dl/xtensa-esp32-elf-linux32-1.22.0-80-g6c4433a-5.2.0.tar.gz

- for Mac OS:

    https://dl.espressif.com/dl/xtensa-esp32-elf-osx-1.22.0-80-g6c4433a-5.2.0.tar.gz

To use it, you will need to update your ``PATH`` environment variable in ``~/.bash_profile`` file. To make ``xtensa-esp32-elf`` available for all terminal sessions, add the following line to your ``~/.bash_profile`` file::

    export PATH=$PATH:$HOME/esp/xtensa-esp32-elf/bin

Alternatively, you may create an alias for the above command. This way you can get the toolchain only when you need it. To do this, add different line to your ``~/.bash_profile`` file::

    alias get_esp32="export PATH=$PATH:$HOME/esp/xtensa-esp32-elf/bin"

Then when you need the toolchain you can type ``get_esp32`` on the command line and the toolchain will be added to your ``PATH``.

You also need the ESP IDF along side this repository in order to build the ESP32 port.
To get it:

    $ git clone --recursive -b idf_v3.3.1 https://github.com/pycom/pycom-esp-idf.git

After cloning, if you did not specify the --recursive option, make sure to checkout all the submodules:

    $ cd pycom-esp-idf
    $ git submodule update --init


``` text
If you updated the repository from a previous revision and/or if switching between branches,<br>
make sure to also update the submodules with the command above.
```

Finally, before building, export the IDF_PATH variable

    $ export IDF_PATH=~/pycom-esp-idf

This repository contains submodules! Clone using the --recursive option:

    $ git clone --recursive https://github.com/pycom/pycom-micropython-sigfox.git

Alternatively checkout the modules manually:

    $ cd pycom-micropython-sigfox
    $ git submodule update --init

``` text
If you updated the repository from a previous revision and/or if switching between branches,<br>
make sure to also update the submodules with the command above.
```

Add any custom files you wish to access inside the firmware: esp32/frozen/Custom

Prior to building the main firmware, you need to build mpy-cross

	$ cd mpy-cross && make clean && make && cd ..

You can change the board type by using the BOARD variable:

    $ cd esp32
    $ make BOARD=GPY clean
    $ make BOARD=GPY
    $ make BOARD=GPY flash

To specify a serial port other than /dev/ttyUSB0, use ESPPORT variable:

    $ # On MacOS
    $ make ESPPORT=/dev/tty.usbserial-DQ008HQY flash
    $ # On Windows
    $ make ESPPORT=COM3 flash
    $ # On linux
    $ make ESPPORT=/dev/ttyUSB1 flash

Make sure that your board is placed into <b>programming mode</b>, otherwise <b>flashing will fail</b>.<br>
All boards except Expansion Board 2.0 will automatically switch into programming mode<br><br>
Expansion Board 2.0 users, please connect ``P2`` to ``GND`` and then reset the board.

LTE OTA Update
-----------------

 server directory

    |- OTA_server.py
    |- 1.0.0
    |  |- flash
    |  |   |- lib
    |  |- sd
    |- 1.0.1
    |  |- flash
    |  |   |- lib
    |  |- sd
    |- firmware_1.0.0.bin
    |- firmware_1.0.1.bin

In order to perform the update add the following.

    ota = LTEOTA(config.server_address_temp, config.server_port_temp)

    ota.update()


Make sure your file structure is like the one above.
Run the OTA_server.py inside a terminal.


    $python3 OTA_server.py

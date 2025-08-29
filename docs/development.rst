***********
Development
***********

In order to build the images, the following packages need to be installed on the system:
  - ``bsdtar`` (On debian, this is part of the `libarchive-tools`_ package)
  - ``xorriso``
  - ``qemu-system-x86``


Setup
#####

Create a virtual environment and install the builder using pip:

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip tox && pip install -e ".[dev]"


Basic Usage
###########

Generate the ISO with the following command:

.. code-block:: bash

   voraus-debian-iso build


..  _libarchive-tools: https://packages.debian.org/search?searchon=names&keywords=libarchive-tools

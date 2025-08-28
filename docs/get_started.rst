***********
Get started
***********

In order to build the images, the following packages need to be installed on the system:
  - ``bsdtar`` (On debian, this is part of the `libarchive-tools`_ package)
  - ``xorriso``
  - ``qemu-system-x86``


Installation
############

Install the builder using pip:

.. code-block:: bash

   pip install voraus-debian-iso


Basic Usage
###########

Generate the ISO with the following command:

.. code-block:: bash

   voraus-debian-iso build


..  _libarchive-tools: https://packages.debian.org/search?searchon=names&keywords=libarchive-tools

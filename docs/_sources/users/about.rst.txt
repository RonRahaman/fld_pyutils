About
=====

Fld Utils provides the means to read and write Nek5000 binary field data using NumPy arrays.
Furthermore, field data is managed to ensure consistency with minimal burden to the user.
This includes consistency between:
    * The header metadata.
    * The shapes of arrays for fields, coordinates, and element IDS.
    * The sizes and endianness of the numerical data types.

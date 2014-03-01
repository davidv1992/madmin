Conventions and structure of Madmin
===================================

Madmin is a system consisting of three layers:
  * Database 
  * Madmin core server
  * Madmin applications

Database
--------

The database itself is used only for data storage

Madmin core server
------------------

The primary task of the madmin core server is to maintain the internal state information stored in the database, providing checking for consistency, and provide access control for the various sources and combinations of sources of information. The end result is an easy to program agains interface of JSON objects over HTTP(S) that provide easy access to the various objects of the accounting system.

Madmin applications
-------------------

The madmin applications are user interfaces build upon the public API of the madmin core server. These are responsible for acting as end-points to user, implementing data entry capabilities and result presentation.


Representations of values
=========================

Representation of percentage defined values
-------------------------------------------

All values that represent percentages are internally stored as tenth's of a percent. This means that 1000 corresponds to 100%.

Representation of monetary values
---------------------------------

The madmin core does not associate a currency with a value, instead monetary values are represented internally in a fundamental unit, which we will call cents. Currency interpretation of these values is only done in Madmin applications.

All of the madmin user interface programs interpret monetary values as having associated currency Euro. In order to represent the euro's combination of complete euro's and cents internally all values are represented in cents whole cents. This allows use of an exact representation of the monetary values as integers and eliminates the arbitrary rounding implicit in floating point values.

Handling of BTW ammounts
------------------------

Every value that represents the price of an object internally is always the price including BTW.

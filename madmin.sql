-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 24, 2013 at 09:02 AM
-- Server version: 5.5.31
-- PHP Version: 5.4.6-1ubuntu1.2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `madmin`
--

-- --------------------------------------------------------

--
-- Table structure for table `tblboekjaar`
--

CREATE TABLE IF NOT EXISTS `tblboekjaar` (
  `bkjr_id` int(11) NOT NULL AUTO_INCREMENT,
  `bkjr_naam` text NOT NULL,
  `bkjr_is_huidig` tinyint(1) NOT NULL,
  PRIMARY KEY (`bkjr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblbudget`
--

CREATE TABLE IF NOT EXISTS `tblbudget` (
  `bdgt_id` int(11) NOT NULL AUTO_INCREMENT,
  `bdgt_naam` text NOT NULL,
  `bdgt_ver_id` int(11) NOT NULL,
  `bdgt_minimum` int(11) NOT NULL,
  `bdgt_current` int(11) NOT NULL,
  PRIMARY KEY (`bdgt_id`),
  KEY `bdgt_vrg_id` (`bdgt_ver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblfactuur`
--

CREATE TABLE IF NOT EXISTS `tblfactuur` (
  `fac_id` int(11) NOT NULL AUTO_INCREMENT,
  `fac_type` int(11) NOT NULL,
  `fac_ver_id` int(11) DEFAULT NULL,
  `fac_leverancier` text,
  `fac_volgnummer` int(11) NOT NULL,
  `fac_factuurdatum` date NOT NULL,
  `fac_leverdatum` date NOT NULL,
  `fac_verantwoordelijke` int(11) NOT NULL,
  `fac_saldo_speciaal` int(11) NOT NULL,
  `fac_saldo_basis` int(11) NOT NULL,
  `fac_saldo_speciaal_na` int(11) NOT NULL,
  `fac_saldo_basis_na` int(11) NOT NULL,
  PRIMARY KEY (`fac_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblproduct`
--

CREATE TABLE IF NOT EXISTS `tblproduct` (
  `prd_id` int(11) NOT NULL AUTO_INCREMENT,
  `prd_verwijderd` tinyint(1) NOT NULL,
  `prd_naam` text NOT NULL,
  `prd_type` int(11) NOT NULL,
  `prd_btw` int(11) NOT NULL,
  `prd_kantineprijs_leden` int(11) NOT NULL,
  `prd_kantineprijs_extern` int(11) NOT NULL,
  `prd_borrelmarge` int(11) NOT NULL,
  `prd_leverancier_id` text NOT NULL,
  `embalageprijs` int(11) NOT NULL,
  PRIMARY KEY (`prd_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblproductrelation`
--

CREATE TABLE IF NOT EXISTS `tblproductrelation` (
  `prdrel_id` int(11) NOT NULL AUTO_INCREMENT,
  `prdrel_orig_prd_id` int(11) NOT NULL,
  `prdrel_rel_prd_id` int(11) NOT NULL,
  `prdrel_aantal` int(11) NOT NULL,
  PRIMARY KEY (`prdrel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblvereniging`
--

CREATE TABLE IF NOT EXISTS `tblvereniging` (
  `ver_id` int(11) NOT NULL AUTO_INCREMENT,
  `ver_naam` text NOT NULL,
  `ver_email` text NOT NULL,
  PRIMARY KEY (`ver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `tblvoorraad`
--

CREATE TABLE IF NOT EXISTS `tblvoorraad` (
  `vrd_id` int(11) NOT NULL AUTO_INCREMENT,
  `vrd_prd_id` int(11) NOT NULL,
  `vrd_aantal` int(11) NOT NULL,
  `vrd_resterend` int(11) NOT NULL,
  `vrd_stukprijs` int(11) NOT NULL,
  `vrd_btw` int(11) NOT NULL,
  PRIMARY KEY (`vrd_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

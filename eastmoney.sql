/*
SQLyog Ultimate v8.32 
MySQL - 5.6.41 : Database - eastmoney
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`eastmoney` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `eastmoney`;

/*Table structure for table `expectValue` */

DROP TABLE IF EXISTS `expectValue`;

CREATE TABLE `expectValue` (
  `fundID` varchar(50) DEFAULT NULL,
  `scrawlDate` date DEFAULT NULL,
  `scrawlTime` time DEFAULT NULL,
  `expectUnitValue` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Table structure for table `jjjz_110003` */

DROP TABLE IF EXISTS `jjjz_110003`;

CREATE TABLE `jjjz_110003` (
  `FundDate` date NOT NULL,
  `netAssetValue` double DEFAULT NULL,
  PRIMARY KEY (`FundDate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

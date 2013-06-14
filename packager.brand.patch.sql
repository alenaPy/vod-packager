-- MySQL dump 10.13  Distrib 5.5.29, for Linux (x86_64)
--
-- Host: localhost    Database: packager
-- ------------------------------------------------------
-- Server version	5.5.29

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `Packager_app_customer_internal_brand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Packager_app_customer_internal_brand` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `internalbrand_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_id` (`customer_id`,`internalbrand_id`),
  KEY `Packager_app_customer_internal_brand_edc991fc` (`customer_id`),
  KEY `Packager_app_customer_internal_brand_ab76e5db` (`internalbrand_id`),
  CONSTRAINT `internalbrand_id_refs_id_d04a32b1` FOREIGN KEY (`internalbrand_id`) REFERENCES `Packager_app_internalbrand` (`id`),
  CONSTRAINT `customer_id_refs_id_c40f5632` FOREIGN KEY (`customer_id`) REFERENCES `Packager_app_customer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
    
--
-- Dumping data for table `Packager_app_customer_internal_brand`
--

LOCK TABLES `Packager_app_customer_internal_brand` WRITE;
/*!40000 ALTER TABLE `Packager_app_customer_internal_brand` DISABLE KEYS */;
/*!40000 ALTER TABLE `Packager_app_customer_internal_brand` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `Packager_app_internalbrand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Packager_app_internalbrand` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `format` varchar(2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Packager_app_internalbrand`
--

LOCK TABLES `Packager_app_internalbrand` WRITE;
/*!40000 ALTER TABLE `Packager_app_internalbrand` DISABLE KEYS */;
/*!40000 ALTER TABLE `Packager_app_internalbrand` ENABLE KEYS */;
UNLOCK TABLES;	

LOCK TABLES `Packager_app_item` WRITE;
ALTER TABLE `Packager_app_item` ADD COLUMN `internal_brand_id` int(11) NOT NULL;
ALTER TABLE `Packager_app_item` ADD KEY `Packager_app_item_f27d3eeb` (`internal_brand_id`);
ALTER TABLE `Packager_app_item` ADD CONSTRAINT `internal_brand_id_refs_id_2a06921b` FOREIGN KEY (`internal_brand_id`) REFERENCES `Packager_app_internalbrand` (`id`);
/*!40000 ALTER TABLE `Packager_app_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `Packager_app_item` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `Packager_app_renditionqueue` WRITE;
ALTER TABLE `Packager_app_renditionqueue` DROP COLUMN `local_svc_path`;
ALTER TABLE `Packager_app_renditionqueue` DROP COLUMN `svc_path`;
UNLOCK TABLES;

LOCK TABLES `Packager_app_path` WRITE;
ALTER TABLE `Packager_app_path` DROP INDEX `key`;
UNLOCK TABLES;




-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 27, 2020 at 02:12 AM
-- Server version: 10.1.38-MariaDB
-- PHP Version: 7.3.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `spectrumGrant`
--

-- --------------------------------------------------------

--
-- Table structure for table `grantLog`
--

CREATE TABLE `grantLog` (
  `grantLogID` int(10) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  `secondaryUserID` int(10) NOT NULL,
  `frequency` double NOT NULL,
  `bandwidth` double NOT NULL,
  `startTime` datetime NOT NULL,
  `endTime` datetime DEFAULT NULL,
  `status` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestMinFrequency` double NOT NULL,
  `requestMaxFrequency` double NOT NULL,
  `requestPreferredFrequency` double NOT NULL,
  `requestFrequencyAbsolute` tinyint(1) NOT NULL,
  `minBandwidth` double NOT NULL,
  `preferredBandwidth` double NOT NULL,
  `requestStartTime` datetime NOT NULL,
  `requestEndTime` datetime NOT NULL,
  `requestApproximateByteSize` double NOT NULL,
  `requestDataType` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestPowerLevel` double NOT NULL,
  `requestLocation` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestMobility` tinyint(1) NOT NULL,
  `requestMaxVelocity` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `grantLog`
--

INSERT INTO `grantLog` (`grantLogID`, `approved`, `secondaryUserID`, `frequency`, `bandwidth`, `startTime`, `endTime`, `status`, `requestMinFrequency`, `requestMaxFrequency`, `requestPreferredFrequency`, `requestFrequencyAbsolute`, `minBandwidth`, `preferredBandwidth`, `requestStartTime`, `requestEndTime`, `requestApproximateByteSize`, `requestDataType`, `requestPowerLevel`, `requestLocation`, `requestMobility`, `requestMaxVelocity`) VALUES
(1, 1, 1, 10000000, 908, '2019-12-06 08:00:00', '2019-12-06 11:00:00', 'DELETED', 90800000, 290000000, 897000000, 1, 300, 9567, '2019-12-06 07:00:00', '2019-12-06 12:00:00', 237980998, 'VIDEO', 90878, '23.3245, 12.3248907', 1, 55),
(2, 1, 1, 3890000, 908, '2019-12-06 08:00:00', '2019-12-06 11:00:00', 'TERMINATED', 500000000, 300000000, 897000000, 1, 9678, 9567, '2019-12-06 06:00:00', '2019-12-06 13:00:00', 23798, 'VIDEO', 349, '27.239048, 20.4398987932', 1, 55);

-- --------------------------------------------------------

--
-- Table structure for table `grantRequest`
--

CREATE TABLE `grantRequest` (
  `requestID` int(10) NOT NULL,
  `secondaryUserID` int(10) NOT NULL,
  `minFrequency` double NOT NULL,
  `maxFrequency` double NOT NULL,
  `preferredFrequency` double NOT NULL,
  `frequencyAbsolute` tinyint(1) NOT NULL,
  `minBandwidth` double NOT NULL,
  `preferredBandwidth` double NOT NULL,
  `startTime` datetime NOT NULL,
  `endTime` datetime DEFAULT NULL,
  `approximateByteSize` double NOT NULL,
  `dataType` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `powerLevel` double NOT NULL,
  `location` varchar(255) COLLATE utf8_bin NOT NULL,
  `mobility` tinyint(1) NOT NULL,
  `maxVelocity` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `grantRequest`
--

INSERT INTO `grantRequest` (`requestID`, `secondaryUserID`, `minFrequency`, `maxFrequency`, `preferredFrequency`, `frequencyAbsolute`, `minBandwidth`, `preferredBandwidth`, `startTime`, `endTime`, `approximateByteSize`, `dataType`, `powerLevel`, `location`, `mobility`, `maxVelocity`) VALUES
(1, 1, 35000000, 40000000, 35000000, 0, 300, 900, '2019-12-06 08:00:00', '2019-12-06 15:00:00', 1234567987, 'VIDEO', 9000, 'EARTH', 1, 55),
(3, 1, 35000000, 40000000, 35000000, 0, 300, 900, '2019-12-06 08:00:00', '2019-12-06 15:00:00', 1234567987, 'VIDEO', 9000, 'EARTH', 1, 55),
(4, 1, 35000000, 40000000, 35000000, 0, 300, 900, '2019-12-06 08:00:00', '2019-12-06 15:00:00', 1234567987, 'VIDEO', 9000, 'EARTH', 1, 55);

-- --------------------------------------------------------

--
-- Table structure for table `heartbeat`
--

CREATE TABLE `heartbeat` (
  `heartbeatID` int(10) NOT NULL,
  `grantID` int(10) NOT NULL,
  `heartbeatTime` datetime NOT NULL,
  `secondaryUserLocation` varchar(255) COLLATE utf8_bin NOT NULL,
  `secondaryUserVelocity` varchar(255) COLLATE utf8_bin NOT NULL,
  `heartbeatGrantStatus` varchar(255) COLLATE utf8_bin NOT NULL,
  `heartbeatBandwidth` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `heartbeat`
--

INSERT INTO `heartbeat` (`heartbeatID`, `grantID`, `heartbeatTime`, `secondaryUserLocation`, `secondaryUserVelocity`, `heartbeatGrantStatus`, `heartbeatBandwidth`) VALUES
(1, 1, '2019-12-06 01:00:00', '12.2134980, 33.1234897', '27', 'SUCCESS', 378);

-- --------------------------------------------------------

--
-- Table structure for table `node`
--

CREATE TABLE `node` (
  `nodeID` int(10) NOT NULL,
  `nodeName` varchar(255) COLLATE utf8_bin NOT NULL,
  `location` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `trustLevel` int(10) NOT NULL,
  `IPAddress` varchar(255) COLLATE utf8_bin NOT NULL,
  `minFrequency` double NOT NULL,
  `maxFrequency` double NOT NULL,
  `minSampleRate` double NOT NULL,
  `maxSampleRate` double NOT NULL,
  `nodeType` varchar(255) COLLATE utf8_bin NOT NULL,
  `mobility` tinyint(1) NOT NULL,
  `status` varchar(255) COLLATE utf8_bin NOT NULL,
  `comment` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `node`
--

INSERT INTO `node` (`nodeID`, `nodeName`, `location`, `trustLevel`, `IPAddress`, `minFrequency`, `maxFrequency`, `minSampleRate`, `maxSampleRate`, `nodeType`, `mobility`, `status`, `comment`) VALUES
(1, 'Test', '128.4432,23.123198', 3, 'ipatr', 16, 4000, 4, 80, 'VT-CRTS-Node', 1, 'INACTIVE', 'test comment'),
(2, 'Test', 'locationTest', 10, 'iPTEST', 1, 2, 3, 4, 'VT-CRTS-Node', 0, 'ACTIVE', 'none');

-- --------------------------------------------------------

--
-- Table structure for table `primaryUser`
--

CREATE TABLE `primaryUser` (
  `primaryUserName` varchar(255) COLLATE utf8_bin NOT NULL,
  `primaryUserID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `primaryUser`
--

INSERT INTO `primaryUser` (`primaryUserName`, `primaryUserID`) VALUES
('Joseph The PU', 1),
('UNKNOWN', 2);

-- --------------------------------------------------------

--
-- Table structure for table `primaryUserActivity`
--

CREATE TABLE `primaryUserActivity` (
  `PUActivityID` int(10) NOT NULL,
  `primaryUserID` int(10) NOT NULL,
  `frequency` int(11) NOT NULL,
  `bandwidth` double NOT NULL,
  `startTime` datetime NOT NULL,
  `endTime` datetime NOT NULL,
  `expectedEndTime` datetime NOT NULL,
  `location` varchar(255) COLLATE utf8_bin NOT NULL,
  `locationConfidence` float NOT NULL,
  `activityStatus` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `primaryUserActivity`
--

INSERT INTO `primaryUserActivity` (`PUActivityID`, `primaryUserID`, `frequency`, `bandwidth`, `startTime`, `endTime`, `expectedEndTime`, `location`, `locationConfidence`, `activityStatus`) VALUES
(2, 1, 23098, 908, '2019-12-06 08:00:00', '2019-12-06 11:00:00', '2019-12-06 03:00:00', '12.3245, 23.23134', 0.87, 'ACTIVE');

-- --------------------------------------------------------

--
-- Table structure for table `primaryUserLog`
--

CREATE TABLE `primaryUserLog` (
  `PULogID` int(10) NOT NULL,
  `primaryUserID` int(10) NOT NULL,
  `frequency` double NOT NULL,
  `bandwidth` double NOT NULL,
  `startTime` datetime NOT NULL,
  `endTime` datetime NOT NULL,
  `expectedEndTime` datetime NOT NULL,
  `location` varchar(255) COLLATE utf8_bin NOT NULL,
  `locationConfidence` float NOT NULL,
  `comment` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `primaryUserLog`
--

INSERT INTO `primaryUserLog` (`PULogID`, `primaryUserID`, `frequency`, `bandwidth`, `startTime`, `endTime`, `expectedEndTime`, `location`, `locationConfidence`, `comment`) VALUES
(1, 1, 234908, 239, '2019-12-06 08:00:00', '2019-12-06 11:00:00', '2019-12-06 03:00:00', '12.3424, 23.44566', 0.24, 'Hi');

-- --------------------------------------------------------

--
-- Table structure for table `secondaryUser`
--

CREATE TABLE `secondaryUser` (
  `secondaryUserID` int(10) NOT NULL,
  `secondaryUserEmail` varchar(255) COLLATE utf8_bin NOT NULL,
  `secondaryUserPassword` varchar(255) COLLATE utf8_bin NOT NULL,
  `secondaryUserName` varchar(255) COLLATE utf8_bin NOT NULL,
  `tier` int(11) NOT NULL,
  `nodeID` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `deviceID` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `location` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `secondaryUser`
--

INSERT INTO `secondaryUser` (`secondaryUserID`, `secondaryUserEmail`, `secondaryUserPassword`, `secondaryUserName`, `tier`, `nodeID`, `deviceID`, `location`) VALUES
(1, 'cam@fake.go', 'password', 'Cam Secondary User', 1, NULL, '2134897', 'UNKNOWN'),
(2, 'joseph@fake', 'password', 'joe', 2, '1', '2', '3,4'),
(3, 'password@fake', 'password', 'joseph', 2, '0', '0', ''),
(4, 'jtolley@vt.edu', 'password123', 'Joseph Tolley', 3, '0', '0', ''),
(5, 'fake@fake', 'pass', 'Joseph', 2, '0', '0', ''),
(6, 'cam@fake', 'pass', 'cam', 1, '0', '0', ''),
(7, 'fakeemail@fake', 'password', 'fake', 3, '0', '0', '0,0'),
(8, 'Time@fake', 'This', 'Last', 3, 'I', 'Do', '0,0');

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `adminID` int(10) NOT NULL,
  `adminEmail` varchar(255) COLLATE utf8_bin NOT NULL,
  `adminPassword` varchar(255) COLLATE utf8_bin NOT NULL,
  `adminName` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `secondaryUser`
--

INSERT INTO `admin` (`adminID`, `adminEmail`, `adminPassword`, `adminName`) VALUES
(1, 'admin@sas.com', 'admin', 'Administrator');

-- --------------------------------------------------------

--
-- Table structure for table `spectrumGrant`
--

CREATE TABLE `spectrumGrant` (
  `grantID` int(10) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  `secondaryUserID` int(10) NOT NULL,
  `frequency` double NOT NULL,
  `bandwidth` double NOT NULL,
  `startTime` datetime NOT NULL,
  `endTime` datetime DEFAULT NULL,
  `status` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestMinFrequency` double NOT NULL,
  `requestMaxFrequency` double NOT NULL,
  `requestPreferredFrequency` double NOT NULL,
  `requestFrequencyAbsolute` tinyint(1) NOT NULL,
  `minBandwidth` double NOT NULL,
  `preferredBandwidth` double NOT NULL,
  `requestStartTime` datetime NOT NULL,
  `requestEndTime` datetime NOT NULL,
  `requestApproximateByteSize` double NOT NULL,
  `requestDataType` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestPowerLevel` double NOT NULL,
  `requestLocation` varchar(255) COLLATE utf8_bin NOT NULL,
  `requestMobility` tinyint(1) NOT NULL,
  `requestMaxVelocity` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `spectrumGrant`
--

INSERT INTO `spectrumGrant` (`grantID`, `approved`, `secondaryUserID`, `frequency`, `bandwidth`, `startTime`, `endTime`, `status`, `requestMinFrequency`, `requestMaxFrequency`, `requestPreferredFrequency`, `requestFrequencyAbsolute`, `minBandwidth`, `preferredBandwidth`, `requestStartTime`, `requestEndTime`, `requestApproximateByteSize`, `requestDataType`, `requestPowerLevel`, `requestLocation`, `requestMobility`, `requestMaxVelocity`) VALUES
(0, 1, 1, 23400000, 234, '2020-02-21 04:21:00', '2020-02-28 00:12:00', 'PENDING', 23849000, 143092000, 41283000, 1, 500, 800, '2020-02-21 00:00:00', '2020-02-28 00:00:00', 3456, 'VIDEO', 23, '23.231456,-87.13245', 1, 23),
(1, 1, 1, 567000000, 234, '2020-02-21 04:21:00', '2020-02-28 00:12:00', 'PENDING', 23849000, 143092000, 41283000, 1, 500, 800, '2020-02-21 00:00:00', '2020-02-28 00:00:00', 3456, 'VIDEO', 23, '23.231456,-87.13245', 1, 23);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `grantLog`
--
ALTER TABLE `grantLog`
  ADD PRIMARY KEY (`grantLogID`);

--
-- Indexes for table `grantRequest`
--
ALTER TABLE `grantRequest`
  ADD PRIMARY KEY (`requestID`);

--
-- Indexes for table `heartbeat`
--
ALTER TABLE `heartbeat`
  ADD PRIMARY KEY (`heartbeatID`);

--
-- Indexes for table `node`
--
ALTER TABLE `node`
  ADD PRIMARY KEY (`nodeID`);

--
-- Indexes for table `primaryUser`
--
ALTER TABLE `primaryUser`
  ADD PRIMARY KEY (`primaryUserID`);

--
-- Indexes for table `primaryUserActivity`
--
ALTER TABLE `primaryUserActivity`
  ADD PRIMARY KEY (`PUActivityID`);

--
-- Indexes for table `primaryUserLog`
--
ALTER TABLE `primaryUserLog`
  ADD PRIMARY KEY (`PULogID`);

--
-- Indexes for table `secondaryUser`
--
ALTER TABLE `secondaryUser`
  ADD PRIMARY KEY (`secondaryUserID`);

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`adminID`);

--
-- Indexes for table `spectrumGrant`
--
ALTER TABLE `spectrumGrant`
  ADD PRIMARY KEY (`grantID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `grantRequest`
--
ALTER TABLE `grantRequest`
  MODIFY `requestID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `heartbeat`
--
ALTER TABLE `heartbeat`
  MODIFY `heartbeatID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `node`
--
ALTER TABLE `node`
  MODIFY `nodeID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `primaryUser`
--
ALTER TABLE `primaryUser`
  MODIFY `primaryUserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `primaryUserActivity`
--
ALTER TABLE `primaryUserActivity`
  MODIFY `PUActivityID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `primaryUserLog`
--
ALTER TABLE `primaryUserLog`
  MODIFY `PULogID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `secondaryUser`
--
ALTER TABLE `secondaryUser`
  MODIFY `secondaryUserID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

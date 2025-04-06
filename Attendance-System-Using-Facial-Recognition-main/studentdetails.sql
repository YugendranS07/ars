-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 06, 2025 at 03:19 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `login`
--

-- --------------------------------------------------------

--
-- Table structure for table `studentdetails`
--

CREATE TABLE `studentdetails` (
  `student_id` varchar(255) NOT NULL,
  `student_name` varchar(255) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `class` varchar(50) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `parent_email` varchar(255) DEFAULT NULL,
  `remarks` varchar(10) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `studentdetails`
--

INSERT INTO `studentdetails` (`student_id`, `student_name`, `gender`, `class`, `section`, `parent_email`, `remarks`) VALUES
('121', 'da', 'Male', '12', '12', 'john123@gmail.com', '0'),
('129', 'anbu', 'Male', 'bsc', 'c', 'maheshanbu246@gmail.com', '0'),
('200', 'mahesh', 'Male', 'msc', 'b', 'mage@gmail.com', '0'),
('47', 'mahesh', 'Male', 'msc', 'b', 'mahe@gmail.com', '0'),
('NDJ898', 'mahesh123', 'Female', 'dss', 'sec', 'sidybsidi@gmail.com', '0'),
('RA025', 'Yugendran', 'Male', 'VBA', 'A', 'syugendran07@gmail.com', '0');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `studentdetails`
--
ALTER TABLE `studentdetails`
  ADD PRIMARY KEY (`student_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

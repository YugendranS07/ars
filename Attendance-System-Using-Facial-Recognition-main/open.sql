-- student form -> adding students
CREATE TABLE `student` (
  `id` int(11) AUTO_INCREMENT PRIMARY KEY,
  `firstName` varchar(100) NOT NULL,
  `lastName` varchar(100) NOT NULL,
  `email` varchar(100) UNIQUE NOT NULL,
  `password` text NOT NULL,
  `birthday` date NOT NULL,
  `gender` varchar(10) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `address` varchar(100) DEFAULT NULL,
  `class` varchar(100) NOT NULL,
  `dept` varchar(100) NOT NULL,
  `pic` text NOT NULL,
   marks varchar(255) DEFAULT 'Absent',
    dateofmark date,
    timeofmark time
) ;
-- dummy values
Insert Into student values('',"yugendran","s","syud@gmail.com","pwd","2002-02-02","male","80980","sfdf","A","BCA","dsd","Present","2022-11-29","07:08:23");
Insert Into student values('',"kumar","s","syuiud@gmail.com","pwd","2002-02-02","male","80980","sfdf","B","BCA","dsd","ABSENT","2022-11-29","07:08:23");
Insert Into student values('',"ravi","s","syui89ud@gmail.com","pwd","2002-02-02","female","80980","sfdf","A","BSC","dsd","ABSENT","2022-11-29","07:08:23");
CREATE TABLE attendance (
   `id` int(11) AUTO_INCREMENT PRIMARY KEY,
    name varchar(255) NOT NULL,
    marks varchar(255) DEFAULT 'Absent',
    dateofmark date,
    timeofmark time
);
UPDATE attendance SET dateofmark = DATE_FORMAT(dateofmark,'%d-%m-%Y');
-- selecting id algorithm

    -- uname = name.spilt(" ")
    -- x=name.split(" ")
    -- fname=""
    -- for i in range(0,len(x)-1):
    --    fname = fname+" "+x[i]
    -- lname = x[len(x)-1]
<?php
$connect = mysqli_connect("localhost", "root","");
mysqli_query($connect,"Create database IF NOT EXISTS PiCrypt");
mysqli_select_db($connect,"PiCrypt") or die("can not select database");
$sql="create table IF NOT EXISTS user("."id int(11) AUTO_INCREMENT PRIMARY KEY,"."name text NOT NULL unique,"."password varchar(100) NOT NULL)";
mysqli_query($connect,$sql);
?>
<?php
$serverName = "LAPTOP-77204R0A\\SQLEXPRESS"; // Your SQL Server name
$connectionOptions = array(
    "Database" => "FormVisitors",
    "UID" => "", // Leave blank for Windows Authentication
    "PWD" => ""  // Leave blank for Windows Authentication
);

// Establishes the connection
$conn = sqlsrv_connect($serverName, $connectionOptions);

// Check connection
if ($conn === false) {
    die("Connection failed: " . print_r(sqlsrv_errors(), true));
}
?>

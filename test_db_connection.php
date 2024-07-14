<?php
include 'forms/db_connection.php';

$sql = "SELECT ManagerID, Name FROM Managers";
echo "Running query: $sql<br>";

$stmt = sqlsrv_query($conn, $sql);

if ($stmt === false) {
    echo "Query error: " . print_r(sqlsrv_errors(), true);
} else {
    $row_count = 0;
    while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
        $row_count++;
        echo "ID: " . $row["ManagerID"] . " - Name: " . $row["Name"] . "<br>";
    }
    if ($row_count === 0) {
        echo "0 results";
    } else {
        echo "Number of results: $row_count";
    }
    sqlsrv_free_stmt($stmt);
}
sqlsrv_close($conn);
?>

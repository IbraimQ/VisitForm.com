<?php
include 'db_connection.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Process form data and insert into the database
    $visitorCount = $_POST['visitor-count'];
    $date = $_POST['date'];
    $managerID = $_POST['manager'];

    for ($i = 1; $i <= $visitorCount; $i++) {
        $name = $_POST["name$i"];
        $phone = $_POST["phone$i"];
        $email = $_POST["email$i"];
        $id = $_POST["id$i"];
        $file = $_FILES["file$i"]['name'];

        // SQL query to insert visitor data
        $sql = "INSERT INTO Visitors (Name, ContactInfo, DateOfVisit) VALUES (?, ?, ?)";
        $params = array($name, $phone, $date);
        sqlsrv_query($conn, $sql, $params);

        // Get the last inserted visitor ID
        $visitorID = sqlsrv_query($conn, "SELECT SCOPE_IDENTITY() AS VisitorID");
        $visitorID = sqlsrv_fetch_array($visitorID)['VisitorID'];

        // Insert visit details
        $sql = "INSERT INTO Visits (VisitorID, ManagerID, VisitDate, ApprovalStatus) VALUES (?, ?, ?, ?)";
        $params = array($visitorID, $managerID, $date, 'Pending');
        sqlsrv_query($conn, $sql, $params);
    }

    echo "Form submitted successfully!";
} else {
    echo "Invalid request method.";
}
?>
s
<html>
<head>
<title>DB2S3</title>

<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
<meta http-equiv="refresh" content="15" >

<?php
if(isset($_POST['status'])){
//move this after the SQL bits
If( intval($_POST['status']) == 0){
//Echo '<meta http-equiv="refresh" content="5" >';
}}
?>
</head>
<body>

<?php

$servername = "";
$username = "";
$password = "";
$dbname = "";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if(isset($_POST['status'])){
$status = intval($_POST['status']);
$sql = "UPDATE PROCESS_LOCK SET LOCKED = " . $status;
$conn->query($sql);
}

$sql = "SELECT LOCKED FROM PROCESS_LOCK";
$sysStatus = $conn->query($sql);
$sysStatus = $sysStatus->fetch_assoc();

$sql = "SELECT COUNT(1) AS PENDING FROM db2s3 WHERE S3_UPLOADED IS NULL";
$pending = $conn->query($sql);
$pending = $pending->fetch_assoc();

$sql = "SELECT FILENAME, DROPBOX_DOWNLOADED, S3_UPLOADED FROM db2s3 ORDER BY S3_UPLOADED DESC LIMIT 10";
$result = $conn->query($sql);

$sql = "SELECT S3_UPLOADED AS LAST FROM db2s3 WHERE S3_UPLOADED IS NOT NULL ORDER BY S3_UPLOADED DESC LIMIT 1";
$lastsync = $conn->query($sql);
$lastsync = $lastsync->fetch_assoc();

//$sql = "SELECT S3_OBJECTS_CURRENT, S3_SIZE_CURRENT / 1073741824 AS S3_SIZE_CURRENT FROM QUANTITY_VOLUME WHERE ID = 1";
$sql = "SELECT SUM(BYTES)/1073741824 AS S3_SIZE_CURRENT, COUNT(1) AS S3_OBJECTS_CURRENT FROM db2s3";
$quanvol = $conn->query($sql);
$quanvol = $quanvol->fetch_assoc();

$sql = "SELECT PATH, DROPBOX_DOWNLOADED FROM db2s3 WHERE S3_UPLOADED IS NULL ORDER BY DROPBOX_DOWNLOADED DESC LIMIT 10";
$resPending = $conn->query($sql);
$conn->close();
?>

<table align="center" width="50%">
<tr>
<td align="center">
<h2>System Status:</h2>
</td>
</tr>
<tr>
<td align="center">
<form action="" method="post">
<select name='status' onchange='this.form.submit()'>
  <option value="0" <?php if ($sysStatus["LOCKED"] == 0) : ?> selected <?php endif; ?>>Live</option>
  <option value="1" <?php if ($sysStatus["LOCKED"] == 1) : ?> selected <?php endif; ?>>Disabled</option>
</select>
<noscript><input type="submit" value="Submit"></noscript>
</form>
</td>
</tr>
</table>
</form>

<?php
$formattedNum = number_format($pending["PENDING"]);

echo '<h4>' . $formattedNum . ' uploads pending' . '</h4>';
echo '<h4> Last sync: ' . $lastsync["LAST"] . '</h4>';
echo '<h4> S3 size: ' . number_format($quanvol["S3_SIZE_CURRENT"], 2, '.', ',') . ' GB</h4>';
echo '<h4> S3 objects: ' . number_format($quanvol["S3_OBJECTS_CURRENT"]) . '</h4>';

if ($resPending) {
  echo '<br>
<h2>Last 10 files pending:</h2>
<table class="table table-striped table-bordered table-condensed">
<thead>
      <tr>
        <th class="col-xs-6 col-sm-4" style="text-align:center">Path</th>
        <th class="col-xs-6 col-sm-4" style="text-align:center">Identified in Dropbox</th>
      </tr>
    </thead>
    <tbody>
';

while($row = $resPending->fetch_assoc()) {
    // Each $row is a row from the query
    echo '<tr>';
    echo '<td>' . $row["PATH"] . '</td>';
    echo '<td>' . $row["DROPBOX_DOWNLOADED"] . '</td>';
    echo '</tr>';
  }
  echo '</table>';
}

if ($result) {
  echo '<br>
<h2>Last 10 files synced:</h2>
<table class="table table-striped table-bordered table-condensed">
<thead>
      <tr>
        <th class="col-xs-6 col-sm-4" style="text-align:center">Filename</th>
        <th class="col-xs-6 col-sm-4" style="text-align:center">Identified in Dropbox</th>
        <th class="col-xs-6 col-sm-4" style="text-align:center">Uploaded to S3</th>
      </tr>
    </thead>
    <tbody>
';

while($row = $result->fetch_assoc()) {
    // Each $row is a row from the query
    echo '<tr>';
    echo '<td>' . $row["FILENAME"] . '</td>';
    echo '<td>' . $row["DROPBOX_DOWNLOADED"] . '</td>';
    echo '<td>' . $row["S3_UPLOADED"] . '</td>';
    echo '</tr>';
  }
  echo '</table>';
}

die();
?>

</body>
</html>

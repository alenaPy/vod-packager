<?php
$targetFile = "MIKESDIRTYMOVIE_PI17-ES-SO.jpg";
$extension = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));
$fileName = basename($targetFile, ".".$extension);
$pos = strrpos($fileName, "_");
if ($pos > 0) {
	$suffix = substr($fileName, $pos);
}

$db_host = "localhost";
$db_user = "root";
$db_pass = "ard010fx";
//$imageProfileEntry = getImageProfileId($db_host, $db_user, $db_pass, $suffix, $extension);
//$imageProfileId = $imageProfileEntry['id'];
$imageProfileId = getImageProfileId($db_host, $db_user, $db_pass, $suffix, $extension);
$itemId = 1; //este valor deberia sacarse del contexto
echo "IMGPROID: ".$imageProfileId."\n";

// ISSUE: Usar la funcion dbConnection y hacer una sola conexion a la base de datos.

if (updateImageRendition($db_host, $db_user, $db_pass, $itemId, $imageProfileId, $fileName)) {
	echo "LO ENCONTRE";
} else {
	echo "NO LO ENCONTRE";
}

function dbConnection($db_host, $db_user, $db_pass) {
mysql_connect($db_host, $db_user, $db_pass) or die ("Cant Connect to DB");
@mysql_select_db("packager") or die( "Unable to select database");
return true;
}

function getImageProfileId($db_host, $db_user, $db_pass, $suffix, $ext) {

    $query = "SELECT id 
		  FROM Packager_app_imageprofile 
		  WHERE file_extension =\"".$ext."\" AND sufix=\"".$suffix."\" LIMIT 1;";
	
	echo $query."\n";

    mysql_connect($db_host, $db_user, $db_pass) or die ("Cant Connect to DB");
    @mysql_select_db("packager") or die( "Unable to select database");

    $result = mysql_query($query);
    // Check result
    // This shows the actual query sent to MySQL, and the error. Useful for debugging.
    if (!$result) {
	echo "Nada";
        $message  = 'Invalid query: ' . mysql_error() . "\n";
        $message .= 'Whole query: ' . $query;
        die($message);
    }
    mysql_close();
    $row = mysql_fetch_assoc($result);
    return $row['id'];
}

function updateImageRendition($db_host, $db_user, $db_pass, $item_id, $profile_id, $filename) {
	
	/*
	$query = "UPDATE Packager_app_imagerendition 
			SET file_name=\"".$filename."\", status=\"F\" 
			WHERE image_profile_id =".$profile_id." AND item_id=".$item_id." AND file_name=\"\" AND status=\"U\" LIMIT 1;";
	*/
	$query = "UPDATE Packager_app_imagerendition 
                        SET file_name=\"".$filename."\", status=\"F\" 
                        WHERE image_profile_id =".$profile_id." AND item_id=".$item_id." AND status=\"U\" LIMIT 1;";
	echo $query."\n";

    mysql_connect($db_host, $db_user, $db_pass) or die ("Cant Connect to DB");
    @mysql_select_db("packager") or die( "Unable to select database");

    $result = mysql_query($query);
    // Check result
    // This shows the actual query sent to MySQL, and the error. Useful for debugging.
    if (!$result) {
        $message  = 'Invalid query: ' . mysql_error() . "\n";
        $message .= 'Whole query: ' . $query;
        die($message);
    }
    mysql_close();
	if ($result) {
		//$row = mysql_affected_rows($result);
		//$row = mysqli_fetch_row ( $result );
		    return true;
	} else {
		return false;
	}
}

?>

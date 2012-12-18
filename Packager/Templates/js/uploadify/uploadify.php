<?php

if (!empty($_FILES)) {
	// Database info
	$db_host = "localhost";
	$db_user = "root";
	$db_pass = "ard010fx";
	$db_name = "packager";
	$link = connectToDatabase($db_host, $db_user, $db_pass, $db_name);
	// Item info
	$itemId = $_GET["item_id"];
	// Uploaded file info
	$tempFile = $_FILES['Filedata']['tmp_name'];
	$targetFolder = getTargetFolder($link);
//echo "FOLDER: ".$targetFolder."\n";
	$targetFile = $targetFolder . '/' . $_FILES['Filedata']['name'];
	//$targetFile = "MIKESDIRTYMOVIE_PI17-ES-SO.jpg";
//echo "FILE: ".$targetFile."\n";
	$fileTypes = array('jpg','jpeg','gif','png'); // File extensions
	$fileParts = pathinfo($_FILES['Filedata']['name']);
	$fileExtension = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));
//echo "EXTENSION: ".$fileExtension."\n";
	$fileName = basename($targetFile, ".".$fileExtension);
	$pos = strrpos($fileName, "_");
	if ($pos > 0) {
		$fileSuffix = substr($fileName, $pos);
//echo "SUFFIX: ".$fileSuffix."\n";
	} else {
		// hay que trapear el error y no tificarlo por pantalla
	}
	// Processing file parts
	if (in_array($fileParts['extension'],$fileTypes)) {
		move_uploaded_file($tempFile,$targetFile);
		// Update image rendition entry
		processImageRendition($link, $itemId, $fileName, $fileExtension, $fileSuffix);
	} else {
		echo 'Invalid file type.';
	}
	disconnectFromDatabase($link);
}


function connectToDatabase($db_host, $db_user, $db_pass, $db_name) {

	$link = mysqli_connect($db_host, $db_user, $db_pass, $db_name);
	/* check connection */
	if (mysqli_connect_errno()) {
		printf("Connect failed: %s\n", mysqli_connect_error());
		exit();
	} else {
		return $link;
	}
}

function disconnectFromDatabase($link) {
	mysqli_close($link);
}

function getTargetFolder($link) {

	$query = "SELECT location FROM Packager_app_path WHERE Packager_app_path.key='image_local_path';";
//echo $query."\n";
	/* Select queries return a resultset */
	if ($result = mysqli_query($link, $query)) {
		$row = mysqli_fetch_assoc($result);
		/* free result set */
		mysqli_free_result($result);
		return $row['location'];
	}
}

function processImageRendition($link, $itemId, $fileName, $fileExtension, $fileSuffix) {

	$imageProfileId = getImageProfileId($link, $fileExtension, $fileSuffix);
//echo "IMAGE PROFILE: ".$imageProfileId."\n";
	if (updateImageRendition($link, $itemId, $imageProfileId, $fileName.".".$fileExtension)) {
		echo "LO ENCONTRE";
	} else {
		echo "NO LO ENCONTRE";
	}
}

function getImageProfileId($link, $fileExtension, $fileSuffix) {

	$query = "SELECT id 
			FROM Packager_app_imageprofile 
			WHERE file_extension =\"".$fileExtension."\" AND sufix=\"".$fileSuffix."\" LIMIT 1;";
//echo $query."\n";
	/* Select queries return a resultset */
	if ($result = mysqli_query($link, $query)) {
		$row = mysqli_fetch_assoc($result);
		/* free result set */
		mysqli_free_result($result);
		return $row['id'];
	}
}

function updateImageRendition($link, $itemId, $imageProfileId, $fileName) {

	$query = "UPDATE Packager_app_imagerendition 
			SET file_name=\"".$fileName."\", status=\"F\" 
			WHERE image_profile_id =".$imageProfileId." AND item_id=".$itemId." AND status=\"U\" LIMIT 1;";
//echo $query."\n";
	/* If we have to retrieve large amount of data we use MYSQLI_USE_RESULT */
	if ($result = mysqli_query($link, $query, MYSQLI_USE_RESULT)) {
		return true;
		mysqli_free_result($result);
	} else {
		return false;
	}
}

?>

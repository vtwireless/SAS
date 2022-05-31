<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: * ");
header("Access-Control-Allow-Headers: Content-Type");
   //include '../incSAS/database.php';
   include 'database.php';
   $connection = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD);
   if (mysqli_connect_errno()){
     echo "Failed to connect to MySQL: " . mysqli_connect_error();
   }
   $database = mysqli_select_db($connection, DB_DATABASE);
	//$result = NULL;
   $exists = 0;
   $valid = 1;
   $lower_case = "abcdefghijklmnopqrstuvwxyz";
   $upper_case = strtoupper($lower_case);
   $numbers = "0123456789";
   $dashes = "_-";
   $allowed = $lower_case.$upper_case.$numbers.$dashes;
   date_default_timezone_set('America/New_York');
   //session_start();

   if ($_SERVER["REQUEST_METHOD"] == "POST") {
   	$action = $_POST['action'];
   	if ($action == "createSU"){

   		$secondaryUserName = $_POST['secondaryUserName'];
       $secondaryUserEmail = strtolower($_POST['secondaryUserEmail']);
       $secondaryUserPassword = $_POST['secondaryUserPassword'];
       $deviceID = $_POST['deviceID'];
       $location = $_POST['location'];


       if ($secondaryUserEmail == "" || $secondaryUserPassword == "" || $secondaryUserName == ""){
         $valid = 0;
       }
       if($valid == 1){
         $result = mysqli_query($connection, "SELECT * FROM secondaryUser WHERE secondaryUserEmail = '$secondaryUserEmail'");
         while ($row = mysqli_fetch_array($result)) {
          $exists = 1;
        }	  			
        if($exists == 0){
         $sql = "INSERT INTO secondaryUser (secondaryUserEmail, secondaryUserPassword, secondaryUserName, deviceID, location, tier)
         VALUES ('$secondaryUserEmail', '$secondaryUserPassword', '$secondaryUserName', '$deviceID', '$location', '3');";

         if (mysqli_query($connection, $sql)) {
           $m['status'] = 1;
           $m['message'] = "New record created successfully";
           echo json_encode($m);
         }
         else {
          $m['message'] = "Error: " . $sql . "<br>" . mysqli_error($connection);
          $m['status'] = 0;
          echo json_encode($m);
        }
      }
      else if ($exists == 1){
       $m['exists'] = 1;
       $m['status'] = 0;
       $m['message'] = 'Email In Use';
       echo json_encode($m);
     }
   }
   else{
    $m['status'] = 0;
    $m['message'] = 'Invalid API Call';
    echo json_encode($m);
  }
}

if ($action == "updateSASSettings"){  
  $algorithm = strtoupper($_POST['algorithm']); 
  $heartbeatInterval = $_POST['heartbeatInterval'];
  $rem = $_POST['REMAlgorithm'];
  if ($algorithm == "" || $heartbeatInterval == "" || $rem == ""){
    $valid = 0;
  }
  if($valid == 1){
    $sql = "UPDATE SASSettings SET algorithm = '$algorithm', heartbeatInterval = '$heartbeatInterval, REMAlgorithm = '$rem' WHERE 1 LIMIT 1;";

    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Settings updated successfully";
     $m['ext'] = $sql;
     echo json_encode($m);
   } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
   }



 }
 else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}


if ($action == "checkEmailAvail"){

 $email = strtolower($_POST['email']);


 if ($email == ""){
   $valid = 0;
 }
 if($valid == 1){
  $result = mysqli_query($connection, "SELECT * FROM secondaryUser WHERE secondaryUserEmail = '$email'");
  while ($row = mysqli_fetch_array($result)) {
    $exists = 1;
  }           
  if ($exists == 1){
   $m['exists'] = 1;
   $m['status'] = 1;
   $m['message'] = 'Email In Use';
   echo json_encode($m);
 }
 else{
   $m['exists'] = 0;
   $m['status'] = 1;
   $m['message'] = 'Email Unique';
   echo json_encode($m);

 }
}
else{
  $m['status'] = 0;
  $m['message'] = 'Invalid check emailAPI Call';
  echo json_encode($m);
}
}

if ($action == "createGrantRequest"){
  $secondaryUserID = $minFrequency = $maxFrequency = $preferredFrequency = $frequencyAbsolute = $minBandwidth = $preferredBandwidth = $startTime = $endTime = $approximateByteSize = $dataType = $powerLevel = $location = $mobility = $maxVelocity = "";
  if ( isset($_POST['secondaryUserID'])) {
   $secondaryUserID = $_POST['secondaryUserID'];
 }
 if ( isset($_POST['minFrequency'])) {
   $minFrequency = $_POST['minFrequency'];
 }
 if ( isset($_POST['maxFrequency'])) {
   $maxFrequency = $_POST['maxFrequency'];
 }
 if ( isset($_POST['preferredFrequency'])) {
   $preferredFrequency = $_POST['preferredFrequency'];
 }
 if ( isset($_POST['frequencyAbsolute'])) {
   $frequencyAbsolute = $_POST['frequencyAbsolute'];
 }
 if ( isset($_POST['minBandwidth'])) {
   $minBandwidth = $_POST['minBandwidth'];
 }
 if ( isset($_POST['preferredBandwidth'])) {
   $preferredBandwidth = $_POST['preferredBandwidth'];
 }
 if ( isset($_POST['startTime'])) {
   $startTime = $_POST['startTime'];
 } else {
  $startTime = date("Y-m-d H:i:s");
}
if ( isset($_POST['endTime'])) {
 $endTime = $_POST['endTime'];
}
if ( isset($_POST['approximateByteSize'])) {
 $approximateByteSize = $_POST['approximateByteSize'];
}
if ( isset($_POST['dataType'])) {
 $dataType = $_POST['dataType'];
}
if ( isset($_POST['powerLevel'])) {
 $powerLevel = $_POST['powerLevel'];
}
if ( isset($_POST['location'])) {
 $location = $_POST['location'];
}
if ( isset($_POST['mobility'])) {
 $mobility = $_POST['mobility'];
} else {
  $mobility = 0;
}
if ( isset($_POST['maxVelocity'])) {
 $maxVelocity = $_POST['maxVelocity'];
} else {
  $maxVelocity = 0;
}


if ($secondaryUserID == "" || $minFrequency == "" || $maxFrequency == "" || $minBandwidth == "" || $powerLevel == ""){
 $valid = 0;
}
if($valid == 1){
  $result = mysqli_query($connection, "SELECT * FROM grantRequest WHERE secondaryUserID = '$secondaryUserID' AND minFrequency = '$minFrequency' AND startTime = '$startTime'");
  while ($row = mysqli_fetch_array($result)) {
    $exists = 1;
  }           
  if($exists == 0){
   $sql = "INSERT INTO grantRequest (secondaryUserID, minFrequency, maxFrequency, preferredFrequency, frequencyAbsolute, minBandwidth, preferredBandwidth, startTime, endTime, approximateByteSize, dataType, powerLevel, location, mobility, maxVelocity)
   VALUES ('$secondaryUserID', '$minFrequency', '$maxFrequency', '$preferredFrequency', '$frequencyAbsolute', '$minBandwidth', '$preferredBandwidth', '$startTime', '$endTime', '$approximateByteSize', '$dataType', '$powerLevel', '$location', '$mobility', '$maxVelocity');";

   if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Grant request created successfully";
     echo json_encode($m);
   }
   else {
    $m['message'] = "Error: " . $sql . "<br>" . mysqli_error($connection);
    $m['status'] = 0;
    echo json_encode($m);
  }
} else {
  $m['status'] = 0;
  $m['message'] = 'grant already exists';
  echo json_encode($m);
}
}
else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}

if ($action == "SULogin"){
 $username = $password = "";

 $username = $_POST['username'];
 $password = $_POST['password'];
 if ($username == "" || $password == ""){
   $valid = 0;
 }
 if($valid == 1){
   $result = mysqli_query($connection, "SELECT * FROM secondaryUser WHERE secondaryUserEmail = '$username' AND secondaryUserPassword = '$password';");
   while ($row = mysqli_fetch_array($result)) {
    $exists = 1;
    $rowa['id'] = $row['secondaryUserID'];
    $rowa['userType'] = 'SU';
    $rowa['name'] = $row['secondaryUserName'];
    $rowa['status'] = 1;
  }	  			
  if($exists == 0){
    $rowa['status'] = 0;
  }
  echo json_encode($rowa);


}
else{
	$m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}


   	/////

if ($action == "adminLogin"){
 $username = $password = "";

 $username = $_POST['username'];
 $password = $_POST['password'];
 if ($username == "" || $password == ""){
   $valid = 0;
 }
 if($valid == 1){
   $result = mysqli_query($connection, "SELECT * FROM admin WHERE adminEmail = '$username' AND adminPassword = '$password';");
   while ($row = mysqli_fetch_array($result)) {
    $exists = 1;
    $rowa['id'] = $row['adminID'];
    $rowa['userType'] = 'ADMIN';
    $rowa['name'] = $row['adminName'];
    $rowa['status'] = 1;
  }	  			
  if($exists == 0){
    $rowa['status'] = 0;
  }
  echo json_encode($rowa);


}
else{
	$m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}


   	////////

if ($action == "deregisterNode"){
 $cbsdID = "";

 $cbsdId = $_POST['cbsdId'];
 if ($cbsdId == "" && str_contains_only($cbsdId, $allowed) == false){
   $valid = 0;
 }
 if($valid == 1){
   $sql = "DELETE FROM node WHERE nodeId= '$cbsdId' LIMIT 1";

   if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "CBSD node". $cbsdId . " deregistered and removed";
     echo json_encode($m);

   } else {
    $m['message'] = "Error: " . $sql . "<br>" . mysqli_error($connection);
    $m['status'] = 0;
    echo json_encode($m);

  }
}

else{
  $m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}


if ($action == "deleteGrantRequest"){
 $grantRequestID = "";

 $grantRequestID = $_POST['grantRequestID'];
 if ($grantRequestID == "" && str_contains_only($grantRequestID, $allowed) == false){
   $valid = 0;
 }
 if($valid == 1){
   $sql = "DELETE FROM grantRequest WHERE requestID= '$grantRequestID' LIMIT 1";

   if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Grant request ". $grantRequestID . " deleted";
     echo json_encode($m);

   } else {
    $m['message'] = "Error: " . $sql . "<br>" . mysqli_error($connection);
    $m['status'] = 0;
    echo json_encode($m);

  }
}

else{
	$m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}

if ($action == "deleteTierClassAssignment"){
  $assignmentID = "";

  $assignmentID = $_POST['assignmentID'];
  if ($assignmentID == "" && str_contains_only($assignmentID, $allowed) == false){
    $valid = 0;
  }
  if($valid == 1){
    $sql = "DELETE FROM tierAssignment WHERE tierAssignmentID= '$assignmentID' LIMIT 1";

    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Tier assignment ". $assignmentID . " deleted";
     echo json_encode($m);

   } else {
     $m['message'] = "Error: " . $sql . "<br>" . mysqli_error($connection);
     $m['status'] = 0;
     echo json_encode($m);

   }
 }

 else{
  $m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}


   	//////
if ($action == "createNode"){	
  $nodeName = $location = $IPAddress = $minFrequency = $maxFrequency = $minSampleRate =$maxSampleRate =$nodeType = $mobility = $status = $comment = $userId = $fccId = $cbsdSerialNumber = $callSign = $cbsdCategory = $airInterface = $installationParam = $measCapability = $groupingParam = $SUID = "";
  if ( isset($_POST['nodeName'])) {
   $nodeName = $_POST['nodeName'];
 }
 if ( isset($_POST['location'])) {
   $location = $_POST['location'];
 }
 if ( isset($_POST['SUID'])) {
  $SUID = $_POST['SUID'];
}
 if ( isset($_POST['trustLevel'])) {
   $trustLevel = $_POST['trustLevel'];
 }
 if ( isset($_POST['IPAddress'])) {
   $IPAddress = $_POST['IPAddress'];
 }
 $trustLevel = 5;
 if ( isset($_POST['minFrequency'])) {
   $minFrequency = $_POST['minFrequency'];
 }
 if ( isset($_POST['maxFrequency'])) {
   $maxFrequency = $_POST['maxFrequency'];
 }
 if ( isset($_POST['minSampleRate'])) {
   $minSampleRate = $_POST['minSampleRate'];
 }
 if ( isset($_POST['maxSampleRate'])) {
   $maxSampleRate = $_POST['maxSampleRate'];
 }
 if ( isset($_POST['nodeType'])) {
   $nodeType = $_POST['nodeType'];
 }
 if ( isset($_POST['mobility'])) {
   $mobility = $_POST['mobility'];
 }  
 if ( isset($_POST['status'])) {
   $status = $_POST['status'];
 } 
 if ( isset($_POST['comment'])) {
   $comment = $_POST['comment'];
 } 
 if ( isset($_POST['userId'])) {
   $userId = $_POST['userId'];
 }  
 if ( isset($_POST['fccId'])) {
   $fccId = $_POST['fccId'];
 }
 if ( isset($_POST['cbsdSerialNumber'])) {
   $cbsdSerialNumber = $_POST['cbsdSerialNumber'];
 }
 if ( isset($_POST['callSign'])) {
   $callSign = $_POST['callSign'];
 }
 if ( isset($_POST['cbsdCategory'])) {
   $cbsdCategory = $_POST['cbsdCategory'];
 }
 if ( isset($_POST['cbsdInfo'])) {
   $cbsdInfo = $_POST['cbsdInfo'];
 }
 if ( isset($_POST['airInterface'])) {
   $airInterface = $_POST['airInterface'];
 }
 if ( isset($_POST['installationParam'])) {
   $installationParam = $_POST['installationParam'];
 }
 if ( isset($_POST['measCapability'])) {
   $measCapability = $_POST['measCapability'];
 }
 if ( isset($_POST['groupingParam'])) {
   $groupingParam = $_POST['groupingParam'];
 }

 if ($fccId == "" || $cbsdSerialNumber == ""){
   $valid = 0;
 }

 $result = mysqli_query($connection, "SELECT * FROM node WHERE fccId = '$fccId' LIMIT 1;");
 $present = 0;
 while ($row = mysqli_fetch_array($result)) {
  $present = 1;
}
if($valid == 1 && $present == 0){
 $sql = "INSERT INTO node (nodeName, secondaryUserId, location, trustLevel, IPAddress, minFrequency, maxFrequency, minSampleRate, maxSampleRate, nodeType, mobility, status, comment, fccId, cbsdSerialNumber, callSign, cbsdCategory, cbsdInfo, airInterface, installationParam, measCapability, groupingParam)
 VALUES ('$nodeName', '$SUID', '$location', '$trustLevel', '$IPAddress', '$minFrequency', '$maxFrequency', '$minSampleRate', '$maxSampleRate', '$nodeType', '$mobility', '$status', '$comment', '$fccId', '$cbsdSerialNumber', '$callSign', '$cbsdCategory', '$cbsdInfo', '$airInterface', '$installationParam', '$measCapability', '$groupingParam');";

 if (mysqli_query($connection, $sql)) {
   $m['status'] = 1;
   $m['message'] = "New node created successfully";
   echo json_encode($m);
 } else {
  $m['status'] = 0;
  $m['message'] = "Error connecting to mysql";
}



}
else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  if ($present == 1) {
    $m['message'] = 'already registered';
  }
  echo json_encode($_POST);
}

}
if ($action == "updateNode"){  
  $nodeID = $_POST['nodeID']; 
  $nodeName = $_POST['nodeName'];
  $location = $_POST['location'];
  $trustLevel = $_POST['trustLevel'];
  $IPAddress = $_POST['IPAddress'];
  $minFrequency = $_POST['minFrequency'];
  $maxFrequency = $_POST['maxFrequency'];
  $minSampleRate = $_POST['minSampleRate'];
  $maxSampleRate = $_POST['maxSampleRate'];
  $nodeType = $_POST['nodeType'];
  $mobility = $_POST['mobility'];
  $status = $_POST['status'];
  $comment = $_POST['comment'];
  $fccId = $_POST['fccId'];
  $cbsdSerialNumber = $_POST['cbsdSerialNumber'];
  $callSign = $_POST['callSign'];
  $cbsdCategory = $_POST['cbsdCategoy'];
  $cbsdInfo = $_POST['cbsdInfo'];
  $airInterface = $_POST['airInterface'];
  $installationParam = $_POST['installationParam'];
  $measCapability = $_POST['measCapability'];
  $groupingParam = $_POST['groupingParam'];

  if ($fccId == "" || $cbsdSerialNumber == ""){
    $valid = 0;
  }
  if($valid == 1){
    $sql = "UPDATE node SET nodeName = '$nodeName', location = '$location', trustLevel = '$trustLevel', IPAddress = '$IPAddress', minFrequency = '$minFrequency', maxFrequency = '$maxFrequency', minSampleRate = '$minSampleRate', maxSampleRate = '$maxSampleRate', nodeType = '$nodeType', mobility = '$mobility', status = '$status', comment = '$comment', fccId = '$fccId', cbsdSerialNumber = '$cbsdSerialNumber', callSign = '$callSign', cbsdCategory = '$cbsdCategory', cbsdInfo = '$cbsdInfo', airInterface = '$airInterface', installationParam = '$installationParam', 'measCapability = $measCapability', groupingParam = '$groupingParam' WHERE nodeID = '$nodeID' LIMIT 1;";

    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Node updated successfully";
     $m['ext'] = $sql;
     echo json_encode($m);
   } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
   }



 }
 else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}


if ($action == "createTierClass"){   
 $tierClassName = $_POST['tierClassName'];
 $tierPriorityLevel = $_POST['tierPriorityLevel'];
 $tierClassDescription = $_POST['tierClassDescription'];
 $maxTierNumber = $_POST['maxTierNumber'];
 $tierUpperBand = $_POST['tierUpperBand'];
 $tierLowerBand = $_POST['tierLowerBand'];


 if ($tierClassName == "" || $tierPriorityLevel == "" || $maxTierNumber == "" || $tierUpperBand == "" || $tierLowerBand == ""){
  $valid = 0;
}
if($valid == 1){
  $sql = "INSERT INTO tierClass (tierClassName, tierPriorityLevel, tierClassDescription, maxTierNumber, tierUpperBand, tierLowerBand)
  VALUES ('$tierClassName', '$tierPriorityLevel', '$tierClassDescription', '$maxTierNumber', '$tierUpperBand', '$tierLowerBand');";

  if (mysqli_query($connection, $sql)) {
   $m['status'] = 1;
   $m['message'] = "New tier class created successfully";
   echo json_encode($m);
 } else {
   $m['status'] = 0;
   $m['message'] = "Error connecting to mysql";
 }


 
}
else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}
if ($action == "updateTierClass"){  
  $tierClassID = $_POST['tierClassID']; 
  $tierPriorityLevel = $_POST['tierPriorityLevel'];
  $tierClassDescription = $_POST['tierClassDescription'];
  $maxTierNumber = $_POST['maxTierNumber'];
  $tierUpperBand = $_POST['tierUpperBand'];
  $tierLowerBand = $_POST['tierLowerBand'];

  if ($tierClassName == "" || $tierPriorityLevel == "" || $maxTierNumber == "" || $tierUpperBand == "" || $tierLowerBand == ""){
    $valid = 0;
  }
  if($valid == 1){
    $sql = "UPDATE tierClass SET tierClassName = '$tierClassName', tierPriorityLevel = '$tierPriorityLevel', tierClassDescription = '$tierClassDescription', maxTierNumber = '$maxTierNumber', tierUpperBand = '$tierUpperBand', tierLowerBand = '$tierLowerBand' WHERE tierClassID = '$tierClassID' LIMIT 1;";

    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Tier class updated successfully";
     echo json_encode($m);
   } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
     echo json_encode($m);
   }



 }
 else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}

if ($action == "createRegionSchedule"){   
  $regionName = $_POST['regionName'];
  $regionShape = $_POST['regionShape'];
  $shapeRadius = $_POST['shapeRadius'];
  $shapePoints = $_POST['shapePoints'];
  $schedulingAlgorithm = $_POST['schedulingAlgorithm'];
  $useSUTiers = $_POST['useSUTiers'];
  $useClassTiers = $_POST['useClassTiers'];
  $useInnerClassTiers = $_POST['useInnerClassTiers'];
  $isDefault = $_POST['isDefault'];
  $isActive = $_POST['isActive'];


  if ($regionName == "" || ($regionShape != "circle" && $regionShape != "polygon") || $schedulingAlgorithm == "" || $useSUTiers == "" || $useClassTiers == "" || $useInnerClassTiers == "" || $isDefault == "" || $isActive == ""){
    $valid = 0;
  }
  else {
    if($regionShape == "circle" && $shapeRadius == ""){
      $valid = 0;
    }
  }
  if($valid == 1){
    $sql = "INSERT INTO regionSchedule (regionName, regionShape, shapeRadius, shapePoints, schedulingAlgorithm, useSUTiers, useClassTiers, useInnerClassTiers, isDefault, isActive)
    VALUES ('$regionName', '$regionShape', '$shapeRadius', '$shapePoints', '$schedulingAlgorithm', '$useSUTiers', '$useClassTiers', '$useInnerClassTiers', '$isDefault', '$isActive');";

    if ($id = mysql_inert_id(mysqli_query($connection, $sql))) {
      $m['status'] = 1;
      $m['message'] = "New region schedule created successfully";
      $m['regionID'] = $id;
      echo json_encode($m);
    } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
   }



 }
 else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}
if ($action == "updateRegionSchedule"){ 
  $regionID = $_POST['regionID'];   
  $regionName = $_POST['regionName'];
  $regionShape = $_POST['regionShape'];
  $shapeRadius = $_POST['shapeRadius'];
  $shapePoints = $_POST['shapePoints'];
  $schedulingAlgorithm = $_POST['schedulingAlgorithm'];
  $useSUTiers = $_POST['useSUTiers'];
  $useClassTiers = $_POST['useClassTiers'];
  $useInnerClassTiers = $_POST['useInnerClassTiers'];
  $isDefault = $_POST['isDefault'];
  $isActive = $_POST['isActive'];

  if ($regionID == "" || $regionName == "" || ($regionShape != "circle" && $regionShape != "polygon") || $schedulingAlgorithm == "" || $useSUTiers == "" || $useClassTiers == "" || $useInnerClassTiers == "" || $isDefault == "" || $isActive == ""){
    $valid = 0;
  }
  else {
    if($regionShape == "circle" && $shapeRadius == ""){
      $valid = 0;
    }
  }
  if($valid == 1){
    $sql = "UPDATE regionSchedule SET regionName = '$regionName', regionShape = '$regionShape', shapeRadius = '$shapeRadius', shapePoints = '$shapePoints', schedulingAlgorithm = '$schedulingAlgorithm', useSUTiers = '$useSUTiers', useClassTiers = '$useClassTiers', useInnerClassTiers = '$useInnerClassTiers', isDefault = '$isDefault', isActive = '$isActive' WHERE regionID = '$regionID' LIMIT 1;";

    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "RegionSchedule updated successfully";
     echo json_encode($m);
   } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
     echo json_encode($m);
   }



 }
 else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}

}

if ($action == "alterTierClassAssignment"){  
  $isNewTA = $_POST['isNewTA'];
  $secondaryUserID = $_POST['secondaryUserID'];
  $tierClassID = $_POST['tierClassID'];
  $innerTierLevel = $_POST['innerTierLevel'];
  $tierAssignmentID = "";
  $present = 0;
  $continue = 0;
  if ($isNewTA == "true"){
    if ($secondaryUserID == "" || $tierClassID == "" || $innerTierLevel == ""){
      $valid = 0;
    }
  }
  else{
    $tierAssignmentID = $_POST['tierAssignmentID']; 
    if ($tierAssignmentID == "" || $secondaryUserID == "" || $tierClassID == "" || $innerTierLevel == ""){
      $valid = 0;
    }

  }
  if($valid == 1){
    $result = mysqli_query($connection, "SELECT * FROM tierAssignment WHERE secondaryUserID = '$secondaryUserID' AND tierClassID = '$tierClassID' LIMIT 1;");

    while ($row = mysqli_fetch_array($result)) {
      $present = 1;
    }
    if ($present){


      $sql = "UPDATE tierAssignment SET tierClassID = '$tierClassID', secondaryUserID = '$secondaryUserID', innerTierLevel = '$innerTierLevel' WHERE tierAssignmentID = '$tierAssignmentID' LIMIT 1;";
      if (mysqli_query($connection, $sql)) {
       $m['status'] = 1;
       $m['message'] = "Tier class updated successfully";
       echo json_encode($m);
     } else {
       $m['status'] = 0;
       $m['message'] = "Error connecting to mysql";
       echo json_encode($m);
     }
   }
   else{
          //create new tier class assignment
    $sql = "INSERT INTO tierAssignment (tierClassID, secondaryUserID, innerTierLevel)
    VALUES ('$tierClassID', '$secondaryUserID', '$innerTierLevel');";
    if (mysqli_query($connection, $sql)) {
     $m['status'] = 1;
     $m['message'] = "Tier class created successfully";
     echo json_encode($m);
   } else {
     $m['status'] = 0;
     $m['message'] = "Error connecting to mysql";
     echo json_encode($m);
   }
 }

}
else{
  $m['status'] = 0;
  $m['message'] = 'invalid call not valid';
  echo json_encode($_POST);
}


}

   	   	//////
if ($action == "logGrant"){
 $grantID = $status = "";
 $status = $_POST['status'];
 $grantID = $_POST['grantID'];
 if ($grantID == "" || $status == ""){
   $valid = 0;
 }
 if($status != "TERMINATED" && $status != "DELETED" && $status != "INTERRUPTED"){
  $valid = 0;
}
if ($valid == 1){
 $valid = 0;
 $result = mysqli_query($connection, "SELECT * FROM spectrumGrant WHERE grantID = '$grantID' LIMIT 1;");
 while ($row = mysqli_fetch_array($result)) {
  $valid = 1;
  $grantID = $row['grantID'];
  $approved = $row['approved'];
  $secondaryUserID = $row['secondaryUserID'];
  $frequency = $row['frequency'];
  $bandwidth = $row['bandwidth'];
  $startTime = $row['startTime'];
  $endTime = $row['endTime'];
  $requestMinFrequency = $row['requestMinFrequency'];
  $requestMaxFrequency = $row['requestMaxFrequency'];
  $requestPreferredFrequency = $row['requestPreferredFrequency'];
  $requestFrequencyAbsolute = $row['requestFrequencyAbsolute'];
  $minBandwidth = $row['minBandwidth'];
  $preferredBandwidth = $row['preferredBandwidth'];
  $requestStartTime = $row['requestStartTime'];
  $requestEndTime = $row['requestEndTime'];
  $requestApproximateByteSize = $row['requestApproximateByteSize'];
  $requestDataType = $row['requestDataType'];
  $requestPowerLevel = $row['requestPowerLevel'];
  $requestLocation = $row['requestLocation'];
  $requestMobility = $row['requestMobility'];
  $requestMaxVelocity = $row['requestMaxVelocity'];
}
}	
if($valid == 1){ 			
 $sql = "INSERT INTO grantLog (`grantLogID`, `approved`, `secondaryUserID`, `frequency`, `bandwidth`, `startTime`, `endTime`, `status`, `requestMinFrequency`, `requestMaxFrequency`, `requestPreferredFrequency`, `requestFrequencyAbsolute`, `minBandwidth`, `preferredBandwidth`, `requestStartTime`, `requestEndTime`, `requestApproximateByteSize`, `requestDataType`, `requestPowerLevel`, `requestLocation`, `requestMobility`, `requestMaxVelocity`)
 VALUES ('$grantID', '$approved', '$secondaryUserID', '$frequency', '$bandwidth', '$startTime', '$endTime', '$status', '$requestMinFrequency', '$requestMaxFrequency', '$requestPreferredFrequency', '$requestFrequencyAbsolute', '$minBandwidth', '$preferredBandwidth', '$requestStartTime', '$requestEndTime', '$requestApproximateByteSize', '$requestDataType', '$requestPowerLevel', '$requestLocation', '$requestMobility', '$requestMaxVelocity');";

 if (mysqli_query($connection, $sql)) {
   $m['message'] = "Grant Logged";

   $sqla = "DELETE FROM spectrumGrant WHERE grantID = '$grantID' LIMIT 1;";
   if (mysqli_query($connection, $sqla)) {
    $m['message'] = "Grant Logged and transferred";
    $m['status'] = 1;
  }
  else{
    $m['status'] = 0;
  }

} else {
 $m['message'] =  "Error: " . $sql . "<br>" . mysqli_error($connection);
 $m['status'] = 0;
}
echo json_encode($m);




}
else{
	$m['message'] = 'invalid call not valid';
  echo json_encode($m);
}

}
}

mysqli_close($connection);

function inputInvalid($input){
  if ($input == NULL || $input = ""){
    return 0;
  }
}


?>

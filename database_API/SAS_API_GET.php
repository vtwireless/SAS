<?php
   header("Access-Control-Allow-Origin: *");
   header("Access-Control-Allow-Methods: POST");
   header("Access-Control-Allow-Headers: *");
   include '../incSAS/database.php';//include 'database.php';

   $connection = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD);
   if (mysqli_connect_errno()){
     echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }
  $database = mysqli_select_db($connection, DB_DATABASE);
  $result = NULL;
  date_default_timezone_set('America/New_York');
   //session_start();
  if ($_SERVER["REQUEST_METHOD"] == "POST") {
   if ($_POST["SAS_KEY"] == SAS_KEY) {
   	$action = $_POST['action'];
   /*if ($_POST['SAS_KEY'] != SAS_KEY){
      return 0;
   }*/
   if ($action == "getAllNodes"){
      $exists = 0;
      $result = mysqli_query($connection, "SELECT * FROM node;");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['nodeID'] = $row['nodeID'];
         $rowa['nodeName'] = $row['nodeName'];
         $rowa['location'] = $row['location'];
         $rowa['trustLevel'] = $row['trustLevel'];
         $rowa['IPAddress'] = $row['IPAddress'];
         $rowa['minFrequency'] = $row['minFrequency'];
         $rowa['maxFrequency'] = $row['maxFrequency'];
         $rowa['minSampleRate'] = $row['minSampleRate'];
         $rowa['maxSampleRate'] = $row['maxSampleRate'];
         $rowa['nodeType'] = $row['nodeType'];
         $rowa['mobility'] = $row['mobility'];
         $rowa['status'] = $row['status'];
         $rowa['comment'] = $row['comment'];
         $rowa['fccId'] = $row['fccId'];
         $rowa['cbsdSerialNumber'] = $row['cbsdSerialNumber'];
         $rowa['callSign'] = $row['callSign'];
         $rowa['cbsdCategory'] = $row['cbsdCategory'];
         $rowa['cbsdInfo'] = $row['cbsdInfo'];
         $rowa['airInterface'] = $row['airInterface'];
         $rowa['installationParam'] = $row['installationParam'];
         $rowa['measCapability'] = $row['measCapability'];
         $rowa['groupingParam'] = $row['groupingParam'];
         $rows[] = $rowa;

         $exists = 1;
      }

   if(!$exists) {
     $returnVal['status'] = 0;
     $returnVal['message'] = "No nodes present";
     echo json_encode($returnVal, JSON_NUMERIC_CHECK);
  }
  else{
   $returnVal['status'] = 1;
   $returnVal['nodes'] = $rows;
   echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }  
}

if ($action == "getNodesBySUID"){//my nodes
   $SUID = $_POST["SUID"];
   $exists = 0;
   $result = mysqli_query($connection, "SELECT * FROM node WHERE secondaryUserId = '$SUID';");
   while ($row = mysqli_fetch_array($result)) {
     $rowa['nodeID'] = $row['nodeID'];
     $rowa['nodeName'] = $row['nodeName'];
     $rowa['location'] = $row['location'];
     $rowa['trustLevel'] = $row['trustLevel'];
     $rowa['IPAddress'] = $row['IPAddress'];
     $rowa['minFrequency'] = $row['minFrequency'];
     $rowa['maxFrequency'] = $row['maxFrequency'];
     $rowa['minSampleRate'] = $row['minSampleRate'];
     $rowa['maxSampleRate'] = $row['maxSampleRate'];
     $rowa['nodeType'] = $row['nodeType'];
     $rowa['mobility'] = $row['mobility'];
     $rowa['status'] = $row['status'];
     $rowa['comment'] = $row['comment'];
     $rowa['fccId'] = $row['fccId'];
     $rowa['cbsdSerialNumber'] = $row['cbsdSerialNumber'];
     $rowa['callSign'] = $row['callSign'];
     $rowa['cbsdCategory'] = $row['cbsdCategory'];
     $rowa['cbsdInfo'] = $row['cbsdInfo'];
     $rowa['airInterface'] = $row['airInterface'];
     $rowa['installationParam'] = $row['installationParam'];
     $rowa['measCapability'] = $row['measCapability'];
     $rowa['groupingParam'] = $row['groupingParam'];
     $rows[] = $rowa;

     $exists = 1;
  }

  if(!$exists){
    $returnVal['status'] = 0;
    $returnVal['message'] = "No nodes present";
    echo json_encode($returnVal, JSON_NUMERIC_CHECK);
 }
 else{
  $returnVal['status'] = 1;
  $returnVal['nodes'] = $rows;
  echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }




}

if ($action == "getSettings"){
   $result = mysqli_query($connection, "SELECT `algorithm`, `heartbeatInterval`, `REMAlgorithm` FROM `SASSettings` WHERE 1");
   $row = mysqli_fetch_array($result);
   $returnVal['algorithm'] = $row['algorithm'];
   $returnVal['heartbeatInterval'] = $row['heartbeatInterval'];
   $returnVal['REMAlgorithm'] = $row['REMAlgorithm'];
   $returnVal['status'] = 1;
   echo json_encode($returnVal, JSON_NUMERIC_CHECK);

}


if ($action == "getNode"){
   $exists = 0;
   $nodeID = $_POST['nodeID'];
   if($nodeID != ""){
      $result = mysqli_query($connection, "SELECT * FROM node WHERE nodeID = '$nodeID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['nodeID'] = $row['nodeID'];
         $rowa['nodeName'] = $row['nodeName'];
         $rowa['location'] = $row['location'];
         $rowa['trustLevel'] = $row['trustLevel'];
         $rowa['IPAddress'] = $row['IPAddress'];
         $rowa['minFrequency'] = $row['minFrequency'];
         $rowa['maxFrequency'] = $row['maxFrequency'];
         $rowa['minSampleRate'] = $row['minSampleRate'];
         $rowa['maxSampleRate'] = $row['maxSampleRate'];
         $rowa['nodeType'] = $row['nodeType'];
         $rowa['mobility'] = $row['mobility'];
         $rowa['status'] = $row['status'];
         $rowa['comment'] = $row['comment'];
         $rowa['fccId'] = $row['fccId'];
         $rowa['cbsdSerialNumber'] = $row['cbsdSerialNumber'];
         $rowa['callSign'] = $row['callSign'];
         $rowa['cbsdCategory'] = $row['cbsdCategory'];
         $rowa['cbsdInfo'] = $row['cbsdInfo'];
         $rowa['airInterface'] = $row['airInterface'];
         $rowa['installationParam'] = $row['installationParam'];
         $rowa['measCapability'] = $row['measCapability'];
         $rowa['groupingParam'] = $row['groupingParam'];


         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No node with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['node'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getPrimaryUsers"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT * FROM primaryUser;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['primaryUserID'] = $row['primaryUserID'];
      $rowa['primaryUserName'] = $row['primaryUserName'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary Users Registered";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['primaryUsers'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getPrimaryUser"){
   $exists = 0;
   $primaryUserID = $_POST['primaryUserID'];
   if($primaryUserID != ""){
      $result = mysqli_query($connection, "SELECT * FROM primaryUser WHERE primaryUserID = '$primaryUserID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['primaryUserID'] = $row['primaryUserID'];
         $rowa['primaryUserName'] = $row['primaryUserName'];
         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary User with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['primaryUser'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getSecondaryUsers"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT * FROM secondaryUser;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['secondaryUserID'] = $row['secondaryUserID'];
      $rowa['secondaryUserEmail'] = $row['secondaryUserEmail'];
      $rowa['secondaryUserName'] = $row['secondaryUserName'];
      $rowa['tier'] = $row['tier'];
      $rowa['nodeID'] = $row['nodeID'];
      $rowa['deviceID'] = $row['deviceID'];
      $rowa['location'] = $row['location'];
      $rows[] = $rowa;


      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No secondaryUsers registered in the system";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['secondaryUsers'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}

if ($action == "getSecondaryUser"){
   $exists = 0;
   $rowsb = [];
   $secondaryUserID = $_POST['secondaryUserID'];
   if($secondaryUserID != ""){
      $result = mysqli_query($connection, "SELECT * FROM secondaryUser WHERE secondaryUserID = '$secondaryUserID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secondaryUserEmail'] = $row['secondaryUserEmail'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['tier'] = $row['tier'];
         $rowa['nodeID'] = $row['nodeID'];
         $rowa['deviceID'] = $row['deviceID'];
         $rowa['location'] = $row['location'];


         $exists = 1;
      }
      $resultb = mysqli_query($connection, "SELECT tierClass.*, tierAssignment.* FROM tierAssignment LEFT JOIN tierClass ON tierAssignment.tierClassID = tierClass.tierClassID WHERE tierAssignment.secondaryUserID = '$secondaryUserID';"
   );
      while ($row = mysqli_fetch_array($resultb)) {
         $rowb['tierClassID'] = $row['tierClassID'];
         $rowb['tierClassName'] = $row['tierClassName'];
         $rowb['tierPriorityLevel'] = $row['tierPriorityLevel'];
         $rowb['tierClassDescription'] = $row['tierClassDescription'];
         $rowb['maxTierNumber'] = $row['maxTierNumber'];
         $rowb['tierUpperBand'] = $row['tierUpperBand'];
         $rowb['tierLowerBand'] = $row['tierLowerBand'];
         $rowb['innerTierLevel'] = $row['innerTierLevel'];
         $rowsb[] = $rowb;
         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No node with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['secondaryUser'] = $rowa;
      $returnVal['tierClasses'] = $rowsb;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


}
if ($action == "getGrantRequests"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT secondaryUser.*, grantRequest.* FROM grantRequest INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = grantRequest.secondaryUserID;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['requestID'] = $row['requestID'];
      $rowa['secondaryUserID'] = $row['secondaryUserID'];
      $rowa['secondaryUserName'] = $row['secondaryUserName'];
      $rowa['secodnaryUserEmail'] = $row['secondaryUserEmail'];
      $rowa['tier'] = $row['tier'];
      $rowa['nodeID'] = $row['nodeID'];
      $rowa['deviceID'] = $row['deviceID'];
      $rowa['minFrequency'] = $row['minFrequency'];
      $rowa['maxFrequency'] = $row['maxFrequency'];
      $rowa['preferredFrequency'] = $row['preferredFrequency'];
      $rowa['frequencyAbsolute'] = $row['frequencyAbsolute'];
      $rowa['minBandwidth'] = $row['minBandwidth'];
      $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
      $rowa['startTime'] = $row['startTime'];
      $rowa['endTime'] = $row['endTime'];
      $rowa['approximateByteSize'] = $row['approximateByteSize'];
      $rowa['dataType'] = $row['dataType'];
      $rowa['powerLevel'] = $row['powerLevel'];
      $rowa['location'] = $row['location'];
      $rowa['mobility'] = $row['mobility'];
      $rowa['maxVelocity'] = $row['maxVelocity'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No grant requests";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantRequests'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getGrantRequest"){
   $exists = 0;
   $requestID = $_POST['requestID'];
   if($requestID != ""){
      $result = mysqli_query($connection, "SELECT secondaryUser.*, grantRequest.* FROM grantRequest INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = grantRequest.secondaryUserID WHERE requestID = '$requestID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['requestID'] = $row['requestID'];
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secodnaryUserEmail'] = $row['secondaryUserEmail'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['tier'] = $row['tier'];
         $rowa['nodeID'] = $row['nodeID'];
         $rowa['deviceID'] = $row['deviceID'];
         $rowa['minFrequency'] = $row['minFrequency'];
         $rowa['maxFrequency'] = $row['maxFrequency'];
         $rowa['preferredFrequency'] = $row['preferredFrequency'];
         $rowa['frequencyAbsolute'] = $row['frequencyAbsolute'];
         $rowa['minBandwidth'] = $row['minBandwidth'];
         $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['approximateByteSize'] = $row['approximateByteSize'];
         $rowa['dataType'] = $row['dataType'];
         $rowa['powerLevel'] = $row['powerLevel'];
         $rowa['location'] = $row['location'];
         $rowa['mobility'] = $row['mobility'];
         $rowa['maxVelocity'] = $row['maxVelocity'];

         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No grant with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantRequest'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}

if ($action == "getGrantPresets"){
   $exists = 0;
   $secondaryUserID = $_POST['secondaryUserID'];
   if($secondaryUserID != ""){
      $result = mysqli_query($connection, "SELECT * FROM grantPresets WHERE secondaryUserID = '$secondaryUserID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['grantPresetID'] = $row['grantPresetID'];
         $row['secondaryUserID'] = $row['secondaryUserID'];
         $row['presetName'] = $row['presetName'];
         $rowa['minFrequency'] = $row['minFrequency'];
         $rowa['maxFrequency'] = $row['maxFrequency'];
         $rowa['preferredFrequency'] = $row['preferredFrequency'];
         $rowa['frequencyAbsolute'] = $row['frequencyAbsolute'];
         $rowa['minBandwidth'] = $row['minBandwidth'];
         $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['approximateByteSize'] = $row['approximateByteSize'];
         $rowa['dataType'] = $row['dataType'];
         $rowa['powerLevel'] = $row['powerLevel'];
         $rowa['location'] = $row['location'];
         $rowa['mobility'] = $row['mobility'];
         $rowa['maxVelocity'] = $row['maxVelocity'];
         $rows[] = $rowa;

         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No grant with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantPresets'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}

if ($action == "getAllGrantsBySUID"){
   $exists = 0;
   $SUID = $_POST['SUID'];
   $rowaa = [];
   $rowba = [];
   $rowca = [];
   if($SUID != ""){
      $result = mysqli_query($connection, "SELECT * FROM grantRequest WHERE secondaryUserID = '$SUID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['requestID'] = $row['requestID'];
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['minFrequency'] = $row['minFrequency'];
         $rowa['maxFrequency'] = $row['maxFrequency'];
         $rowa['preferredFrequency'] = $row['preferredFrequency'];
         $rowa['frequencyAbsolute'] = $row['frequencyAbsolute'];
         $rowa['minBandwidth'] = $row['minBandwidth'];
         $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['approximateByteSize'] = $row['approximateByteSize'];
         $rowa['dataType'] = $row['dataType'];
         $rowa['powerLevel'] = $row['powerLevel'];
         $rowa['location'] = $row['location'];
         $rowa['mobility'] = $row['mobility'];
         $rowa['maxVelocity'] = $row['maxVelocity'];
         $rowaa[] = $rowa;

         $exists = 1;
      }
      $result = mysqli_query($connection, "SELECT * FROM spectrumGrant WHERE secondaryUserID = '$SUID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowb['grantID'] = $row['grantID'];
         $rowb['approved'] = $row['approved'];
         $rowb['secondaryUserID'] = $row['secondaryUserID'];
         $rowb['frequency'] = $row['frequency'];
         $rowb['bandwidth'] = $row['bandwidth'];
         $rowb['startTime'] = $row['startTime'];
         $rowb['endTime'] = $row['endTime'];
         $rowb['status'] = $row['status'];
         $rowb['requestMinFrequency'] = $row['requestMinFrequency'];
         $rowb['requestMaxFrequency'] = $row['requestMaxFrequency'];
         $rowb['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
         $rowb['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
         $rowb['minBandwidth'] = $row['minBandwidth'];
         $rowb['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowb['requestStartTime'] = $row['requestStartTime'];
         $rowb['requestEndTime'] = $row['requestEndTime'];
         $rowb['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
         $rowb['requestDataType'] = $row['requestDataType'];
         $rowb['requestPowerLevel'] = $row['requestPowerLevel'];
         $rowb['requestLocation'] = $row['requestLocation'];
         $rowb['requestMobility'] = $row['requestMobility'];
         $rowb['requestMaxVelocity'] = $row['requestMaxVelocity'];
         $rowba[] = $rowb;
         $exists = 1;
      }
      $result = mysqli_query($connection, "SELECT * FROM grantLog WHERE secondaryUserID = '$SUID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowc['grantLogID'] = $row['grantLogID'];
         $rowc['approved'] = $row['approved'];
         $rowc['secondaryUserID'] = $row['secondaryUserID'];
         $rowc['frequency'] = $row['frequency'];
         $rowc['bandwidth'] = $row['bandwidth'];
         $rowc['startTime'] = $row['startTime'];
         $rowc['endTime'] = $row['endTime'];
         $rowc['status'] = $row['status'];
         $rowc['requestMinFrequency'] = $row['requestMinFrequency'];
         $rowc['requestMaxFrequency'] = $row['requestMaxFrequency'];
         $rowc['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
         $rowc['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
         $rowc['minBandwidth'] = $row['minBandwidth'];
         $rowc['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowc['requestStartTime'] = $row['requestStartTime'];
         $rowc['requestEndTime'] = $row['requestEndTime'];
         $rowc['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
         $rowc['requestDataType'] = $row['requestDataType'];
         $rowc['requestPowerLevel'] = $row['requestPowerLevel'];
         $rowc['requestLocation'] = $row['requestLocation'];
         $rowc['requestMobility'] = $row['requestMobility'];
         $rowc['requestMaxVelocity'] = $row['requestMaxVelocity'];
         $rowca[] = $rowc;
         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No grants from that Secondary User ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantRequests'] = $rowaa;
      $returnVal['spectrumGrants'] = $rowba;
      $returnVal['grantLogs'] = $rowca;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getSpectrumGrants"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT secondaryUser.*, spectrumGrant.* FROM spectrumGrant INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = spectrumGrant.secondaryUserID");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['grantID'] = $row['grantID'];
      $rowa['approved'] = $row['approved'];
      $rowa['secondaryUserID'] = $row['secondaryUserID'];
      $rowa['secondaryUserName'] = $row['secondaryUserName'];
      $rowa['tier'] = $row['tier'];
      //$rowa['nodeID'] = $row['nodeID'];
      $rowa['deviceID'] = $row['deviceID'];
      $rowa['frequency'] = $row['frequency'];
      $rowa['bandwidth'] = $row['bandwidth'];
      $rowa['startTime'] = $row['startTime'];
      $rowa['endTime'] = $row['endTime'];
      $rowa['status'] = $row['status'];
      $rowa['requestMinFrequency'] = $row['requestMinFrequency'];
      $rowa['requestMaxFrequency'] = $row['requestMaxFrequency'];
      $rowa['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
      $rowa['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
      $rowa['minBandwidth'] = $row['minBandwidth'];
      $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
      $rowa['requestStartTime'] = $row['requestStartTime'];
      $rowa['requestEndTime'] = $row['requestEndTime'];
      $rowa['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
      $rowa['requestDataType'] = $row['requestDataType'];
      $rowa['requestPowerLevel'] = $row['requestPowerLevel'];
      $rowa['requestLocation'] = $row['requestLocation'];
      $rowa['requestMobility'] = $row['requestMobility'];
      $rowa['requestMaxVelocity'] = $row['requestMaxVelocity'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No spectrum grants";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['spectrumGrants'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getSpectrumGrant"){
   $exists = 0;
   $grantID = $_POST['grantID'];
   if($grantID != ""){
      $result = mysqli_query($connection, "SELECT secondaryUser.*, spectrumGrant.* FROM spectrumGrant INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = spectrumGrant.secondaryUserID WHERE grantID = '$grantID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['grantID'] = $row['grantID'];
         $rowa['approved'] = $row['approved'];
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['tier'] = $row['tier'];
         //$rowa['nodeID'] = $row['nodeID'];
         $rowa['deviceID'] = $row['deviceID'];
         $rowa['frequency'] = $row['frequency'];
         $rowa['bandwidth'] = $row['bandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['status'] = $row['status'];
         $rowa['requestMinFrequency'] = $row['requestMinFrequency'];
         $rowa['requestMaxFrequency'] = $row['requestMaxFrequency'];
         $rowa['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
         $rowa['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
         $rowa['minBandwidth'] = $row['minBandwidth'];
         $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowa['requestStartTime'] = $row['requestStartTime'];
         $rowa['requestEndTime'] = $row['requestEndTime'];
         $rowa['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
         $rowa['requestDataType'] = $row['requestDataType'];
         $rowa['requestPowerLevel'] = $row['requestPowerLevel'];
         $rowa['requestLocation'] = $row['requestLocation'];
         $rowa['requestMobility'] = $row['requestMobility'];
         $rowa['requestMaxVelocity'] = $row['requestMaxVelocity'];

         $exists = 1;
      }
      $rowc = [];
      $resultb = mysqli_query($connection, "SELECT * FROM heartbeat WHERE grantID = '$grantID';");
      while ($rows = mysqli_fetch_array($resultb)) {
         $rowb['grantID'] = $rows['grantID'];
         $rowb['heartbeatID'] = $rows['heartbeatID'];
         $rowb['heartbeatTime'] = $rows['heartbeatTime'];
         $rowb['secondaryUserLocation'] = $rows['secondaryUserLocation'];
         $rowb['secondaryUserVelocity'] = $rows['secondaryUserVelocity'];
         $rowb['heartbeatGrantStatus'] = $rows['heartbeatGrantStatus'];
         $rowb['heartbeatBandwidth'] = $rows['heartbeatBandwidth'];
         $rowc[] = $rowb;
         $exists = 1;
      }            
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No node with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['spectrumGrant'] = $rowa;
      $returnVal['heartbeats'] = $rowc;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getTierClasses"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT * FROM tierClass");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['tierClassID'] = $row['tierClassID'];
      $rowa['tierClassName'] = $row['tierClassName'];
      $rowa['tierPriorityLevel'] = $row['tierPriorityLevel'];
      $rowa['tierClassDescription'] = $row['tierClassDescription'];
      $rowa['maxTierNumber'] = $row['maxTierNumber'];
      $rowa['tierUpperBand'] = $row['tierUpperBand'];
      $rowa['tierLowerBand'] = $row['tierLowerBand'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No tier classes";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['tierClasses'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getTierClass"){
   $exists = 0;
   $tierClassID = $_POST['tierClassID'];
   if($tierClassID != ""){
      $result = mysqli_query($connection, "SELECT * FROM tierClass WHERE tierClassID = '$tierClassID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['tierClassID'] = $row['tierClassID'];
         $rowa['tierClassName'] = $row['tierClassName'];
         $rowa['tierPriorityLevel'] = $row['tierPriorityLevel'];
         $rowa['tierClassDescription'] = $row['tierClassDescription'];
         $rowa['maxTierNumber'] = $row['maxTierNumber'];
         $rowa['tierUpperBand'] = $row['tierUpperBand'];
         $rowa['tierLowerBand'] = $row['tierLowerBand'];
         $rows[] = $rowa;
         $exists = 1;
      }
      $rowc = [];
      $resultb = mysqli_query($connection, "SELECT tierAssignment.*, secondaryUser.secondaryUserID, secondaryUser.secondaryUserEmail, secondaryUser.secondaryUserName FROM `tierAssignment` INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = tierAssignment.secondaryUserID WHERE tierClassID = '$tierClassID';");
      while ($rows = mysqli_fetch_array($resultb)) {
         $rowb['tierAssignmentID'] = $rows['tierAssignmentID'];
         $rowb['secondaryUserID'] = $rows['secondaryUserID'];
         $rowb['secondaryUserName'] = $rows['secondaryUserName'];
         $rowb['secondaryUserEmail'] = $rows['secondaryUserEmail'];
         $rowb['innerTierLevel'] = $rows['innerTierLevel'];

         $rowc[] = $rowb;
         $exists = 1;
      }            
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No tier class with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['tierClass'] = $rowa;
      $returnVal['tierClassSUs'] = $rowc;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getSUsNotInTierClass"){
   $exists = 0;
   $tierClassID = $_POST['tierClassID'];
   if($tierClassID != ""){
      $result = mysqli_query($connection, "SELECT secondaryUser.secondaryUserID, secondaryUser.secondaryUserEmail, secondaryUser.secondaryUserName FROM secondaryUser WHERE secondaryUserID NOT IN ( SELECT secondaryUser.secondaryUserID from secondaryUser JOIN tierAssignment ON secondaryUser.secondaryUserID = tierAssignment.secondaryUserID WHERE tierAssignment.tierClassID = '$tierClassID');");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['secondaryUserEmail'] = $row['secondaryUserEmail'];
         $rows[] = $rowa;
         $exists = 1;
      }            
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No tier class with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['secondaryUsers'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}
if ($action == "getGrantLogs"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT secondaryUser.*, grantLog.* FROM grantLog INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = grantLog.secondaryUserID;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['grantID'] = $row['grantLogID'];
      $rowa['approved'] = $row['approved'];
      $rowa['secondaryUserID'] = $row['secondaryUserID'];
      $rowa['secondaryUserName'] = $row['secondaryUserName'];
      $rowa['tier'] = $row['tier'];
      $rowa['nodeID'] = $row['nodeID'];
      $rowa['deviceID'] = $row['deviceID'];
      $rowa['frequency'] = $row['frequency'];
      $rowa['bandwidth'] = $row['bandwidth'];
      $rowa['startTime'] = $row['startTime'];
      $rowa['endTime'] = $row['endTime'];
      $rowa['status'] = $row['status'];
      $rowa['requestMinFrequency'] = $row['requestMinFrequency'];
      $rowa['requestMaxFrequency'] = $row['requestMaxFrequency'];
      $rowa['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
      $rowa['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
      $rowa['minBandwidth'] = $row['minBandwidth'];
      $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
      $rowa['requestStartTime'] = $row['requestStartTime'];
      $rowa['requestEndTime'] = $row['requestEndTime'];
      $rowa['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
      $rowa['requestDataType'] = $row['requestDataType'];
      $rowa['requestPowerLevel'] = $row['requestPowerLevel'];
      $rowa['requestLocation'] = $row['requestLocation'];
      $rowa['requestMobility'] = $row['requestMobility'];
      $rowa['requestMaxVelocity'] = $row['requestMaxVelocity'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No logged grants";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantLogs'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getGrantLog"){
   $exists = 0;
   $grantLogID = $_POST['grantLogID'];
   if($grantLogID != ""){
      $result = mysqli_query($connection, "SELECT secondaryUser.*, grantLog.* FROM grantLog INNER JOIN secondaryUser ON secondaryUser.secondaryUserID = grantLog.secondaryUserID WHERE grantLogID = '$grantLogID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['grantID'] = $row['grantLogID'];
         $rowa['approved'] = $row['approved'];
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['tier'] = $row['tier'];
         $rowa['nodeID'] = $row['nodeID'];
         $rowa['deviceID'] = $row['deviceID'];
         $rowa['frequency'] = $row['frequency'];
         $rowa['bandwidth'] = $row['bandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['status'] = $row['status'];
         $rowa['requestMinFrequency'] = $row['requestMinFrequency'];
         $rowa['requestMaxFrequency'] = $row['requestMaxFrequency'];
         $rowa['requestPreferredFrequency'] = $row['requestPreferredFrequency'];
         $rowa['requestFrequencyAbsolute'] = $row['requestFrequencyAbsolute'];
         $rowa['minBandwidth'] = $row['minBandwidth'];
         $rowa['preferredBandwidth'] = $row['preferredBandwidth'];
         $rowa['requestStartTime'] = $row['requestStartTime'];
         $rowa['requestEndTime'] = $row['requestEndTime'];
         $rowa['requestApproximateByteSize'] = $row['requestApproximateByteSize'];
         $rowa['requestDataType'] = $row['requestDataType'];
         $rowa['requestPowerLevel'] = $row['requestPowerLevel'];
         $rowa['requestLocation'] = $row['requestLocation'];
         $rowa['requestMobility'] = $row['requestMobility'];
         $rowa['requestMaxVelocity'] = $row['requestMaxVelocity'];


         $exists = 1;
      }
      $rowc = [];
      $resultb = mysqli_query($connection, "SELECT * FROM heartbeat WHERE grantID = '$grantLogID';");
      while ($rows = mysqli_fetch_array($resultb)) {
         $rowb['grantID'] = $rows['grantID'];
         $rowb['heartbeatID'] = $rows['heartbeatID'];
         $rowb['heartbeatTime'] = $rows['heartbeatTime'];
         $rowb['secondaryUserLocation'] = $rows['secondaryUserLocation'];
         $rowb['secondaryUserVelocity'] = $rows['secondaryUserVelocity'];
         $rowb['heartbeatGrantStatus'] = $rows['heartbeatGrantStatus'];
         $rowb['heartbeatBandwidth'] = $rows['heartbeatBandwidth'];
         $rowc[] = $rowb;
         $exists = 1;
      }   
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No logged grants with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['grantLog'] = $rowa;
      $returnVal['heartbeats'] = $rowc;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


   

}
if ($action == "getHeartbeats"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT heartbeat.*, spectrumGrant.*, secondaryUser.* FROM heartbeat INNER JOIN spectrumGrant ON heartbeat.grantID = spectrumGrant.grantID INNER JOIN secondaryUser ON spectrumGrant.secondaryUserID = secondaryUser.secondaryUserID;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['heartbeatID'] = $row['heartbeatID'];
      $rowa['grantID'] = $row['grantID'];
      $rowa['secondaryUserID'] = $row['secondaryUserID'];
      $rowa['secondaryUserName'] = $row['secondaryUserName'];
      $rowa['tier'] = $row['tier'];
      $rowa['heartbeatTime'] = $row['heartbeatTime'];
      $rowa['secondaryUserLocation'] = $row['secondaryUserLocation'];
      $rowa['secondaryUserVelocity'] = $row['secondaryUserVelocity'];
      $rowa['heartbeatGrantStatus'] = $row['heartbeatGrantStatus'];
      $rowa['heartbeatBandwidth'] = $row['heartbeatBandwidth'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No heartbeats";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['heartbeats'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getHeartbeat"){
   $exists = 0;
   $heartbeatID = $_POST['heartbeatID'];
   if($heartbeatID != ""){
      $result = mysqli_query($connection, "SELECT heartbeat.*, spectrumGrant.*, secondaryUser.* FROM heartbeat INNER JOIN spectrumGrant ON heartbeat.grantID = spectrumGrant.grantID INNER JOIN secondaryUser ON spectrumGrant.secondaryUserID = secondaryUser.secondaryUserID WHERE heartbeatID = '$heartbeatID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['heartbeatID'] = $row['heartbeatID'];
         $rowa['grantID'] = $row['grantID'];
         $rowa['secondaryUserID'] = $row['secondaryUserID'];
         $rowa['secondaryUserName'] = $row['secondaryUserName'];
         $rowa['tier'] = $row['tier'];
         $rowa['heartbeatTime'] = $row['heartbeatTime'];
         $rowa['secondaryUserLocation'] = $row['secondaryUserLocation'];
         $rowa['secondaryUserVelocity'] = $row['secondaryUserVelocity'];
         $rowa['heartbeatGrantStatus'] = $row['heartbeatGrantStatus'];
         $rowa['heartbeatBandwidth'] = $row['heartbeatBandwidth'];


         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No heartbeats with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['heartbeat'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}
if ($action == "getPrimaryUserActivities"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT primaryUser.*, primaryUserActivity.* FROM primaryUserActivity INNER JOIN primaryUser ON primaryUser.primaryUserID = primaryUserActivity.primaryUserID");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['PUActivityID'] = $row['PUActivityID'];
      $rowa['primaryUserID'] = $row['primaryUserID'];
      $rowa['primaryUserName'] = $row['primaryUserName'];
      $rowa['bandwidth'] = $row['bandwidth'];
      $rowa['frequency'] = $row['frequency'];
      $rowa['startTime'] = $row['startTime'];
      $rowa['endTime'] = $row['endTime'];
      $rowa['expectedEndTime'] = $row['expectedEndTime'];
      $rowa['location'] = $row['location'];
      $rowa['locationConfidence'] = $row['locationConfidence'];
      $rowa['activityStatus'] = $row['activityStatus'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary User activity";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['primaryUserActivities'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}
if ($action == "getRegionSchedules"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT * FROM regionSchedule;");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['regionID'] = $row['regionID'];
      $rowa['regionName'] = $row['regionName'];
      $rowa['regionShape'] = $row['regionShape'];
      $rowa['shapePoints'] = $row['shapePoints'];
      $rowa['shapeRadius'] = $row['shapeRadius'];
      $rowa['schedulingAlgorithm'] = $row['schedulingAlgorithm'];
      $rowa['useSUTiers'] = $row['useSUTiers'];
      $rowa['useClassTiers'] = $row['useClassTiers'];
      $rowa['useInnerClassTiers'] = $row['useInnerClassTiers'];
      $rowa['isDefault'] = $row['isDefault'];
      $rowa['isActive'] = $row['isActive'];
      $rows[] = $rowa;
      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No schedules";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['regionSchedules'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }


}
if ($action == "getPrimaryUserActivitiesByPUID"){
   $exists = 0;
   $primaryUserID = $_POST['primaryUserID'];
   if ($primaryUserID != ""){
      $result = mysqli_query($connection, "SELECT primaryUser.primaryUserName, primaryUserActivity.* FROM primaryUserActivity INNER JOIN primaryUser ON primaryUser.primaryUserID = primaryUserActivity.primaryUserID WHERE primaryUser.primaryUserID = '$primaryUserID'");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['PUActivityID'] = $row['PUActivityID'];
         $rowa['primaryUserID'] = $row['primaryUserID'];
         $rowa['primaryUserName'] = $row['primaryUserName'];
         $rowa['bandwidth'] = $row['bandwidth'];
         $rowa['frequency'] = $row['frequency'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['expectedEndTime'] = $row['expectedEndTime'];
         $rowa['location'] = $row['location'];
         $rowa['locationConfidence'] = $row['locationConfidence'];
         $rowa['activityStatus'] = $row['activityStatus'];
         $rows[] = $rowa;
         $exists = 1;
      }

      if(!$exists){
         $returnVal['status'] = 0;
         $returnVal['message'] = "No Primary User activity";
         echo json_encode($returnVal, JSON_NUMERIC_CHECK);
      }
      else{
         $returnVal['status'] = 1;
         $returnVal['primaryUserActivities'] = $rows;
         echo json_encode($returnVal, JSON_NUMERIC_CHECK);
      }
   }

}


if ($action == "getPrimaryUserActivitiesByID"){
   $exists = 0;
   $PUActivityID = $_POST['PUActivityID'];
   if($PUActivityID != ""){
      $result = mysqli_query($connection, "SELECT primaryUser.*, primaryUserActivity.* FROM primaryUserActivity INNER JOIN primaryUser ON primaryUser.primaryUserID = primaryUserActivity.primaryUserID WHERE PUActivityID = '$PUActivityID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['PUActivityID'] = $row['PUActivityID'];
         $rowa['primaryUserID'] = $row['primaryUserID'];
         $rowa['primaryUserName'] = $row['primaryUserName'];
         $rowa['frequency'] = $row['frequency'];
         $rowa['bandwidth'] = $row['bandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['expectedEndTime'] = $row['expectedEndTime'];
         $rowa['location'] = $row['location'];
         $rowa['locationConfidence'] = $row['locationConfidence'];
         $rowa['activityStatus'] = $row['activityStatus'];

         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary User Activity with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['PUActivities'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}
if ($action == "getPrimaryUserLogs"){
   $exists = 0;
   $result = mysqli_query($connection, "SELECT primaryUser.*, primaryUserLog.* FROM primaryUserLog INNER JOIN primaryUser ON primaryUser.primaryUserID = primaryUserLog.primaryUserID");
   while ($row = mysqli_fetch_array($result)) {
      $rowa['PULogID'] = $row['PULogID'];
      $rowa['primaryUserID'] = $row['primaryUserID'];
      $rowa['primaryUserName'] = $row['primaryUserName'];
      $rowa['frequency'] = $row['frequency'];
      $rowa['bandwidth'] = $row['bandwidth'];
      $rowa['startTime'] = $row['startTime'];
      $rowa['endTime'] = $row['endTime'];
      $rowa['expectedEndTime'] = $row['expectedEndTime'];
      $rowa['location'] = $row['location'];
      $rowa['locationConfidence'] = $row['locationConfidence'];
      $rowa['comment'] = $row['comment'];
      $rows[] = $rowa;

      $exists = 1;
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary User logs";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['primaryUserLogs'] = $rows;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}


if ($action == "getPrimaryUserLog"){
   $exists = 0;
   $PULogID = $_POST['PULogID'];
   if($PULogID != ""){
      $result = mysqli_query($connection, "SELECT primaryUser.*, primaryUserLog.* FROM primaryUserLog INNER JOIN primaryUser ON primaryUser.primaryUserID = primaryUserLog.primaryUserID WHERE PULogID = '$PULogID';");
      while ($row = mysqli_fetch_array($result)) {
         $rowa['PULogID'] = $row['PULogID'];
         $rowa['primaryUserID'] = $row['primaryUserID'];
         $rowa['primaryUserName'] = $row['primaryUserName'];
         $rowa['frequency'] = $row['frequency'];
         $rowa['bandwidth'] = $row['bandwidth'];
         $rowa['startTime'] = $row['startTime'];
         $rowa['endTime'] = $row['endTime'];
         $rowa['expectedEndTime'] = $row['expectedEndTime'];
         $rowa['location'] = $row['location'];
         $rowa['locationConfidence'] = $row['locationConfidence'];
         $rowa['comment'] = $row['comment'];


         $exists = 1;
      }
   }

   if(!$exists){
      $returnVal['status'] = 0;
      $returnVal['message'] = "No Primary User Log with that ID";
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }
   else{
      $returnVal['status'] = 1;
      $returnVal['PULog'] = $rowa;
      echo json_encode($returnVal, JSON_NUMERIC_CHECK);
   }

}

}
}
if ($result != NULL){
   mysqli_free_result($result);
}
else{
   echo 'incorrect API Call';
}
mysqli_close($connection);
?>
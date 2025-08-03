<?php
/*
$pythonScript = 'C:\xampp\htdocs\PiCrypt\python\picrypt.py';
$uploadFolder = 'C:\xampp\htdocs\PiCrypt\python\upload\\';

// Specify the desired names for the images
$secretImageName = "stego.png";

$tempFile1 = $_FILES["stego_image"]["tmp_name"];
$destination1= $uploadFolder . $secretImageName;
// Move uploaded files to the specified names
if (move_uploaded_file($tempFile1, $destination1)) {
    #echo "Files have been successfully uploaded and stored.";
} else {
    #echo "Error uploading or storing files.";
}


$privateKey = 'C:\xampp\htdocs\PiCrypt\python\keypair\myprivatekey.pem';
$outputImage = 'C:\xampp\htdocs\PiCrypt\python\extract\extract.png';

// Execute Python script to process the image
$command = "python \"$pythonScript\" extract \"$destination1\" \"$privateKey\" \"$outputImage\"";
$output = shell_exec($command);
echo '<script>
        window.location = "../extract/page2.html";
      </script>';

if (file_exists($destination1)) {
    unlink($destination1);
    }*/
?>

<?php

$pythonScript = '..\python\picrypt.py';
$uploadFolder = '..\python\upload\\';
$stegoimageName = "stego.png";
// Specify the desired names for the images
$tempFile1 = $_FILES["stego_image"]["tmp_name"];
$destination1 = $uploadFolder.$stegoimageName;
// Move uploaded files to the specified names
if (move_uploaded_file($tempFile1, $destination1)) {
    #echo "Files have been successfully uploaded and stored.";
} else {
    #echo "Error uploading or storing files.";
}


$privateKey = '..\python\keypair\myprivatekey.pem';
$outputImage = '..\python\extract\extract.png';

// Execute Python script to process the image
$command = "python \"$pythonScript\" extract \"$destination1\" \"$privateKey\" \"$outputImage\" 2>&1";
$output = exec($command);
#echo "Successfully generated and stored stego image.";
#echo $command,$output;
$colonPosition = strpos($output, ':');
if ($colonPosition !== false) {
    $output = substr($output, $colonPosition + 1);
}

if (file_exists($destination1)) {
    unlink($destination1);
}

?>

<script>
    // Display the output in an alert box
    alert('<?php echo $output; ?>');
    
    // Redirect to another page after displaying the alert
    window.location = "../extract/page2.html";
</script>

<?php

$pythonScript = '..\python\picrypt.py';
$uploadFolder = '..\python\upload\\';
// Specify the desired names for the images
$tempFile1 = $_FILES["cover_image"]["tmp_name"];
$tempFile2 = $_FILES["secret_image"]["tmp_name"];
$coverImageName = "coverimage.png";
$secretImageName = "secretimage.png";
$destination1 = $uploadFolder.$coverImageName;
$destination2 = $uploadFolder.$secretImageName;
// Move uploaded files to the specified names
if (move_uploaded_file($tempFile1, $destination1) && move_uploaded_file($tempFile2, $destination2)) {
    #echo "Files have been successfully uploaded and stored.";
} else {
    #echo "Error uploading or storing files.";
}


$publicKey = '..\python\keypair\mypublickey.pem';
$outputImage = '..\python\secret\stego.png';

// Execute Python script to process the image
$command = "python \"$pythonScript\" hide \"$destination1\" \"$destination2\" \"$publicKey\" \"$outputImage\" 2>&1";
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

if (file_exists($destination2)) {
    unlink($destination2);
}
?>

<script>
    // Display the output in an alert box
    alert('<?php echo $output; ?>');
    
    // Redirect to another page after displaying the alert
    window.location = "../embed/page1.html";
</script>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    #gifContainer {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    #gifImage {
      transition: transform 2s;
    }
  </style>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
<?php
    include("connection.php");

    $email = $_POST['email'];
    $pass = $_POST['password'];
    $cpass = $_POST['cpass'];
    $check = mysqli_query($connect, "select * from user where name='$email' ");
    if($cpass!=$pass){
        ?>
            <div id="gifContainer">
            <?php
                // Display the GIF image
                echo '<img id="gifImage" src="../gallery/unsuccess.gif" alt="GIF Image">';
            ?>
            </div><?php
         echo '<script>';
         echo 'document.getElementById("gifImage").style.transform = "scale(0.5)";'; // You can adjust the scale factor as needed
         echo '</script>';
         echo '<script>';
         echo 'setTimeout(function() {';
         echo 'window.location.href = "../signin/index.html";'; 
         echo '}, 2000);'; 
         echo '</script>';
    }
    else if(mysqli_num_rows($check)>0){ 
     echo '<script>alert("User ID already Exists ")</script>';
     echo '<script>window.location.href = "../signin/index.html"</script>;'; 
    }
    else{
        $pass1 = hash('sha256', $pass);
        $insert = mysqli_query($connect, "insert into user (name,password) values('$email','$pass1') ");
        if($insert){?>
            <div id="gifContainer">
            <?php
                // Display the GIF image
                echo '<img id="gifImage" src="../gallery/success.gif" alt="GIF Image">';
            ?>
            </div><?php
            echo '<script>';
            echo 'document.getElementById("gifImage").style.transform = "scale(0.7)";'; // You can adjust the scale factor as needed
            echo '</script>';
        
            // Redirect to the next page after 5 seconds
            echo '<script>';
            echo 'setTimeout(function() {';
            echo 'window.location.href = "../optional/index.html";'; // Replace "next-page.php" with the URL of the next page
            echo '}, 2000);'; 
            echo '</script>';
        }
      }
    
?>
</body>
</html>
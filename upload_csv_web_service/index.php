<?php 

    if(isset($_POST['submit']) and $_FILES) {
        move_uploaded_file($_FILES['file']['tmp_name'], "~/aiogram_db_bot/".$_FILES['file']['name']);
    }

?>

<form method="post" action="" enctype="multipart/form-data">
<input type="file" name="file"><br>
<input type="submit" name="submit" value="Загрузить файл">
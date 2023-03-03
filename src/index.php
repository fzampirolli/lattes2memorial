<?php

function custom_copy($src, $dst)
{
  // open the source directory
  $dir = opendir($src);
  // Make the destination directory if not exist
  @mkdir($dst);
  // Loop through the files in source directory
  while ($file = readdir($dir)) {
    if (($file != '.') && ($file != '..')) {
      if (is_dir($src . '/' . $file)) {
        // Recursively calling custom copy function
        // for sub directory 
        custom_copy($src . '/' . $file, $dst . '/' . $file);
      } else {
        copy($src . '/' . $file, $dst . '/' . $file);
      }
    }
  }
  closedir($dir);
}

if (isset($_FILES['image'])) {
  $errors = array();
  $file_name = $_FILES['image']['name'];
  $file_size = $_FILES['image']['size'];
  $file_tmp = $_FILES['image']['tmp_name'];
  $file_type = $_FILES['image']['type'];
  $file_ext = strtolower(end(explode('.', $_FILES['image']['name'])));

  $extensions = array("zip");

  if (in_array($file_ext, $extensions) === false) {
    $errors[] = "extension not allowed, please choose a zip file.";
  }

  if ($file_size > 2097152) {
    $errors[] = 'File size must be excately 2 MB';
  }

  if (empty($errors) == true) {
    echo "<h2>$file_name</h2>";
    $aux = substr($file_name, 0, 19);
    $dst =  "tmp/" . $aux;
    @mkdir($dst);
    move_uploaded_file($file_tmp, $dst . "/" . $file_name);
    $src = "src";
    custom_copy($src, $dst);

    exec("find " . $dst . " -type d -exec chmod 0777 {} +");
    exec("find " . $dst . " -type f -exec chmod 0777 {} +");

    echo "<pre>$dst</pre>";
    $output = exec("sh " . $dst . "/run.sh " . $aux);
    echo "<pre>source " . $dst . "/run.sh " . $aux . "</pre>";


    $file =  $dst . "_lattes.zip";
    header('Content-Type: application/octet-stream');
    header("Content-Transfer-Encoding: utf-8");
    header("Content-disposition: attachment; filename=\"" . basename($file) . "\"");
    readfile($file);

    echo "<pre>download file " . $file . "</pre>";


    if (unlink($file)) {
      print("Todos os arquivos deste lattes foram removidos deste servidor");
    } else {
      $errors[] = 'Erro ao remover arquivos do servidor, enviar email ao admin';
    }


    $file =  substr($dst, 4, strlen($str)-1) . "_lattes.zip";
    $error_message = "lattes2memorial: " . $file;
    $log_file = "./tmp/logs.txt";

    // setting error logging to be active
    ini_set("log_errors", TRUE);

    // setting the logging file in php.ini
    ini_set('error_log', $log_file);

    // logging the error
    error_log($error_message);
  } else {
    print_r($errors);
  }
}
?>
<!DOCTYPE html>
<html lang="pt-br">

<head>
  <style>
    div {
      background-color: lightgrey;
      width: 85%;
      border: 10px solid green;
      padding: 30px;
      margin: 20px;
    }
  </style>

  <title>lattes2memorial</title>
</head>

<body>
  <h1>Serviço para fazer upload do zip gerado pelo lattes e converter para latex</h1>
  <hr>
  <div>
    <ul>
      <li> Submeter examente o zip gerado pela plataforma lattes no formato "CV_xxxxxxxxxxxxx.zip" (ver <a href="https://github.com/fzampirolli/lattes2memorial" target="_blank">GitHub</a>); </li>
      <li> Após clicar no botão Enviar abaixo, o servidor cria todos os arquivos necessários para gerar o PDF pelo latex; </li>
      <li> Estes arquivos estarão dentro de uma pasta que será compactada e enviada de volta ao seu computador; </li>
      <li> Todos os arquivos do servidor referente ao seu lattes serão removidos após esse envio; </li>
      <li> O conteúdo deste zip poderá ser adaptado como desejar em seu computador, após instalar as bibliotecas necessárias; </li>
      <li> Todos os fontes para processar localmente estão também nesse zip, contendo o mesmo conteúdo genérico que está no <a href="https://github.com/fzampirolli/lattes2memorial" target="_blank">GitHub</a>; </li>
      <li> Bugs poderão existir, pois esse gerador de conteúdo foi criado para atender as necessidades do lattes do autor; </li>
      <li> Assim, melhorias deverão ocorrer, conforme feedbacks; </li>
      <li> Sugestões são sempre bem vindas: <a href="mailto:fzampirolli@ufabc.edu.br" target="_self">enviar e-mail</a>. </li>
    </ul>
    <h4>
    </h4>

    <hr>
    <p>
    <form action="" method="POST" enctype="multipart/form-data">
      <input type="file" name="image" />
      <input type="submit" />
    </form>
    <p>
  </div>

  <hr>

  <a href="https://www.gnu.org/licenses/agpl-3.0.html"><img src="http://mctest.ufabc.edu.br:8000/static/agplv3.png"></a>

  <a href="#">Copyright © 2023</a> por

  <a href="https://sites.google.com/site/fzampirolli/">Francisco de Assis Zampirolli</a> da

  <a href="http://www.ufabc.edu.br">UFABC</a> e colaboradores, em especial ao prof. <a href="https://www.ufabc.edu.br/ensino/docentes/irineu-antunes-junior">Irineu Antunes Júnior</a>.

</body>

</html>
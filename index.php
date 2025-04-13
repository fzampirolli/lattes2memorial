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
    //header('Content-Type: application/octet-stream');
    //header("Content-Transfer-Encoding: utf-8");
    //header("Content-disposition: attachment; filename=\"" . basename($file) . "\"");

    // Verifique se o arquivo existe
    if (!file_exists($file)) {
        die("Arquivo ZIP não encontrado");
    }

    // Verifique as permissões do arquivo
    if (!is_readable($file)) {
        die("Sem permissão para ler o arquivo");
    }

    // Defina headers mais explícitos
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="' . basename($file) . '"');
    header('Content-Length: ' . filesize($file));
    header('Cache-Control: no-cache');
    header('Pragma: no-cache');

    // Limpe qualquer saída de buffer
    ob_clean();
    flush();

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
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>lattes2memorial</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 0;
      padding: 0;
      background-color: #f4f4f4;
      color: #333;
    }

    header {
      background-color: #4CAF50;
      color: white;
      padding: 20px 0;
      text-align: center;
    }

    h1 {
      margin: 0;
      font-size: 2rem;
    }

    .container {
      max-width: 800px;
      margin: 20px auto;
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    ul {
      list-style-type: square;
      padding-left: 20px;
    }

    ul li {
      margin-bottom: 10px;
    }

    a {
      color: #4CAF50;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    form {
      margin-top: 20px;
    }

    form label {
      font-weight: bold;
    }

    form input[type="file"] {
      margin: 10px 0;
    }

    form input[type="submit"] {
      background-color: #4CAF50;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 1rem;
    }

    form input[type="submit"]:hover {
      background-color: #45a049;
    }

    pre {
      background-color: #f8f8f8;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 5px;
      overflow-x: auto;
    }

    footer {
      text-align: center;
      margin-top: 20px;
      font-size: 0.9rem;
    }

    footer img {
      vertical-align: middle;
      margin-right: 10px;
    }

      .button-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .spinner {
        display: none;
        width: 16px;
        height: 16px;
        border: 3px solid #fff;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }

      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }

  </style>

  <script>
    document.addEventListener('DOMContentLoaded', function () {
      const form = document.querySelector('form');
      const spinner = document.getElementById('spinner');
      const submitButton = document.getElementById('submit-btn');
      const fileInput = document.getElementById('file-input');

      form.addEventListener('submit', function (e) {
        if (!fileInput.files.length) {
          e.preventDefault();
          alert('Por favor, selecione um arquivo ZIP antes de enviar.');
          return;
        }

        // Mostra o spinner ao lado do botão
        spinner.style.display = 'inline-block';
        submitButton.disabled = true;

        // Remove o spinner após 7 segundos (tempo estimado para download iniciar)
        setTimeout(() => {
          spinner.style.display = 'none';
          submitButton.disabled = false;
        }, 7000);
      });
    });
  </script>



</head>

<body>
  <header>
    <h1>lattes2memorial</h1>
  </header>

  <div class="container">
    <h2>Serviço de Upload e Conversão</h2>
    <p>
      Este serviço permite enviar um arquivo ZIP gerado pela <a href="https://lattes.cnpq.br/">plataforma Lattes</a> e obter os arquivos necessários para gerar um documento LaTeX.
    </p>
    <ul>
      <li>Envie o arquivo ZIP gerado pela plataforma Lattes exatamente no formato "CV_ID.zip", onde "ID" corresponde ao identificador único atribuído ao seu currículo na plataforma Lattes. Ver detalhes no <a href="https://github.com/fzampirolli/lattes2memorial" target="_blank">GitHub</a>.</li>
      <li>Após o envio, o servidor processa e cria os arquivos necessários para gerar um PDF pelo LaTeX.</li>
      <li>Os arquivos estarão compactados em um ZIP para download.</li>
      <li>Todos os arquivos no servidor relacionados ao seu Lattes serão removidos após o download.</li>
      <li>O conteúdo do ZIP pode ser adaptado no seu computador após a instalação das bibliotecas necessárias.</li>
      <li>Os arquivos contêm o mesmo conteúdo genérico disponível no
        <a href="https://github.com/fzampirolli/lattes2memorial" target="_blank">GitHub</a>.</li>
      <li>Bugs podem existir, pois este gerador foi criado para atender necessidades específicas do autor.</li>
      <li>Feedbacks e sugestões são bem-vindos. Entre em contato por e-mail:
        <a href="mailto:fzampirolli@ufabc.edu.br" target="_self">enviar e-mail</a>.</li>
    </ul>

    <hr>

    <h3>Envie seu arquivo</h3>


    <form action="" method="POST" enctype="multipart/form-data">
      <label for="file-input">Escolha o arquivo ZIP:</label><br />
      <input id="file-input" type="file" name="image" /><br /><br />

      <div class="button-wrapper">
        <input id="submit-btn" type="submit" value="Enviar" />
        <div id="spinner" class="spinner"></div>
      </div>
    </form>


  </div>

  <footer>
    <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank">
      <img src="http://mctest.ufabc.edu.br:8000/static/agplv3.png" alt="AGPL v3" width="50">
    </a>
    <p>
      Copyright © 2023-2025 por
      <a href="https://sites.google.com/site/fzampirolli/" target="_blank">Francisco de Assis Zampirolli</a> da
      <a href="http://www.ufabc.edu.br" target="_blank">UFABC</a> e colaboradores.
    </p>
  </footer>
</body>

</html>

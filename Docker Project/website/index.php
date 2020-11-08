<html>
    <head>
        <title>CIS 322 proj6-rest ACP Times list</title>
    </head>

    <body>
      	<h1>List All</h1>
	<ul>
	  <?php
	     $json = file_get_contents('http://laptop-service/listAll');
	     $obj = json_decode($json);
	     $openT = $obj->opening;
	  $closeT = $obj->closing;
	  echo "<b>Open Times</b>";
	     foreach ($openT as $l){
	  
	     echo "<li>$l</li>";
	  }
	  echo "<b>Close Times</b>";
	  foreach ($closeT as $k){
	  echo "<li>$k</li>";
	  }
	     
	     
	     ?>
	</ul>
	<h1>List Open Only</h1>
	<ul>
	  <?php
	      $json = file_get_contents('http://laptop-service/listAll');
             $obj = json_decode($json);
             $openT = $obj->opening;
          echo "Open Times";
             foreach ($openT as $l){
             echo "<li> $l </li>";
          }
	  ?>
        </ul>
	<h1>List Closed Only</h1>
	<ul>
	  <?php
	  $json = file_get_contents('http://laptop-service/listAll');
          $obj = json_decode($json);
          $closeT = $obj->closing;
          echo "Close Times";
          foreach ($closeT as $k){
          echo "<li> $k </li>";
          }
	  ?>
        </ul>
    </body>
</html>

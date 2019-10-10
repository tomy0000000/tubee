<?php
header("Access-Control-Allow-Origin: *");
$context = stream_context_create(array("http" => array('method' => "GET",
    'header' => "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36\r\n",
)));
$getdata = array();
foreach ($_GET as $key => $value) {
    $getdata[str_replace("_", ".", $key)] = $value;
}
$getdata = http_build_query($getdata);
$url = "https://pubsubhubbub.appspot.com/subscription-details?";
$res = file_get_contents($url . $getdata, false, $context);
print($res);
?>
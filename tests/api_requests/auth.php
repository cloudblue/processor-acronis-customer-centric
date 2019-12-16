<?php
/**
 * Created by PhpStorm.
 * User: Adrian
 * Date: 27/11/2018
 * Time: 16:39

This file is part of the Ingram Micro Cloud Blue Connect SDK.
Copyright (c) 2019 Ingram Micro. All Rights Reserved.

 */


$authMethod = "/idp/token";
$config_file = './rest-client.env.json';
$config = json_decode(file_get_contents($config_file));
$url = $config->development->host . $config->development->api_version . $authMethod;

$context = stream_context_create(array(
    'http' => array(
        'method' => 'POST',
        'header' => 'Content-type: application/x-www-form-urlencoded',
        'content' => http_build_query(
            array(
                'grant_type' => $config->development->grant_type,
                'username' => $config->development->username,
                'password' => $config->development->password,
            )
        ),
        'timeout' => 60
    )
));

$resp = json_decode(file_get_contents($url, FALSE, $context));

if (property_exists($resp, "access_token")) {
    $config->development->access_token = $resp->access_token;
    file_put_contents($config_file, str_replace(',', ",\r\n", json_encode($config, JSON_UNESCAPED_SLASHES)));
    echo "SUCCESS";
} else {
    print_r($resp, 1);
    echo "FAIL";
}

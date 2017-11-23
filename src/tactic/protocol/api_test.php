<?php



function executeREST($data) {
    $login_ticket = "south123paw";
    $url = "http://192.168.205.180/workflow/workflow/rest"
    $data['login_ticket'] = $login_ticket;


    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_FAILONERROR, true);

    $result = curl_exec($ch);
    if (curl_error($ch)) {
        throw new Exception(curl_error($ch));
    }
    $result = json_decode( $result );
    return $result;
}

$data = [
    'method' => 'get_by_search_key',
    'search_key' => 'workflow/asset?project=workflow&code=ASSET00002'
];

$result = executeREST($data);


echo 'description: ', $result->description;
echo 'status: ', $result->status;
echo "\n";
echo "---";
echo "\n";

$data = [
    'method' => 'get_by_code',
    'search_type' => 'workflow/job',
    'code' => 'JOB00220',
];
$result = executeREST($data);


print_r($result);
echo "\n";
echo "!---";
echo "\n";

$data = [
    'method' => 'query',
    'search_type' => 'workflow/asset',
];
$result = executeREST($data);



print_r($result);
echo "\n";
echo "---";
echo "\n";

$data = [
    'method' => 'eval',
    'kwargs' => json_encode( [
        'expression' => '@SOBJECT(workflow/asset)',
        'single' => true,
    ] ),
];
$result = executeREST($data);










?>

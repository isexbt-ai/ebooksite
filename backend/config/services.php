<?php

return [

    'postmark' => [
        'token' => env('POSTMARK_TOKEN'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'resend' => [
        'key' => env('RESEND_KEY'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    /*
    |--------------------------------------------------------------------------
    | Cloudflare R2 存储配置
    |--------------------------------------------------------------------------
    */

    'r2' => [
        'key'               => env('R2_ACCESS_KEY_ID'),
        'secret'            => env('R2_SECRET_ACCESS_KEY'),
        'region'            => env('R2_REGION', 'auto'),
        'endpoint'          => env('R2_ENDPOINT'),
        'bucket'            => env('R2_BUCKET'),
        'public_url'        => env('R2_PUBLIC_URL'),
        'presigned_expires' => env('R2_PRESIGNED_URL_EXPIRES', 3600),
    ],

];

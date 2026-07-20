<?php

namespace App\Http\Controllers;

use App\Services\ApiResponseService;
use Illuminate\Routing\Controller as BaseController;

class Controller extends BaseController
{
    protected ApiResponseService $api;

    public function __construct()
    {
        $this->api = new ApiResponseService();
    }
}

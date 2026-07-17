<?php

use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
*/

// 所有前端路由返回 index.html（SPA 模式）
Route::get('/{any?}', function () {
    $indexPath = public_path('index.html');
    if (file_exists($indexPath)) {
        return file_get_contents($indexPath);
    }
    return view('welcome');
})->where('any', '.*');

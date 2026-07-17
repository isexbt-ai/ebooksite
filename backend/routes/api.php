<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\BookController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\SettingsController;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// 公开路由
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);
Route::get('/settings/buy_link', [SettingsController::class, 'buyLink']);

// 书籍搜索（公开）
Route::get('/books/search', [BookController::class, 'search']);

// 需要登录的路由
Route::middleware('auth:sanctum')->group(function () {
    Route::post('/auth/logout', [AuthController::class, 'logout']);
    Route::get('/auth/me', [AuthController::class, 'me']);
    Route::post('/auth/redeem', [AuthController::class, 'redeem']);

    // 书籍
    Route::get('/books', [BookController::class, 'index']);
    Route::get('/books/{id}', [BookController::class, 'show']);
    Route::get('/books/download/{id}', [BookController::class, 'download']);

    // 用户设置
    Route::post('/user/settings', [UserController::class, 'updateProfile']);
    Route::post('/user/password', [UserController::class, 'changePassword']);

    // 反馈
    Route::post('/feedback', [SettingsController::class, 'feedback']);
});

// 管理员路由
Route::middleware('auth:sanctum')->prefix('admin')->group(function () {
    Route::post('/auth/login', [AdminController::class, 'login']);
    Route::get('/stats', [AdminController::class, 'stats']);
    Route::get('/users', [AdminController::class, 'users']);
    Route::post('/users/{id}/delete', [AdminController::class, 'deleteUser']);
    Route::get('/cards', [AdminController::class, 'cards']);
    Route::post('/cards/generate', [AuthController::class, 'generateCards']);
    Route::get('/books', [AdminController::class, 'books']);
    Route::post('/books/{id}/delete', [AdminController::class, 'deleteBook']);
    Route::get('/feedbacks', [AdminController::class, 'feedbacks']);
    Route::post('/feedbacks/{id}/delete', [AdminController::class, 'deleteFeedback']);
    Route::get('/settings', [AdminController::class, 'settings']);
    Route::post('/settings', [AdminController::class, 'saveSettings']);
});

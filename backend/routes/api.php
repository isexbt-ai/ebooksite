<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\BookController;
use App\Http\Controllers\BookUploadController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\SettingsController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// 公开路由
Route::get('/settings', [SettingsController::class, 'index']);
Route::post('/feedback', [SettingsController::class, 'feedback']);

// 认证路由
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);
Route::post('/auth/admin-login', [AuthController::class, 'adminLogin']);

// 书籍路由（公开）
Route::get('/books', [BookController::class, 'index']);
Route::get('/books/hot', [BookController::class, 'hot']);
Route::get('/books/{id}', [BookController::class, 'show']);

// 需要认证的路由
Route::middleware('auth:sanctum')->group(function () {
    // 认证相关
    Route::post('/auth/logout', [AuthController::class, 'logout']);
    Route::get('/auth/me', [AuthController::class, 'me']);
    Route::post('/auth/redeem', [AuthController::class, 'redeem']);

    // 用户资料
    Route::get('/profile', [UserController::class, 'profile']);
    Route::put('/profile', [UserController::class, 'updateProfile']);
    Route::put('/profile/password', [UserController::class, 'changePassword']);
    Route::get('/downloads', [UserController::class, 'downloads']);

    // 书籍下载
    Route::get('/books/{id}/download', [BookController::class, 'download']);

    // 删除自己的书籍
    Route::delete('/books/{id}', [BookUploadController::class, 'destroy']);
});

// 管理后台路由
Route::middleware(['auth:sanctum', 'admin'])->prefix('admin')->group(function () {
    Route::get('/dashboard', [AdminController::class, 'dashboard']);
    Route::post('/verify-password', [AdminController::class, 'verifyPassword']);

    // 用户管理
    Route::get('/users', [AdminController::class, 'users']);
    Route::delete('/users/{id}', [AdminController::class, 'deleteUser']);
    Route::delete('/users/batch', [AdminController::class, 'batchDeleteUsers']);

    // 书籍管理
    Route::get('/books', [AdminController::class, 'books']);
    Route::delete('/books/{id}', [AdminController::class, 'deleteBook']);
    Route::delete('/books/batch', [AdminController::class, 'batchDeleteBooks']);
    Route::post('/books/dedup', [AdminController::class, 'dedupBooks']);

    // 上传路由（仅管理员）
    Route::post('/upload/single', [BookUploadController::class, 'upload']);
    Route::post('/upload/multipart/initiate', [BookUploadController::class, 'initiateMultipart']);
    Route::post('/upload/multipart/chunk', [BookUploadController::class, 'uploadChunk']);
    Route::post('/upload/multipart/complete', [BookUploadController::class, 'completeMultipart']);
    Route::post('/upload/multipart/abort', [BookUploadController::class, 'abortMultipart']);
    Route::post('/upload/batch-dedup', [BookUploadController::class, 'batchUploadDedup']);

    // 卡密管理
    Route::get('/cards', [AdminController::class, 'cards']);
    Route::post('/cards', [AdminController::class, 'createCard']);

    // 反馈管理
    Route::get('/feedbacks', [AdminController::class, 'feedbacks']);
    Route::put('/feedbacks/{id}', [AdminController::class, 'updateFeedback']);
    Route::delete('/feedbacks/{id}', [AdminController::class, 'deleteFeedback']);

    // 系统设置
    Route::get('/settings', [AdminController::class, 'settings']);
    Route::put('/settings', [AdminController::class, 'saveSettings']);
});

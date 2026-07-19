<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\BookController;
use App\Http\Controllers\BookUploadController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\SettingsController;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// 认证路由
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth:sanctum');
Route::get('/user', [AuthController::class, 'user'])->middleware('auth:sanctum');

// 书籍路由（公开）
Route::get('/books', [BookController::class, 'index']);
Route::get('/books/{id}', [BookController::class, 'show']);

// 需要认证的路由
Route::middleware('auth:sanctum')->group(function () {
    // 普通上传
    Route::post('/books/upload', [BookUploadController::class, 'upload']);
    
    // 分片上传
    Route::post('/books/multipart/initiate', [BookUploadController::class, 'initiateMultipart']);
    Route::post('/books/multipart/chunk', [BookUploadController::class, 'uploadChunk']);
    Route::post('/books/multipart/complete', [BookUploadController::class, 'completeMultipart']);
    Route::post('/books/multipart/abort', [BookUploadController::class, 'abortMultipart']);
    
    // 批量上传
    Route::post('/books/batch-upload', [BookUploadController::class, 'batchUpload']);
    
    // 下载
    Route::get('/books/{id}/download', [BookUploadController::class, 'download']);
    
    // 删除
    Route::delete('/books/{id}', [BookUploadController::class, 'destroy']);
});

// 管理后台路由
Route::middleware(['auth:sanctum', 'admin'])->prefix('admin')->group(function () {
    Route::get('/dashboard', [AdminController::class, 'dashboard']);
    Route::get('/users', [AdminController::class, 'users']);
    Route::get('/books', [AdminController::class, 'books']);
    Route::get('/settings', [AdminController::class, 'settings']);
    Route::put('/settings', [AdminController::class, 'updateSettings']);
});

// 系统设置
Route::get('/settings', [SettingsController::class, 'index']);
Route::put('/settings', [SettingsController::class, 'update'])->middleware('auth:sanctum');

// 用户路由
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/profile', [UserController::class, 'profile']);
    Route::put('/profile', [UserController::class, 'updateProfile']);
    Route::get('/downloads', [UserController::class, 'downloads']);
});

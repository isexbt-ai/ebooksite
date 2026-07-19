<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('books', function (Blueprint ) {
            ->string('r2_key')->nullable()->comment('R2 存储键');
            ->string('r2_url')->nullable()->comment('R2 公开访问 URL');
            ->bigInteger('file_size')->nullable()->comment('文件大小(字节)');
            ->string('mime_type')->nullable()->comment('文件类型');
            ->string('upload_status')->default('pending')->comment('上传状态');
            ->string('upload_id')->nullable()->comment('分片上传ID');
            ->json('upload_parts')->nullable()->comment('分片信息');
        });
    }

    public function down(): void
    {
        Schema::table('books', function (Blueprint ) {
            ->dropColumn(['r2_key', 'r2_url', 'file_size', 'mime_type', 'upload_status', 'upload_id', 'upload_parts']);
        });
    }
};

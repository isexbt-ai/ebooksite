<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('books', function (Blueprint $table) {
            $table->id();
            $table->string('title', 500);
            $table->string('author', 200)->nullable();
            $table->string('category', 50)->nullable();
            $table->string('tags')->nullable();
            $table->text('description')->nullable();
            $table->string('cover_url', 500)->nullable();
            $table->string('r2_key', 500)->nullable();
            $table->string('r2_url', 500)->nullable();
            $table->unsignedBigInteger('file_size')->nullable();
            $table->string('file_format', 10)->nullable();
            $table->string('mime_type', 100)->nullable();
            $table->string('upload_status', 20)->default('pending');
            $table->string('upload_id')->nullable();
            $table->text('upload_parts')->nullable();
            $table->unsignedBigInteger('uploader_id')->nullable();
            $table->string('file_hash', 64)->nullable();
            $table->unsignedInteger('search_count')->default(0);
            $table->timestamps();
            $table->softDeletes();

            $table->index('search_count');
            $table->index('file_hash');
            $table->index('category');
            $table->foreign('uploader_id')->references('id')->on('users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('books');
    }
};

<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('books', function (Blueprint $table) {
            $table->id();
            $table->string('title', 500);
            $table->string('author', 200)->nullable();
            $table->text('file_path');
            $table->integer('file_size')->default(0);
            $table->string('file_format', 10)->nullable();
            $table->text('cover_path')->nullable();
            $table->text('description')->nullable();
            $table->text('tags')->nullable();
            $table->string('category', 100)->nullable();
            $table->timestamp('indexed_at')->nullable();
            $table->timestamps();

            $table->index('title');
            $table->index('author');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('books');
    }
};

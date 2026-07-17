<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Book extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'author',
        'file_path',
        'file_size',
        'file_format',
        'cover_path',
        'description',
        'tags',
        'category',
        'indexed_at',
    ];

    protected $casts = [
        'file_size' => 'integer',
        'indexed_at' => 'datetime',
    ];

    public function scopeSearch($query, string $keyword)
    {
        return $query->where(function ($q) use ($keyword) {
            $q->where('title', 'like', "%{$keyword}%")
              ->orWhere('author', 'like', "%{$keyword}%");
        });
    }
}

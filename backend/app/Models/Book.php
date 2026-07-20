<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Book extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'title',
        'author',
        'category',
        'tags',
        'description',
        'cover_url',
        'r2_key',
        'r2_url',
        'file_size',
        'file_format',
        'mime_type',
        'upload_status',
        'upload_id',
        'upload_parts',
        'uploader_id',
        'file_hash',
        'search_count',
    ];

    protected $casts = [
        'file_size' => 'integer',
        'search_count' => 'integer',
        'upload_parts' => 'array',
    ];

    public function uploader()
    {
        return $this->belongsTo(User::class, 'uploader_id');
    }

    public function downloads()
    {
        return $this->hasMany(Download::class);
    }

    /**
     * 搜索作用域 - 转义LIKE特殊字符防注入
     */
    public function scopeSearch($query, string $keyword)
    {
        $escaped = str_replace(['%', '_'], ['\%', '\_'], $keyword);
        return $query->where(function ($q) use ($escaped) {
            $q->where('title', 'like', "%{$escaped}%")
              ->orWhere('author', 'like', "%{$escaped}%");
        });
    }

    /**
     * 按分类筛选
     */
    public function scopeByCategory($query, string $category)
    {
        return $query->where('category', $category);
    }

    /**
     * 热门排序
     */
    public function scopeHot($query, int $limit = 10)
    {
        return $query->orderBy('search_count', 'desc')->limit($limit);
    }

    /**
     * 增加搜索计数
     */
    public function incrementSearchCount(): void
    {
        $this->increment('search_count');
    }
}

<?php

namespace App\Http\Controllers;

use App\Models\Book;
use App\Models\Download;
use App\Models\Setting;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class BookController extends Controller
{
    /**
     * 书籍列表（支持搜索和分类筛选）
     */
    public function index(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);
        $search = $request->get('search', '');
        $category = $request->get('category', '');

        $query = Book::where('upload_status', 'completed');

        if ($search) {
            $query->search($search);
        }

        if ($category) {
            $query->byCategory($category);
        }

        $books = $query->orderBy('title')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($books);
    }

    /**
     * 书籍详情
     */
    public function show(int $id): JsonResponse
    {
        $book = Book::find($id);

        if (!$book) {
            return $this->api->notFound('书籍不存在');
        }

        // 增加搜索计数
        $book->incrementSearchCount();

        return $this->api->success($book);
    }

    /**
     * 热门书籍
     */
    public function hot(Request $request): JsonResponse
    {
        $limit = $request->get('limit', 10);

        $books = Book::where('upload_status', 'completed')
            ->hot($limit)
            ->get();

        return $this->api->success([
            'items' => $books->map(function ($book, $index) {
                return array_merge($book->toArray(), ['rank' => $index + 1]);
            }),
        ]);
    }

    /**
     * 下载书籍（需要认证）
     */
    public function download(Request $request, int $id): JsonResponse
    {
        $user = $request->user();

        // 检查下载上限
        $today = now()->format('Y-m-d');
        $downloadCount = Download::where('user_id', $user->id)
            ->whereDate('created_at', $today)
            ->count();

        $limit = (int) Setting::get('download_limit', '10');

        if ($downloadCount >= $limit) {
            return $this->api->error("今日下载次数已达上限（{$limit}次），请明天再试", 2001, 403);
        }

        $book = Book::find($id);

        if (!$book || $book->upload_status !== 'completed') {
            return $this->api->notFound('书籍不存在或未上传完成');
        }

        // 记录下载
        Download::create([
            'user_id' => $user->id,
            'book_id' => $book->id,
        ]);

        // 返回R2公开URL（如果配置了公开访问）
        if ($book->r2_url) {
            return $this->api->success([
                'download_url' => $book->r2_url,
                'file_name'    => $this->sanitizeFilename($book->title) . '.' . $book->file_format,
                'file_size'    => $book->file_size,
            ]);
        }

        // 否则返回预签名URL
        $r2 = app(\App\Services\R2StorageService::class);
        $url = $r2->getPresignedUrl($book->r2_key);

        if (!$url) {
            return $this->api->error('生成下载链接失败', 2002, 500);
        }

        return $this->api->success([
            'download_url' => $url,
            'file_name'    => $this->sanitizeFilename($book->title) . '.' . $book->file_format,
            'file_size'    => $book->file_size,
            'expires_in'   => 3600,
        ]);
    }

    /**
     * 清理文件名中的非法字符
     */
    private function sanitizeFilename(string $filename): string
    {
        return preg_replace('/[^\w\-一-龥]/u', '_', $filename);
    }
}

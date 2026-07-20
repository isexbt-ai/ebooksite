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
     * 返回一次性下载 token，前端通过代理路由下载
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

        // 生成一次性下载 token（5分钟有效）
        $token = md5($user->id . $book->id . time() . uniqid());
        cache()->put("download_token:{$token}", [
            'book_id'  => $book->id,
            'user_id'  => $user->id,
        ], now()->addMinutes(5));

        return $this->api->success([
            'download_url' => url("/api/books/file/{$token}"),
            'file_name'    => $this->sanitizeFilename($book->title) . '.' . $book->file_format,
            'file_size'    => $book->file_size,
        ]);
    }

    /**
     * 代理下载文件（通过一次性 token）
     * 浏览器直接访问此 URL 触发下载
     */
    public function downloadFile(Request $request, string $token)
    {
        $cached = cache()->pull("download_token:{$token}");

        if (!$cached) {
            abort(404, '下载链接已过期或无效');
        }

        $book = Book::find($cached['book_id']);
        if (!$book || !$book->r2_key) {
            abort(404, '文件不存在');
        }

        $fileName = $this->sanitizeFilename($book->title) . '.' . $book->file_format;
        $downloadUrl = $book->r2_url;

        // 如果没有公开 URL，生成预签名 URL
        if (!$downloadUrl) {
            $r2 = app(\App\Services\R2StorageService::class);
            $downloadUrl = $r2->getPresignedUrl($book->r2_key);
            if (!$downloadUrl) {
                abort(500, '生成下载链接失败');
            }
        }

        // 使用 PHP stream 代理下载，设置 Content-Disposition 强制浏览器下载
        return response()->stream(function () use ($downloadUrl) {
            $ctx = stream_context_create([
                'http' => [
                    'method' => 'GET',
                    'timeout' => 300,
                    'follow_location' => true,
                ],
                'ssl' => [
                    'verify_peer' => false,
                    'verify_peer_name' => false,
                ],
            ]);
            $stream = @fopen($downloadUrl, 'rb', false, $ctx);
            if (!$stream) {
                abort(500, '无法连接文件服务器');
            }
            while (!feof($stream)) {
                echo fread($stream, 8192);
                flush();
            }
            fclose($stream);
        }, 200, [
            'Content-Type'        => $book->mime_type ?: 'application/octet-stream',
            'Content-Disposition' => 'attachment; filename="' . $fileName . '"',
            'Content-Length'      => $book->file_size,
            'Cache-Control'       => 'no-store',
            'X-Accel-Buffering'   => 'no',
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

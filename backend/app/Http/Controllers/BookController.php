<?php

namespace App\Http\Controllers;

use App\Models\Book;
use App\Models\UserDownload;
use App\Models\SystemSetting;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Crypt;
use Illuminate\Support\Facades\Log;
use Illuminate\Contracts\Encryption\DecryptException;

class BookController extends Controller
{
    /**
     * 搜索书籍
     */
    public function search(Request $request): JsonResponse
    {
        $query = $request->get('q', '');
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        if (empty($query)) {
            return response()->json(['err' => 'invalid_params', 'msg' => '请输入搜索关键词'], 400);
        }

        $books = Book::search($query)
            ->orderBy('title')
            ->paginate($size, ['*'], 'page', $page);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total' => $books->total(),
                'items' => $books->items(),
                'page' => $books->currentPage(),
                'size' => $books->perPage(),
            ],
        ]);
    }

    /**
     * 获取书籍列表
     */
    public function index(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        $books = Book::orderBy('title')
            ->paginate($size, ['*'], 'page', $page);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total' => $books->total(),
                'items' => $books->items(),
                'page' => $books->currentPage(),
                'size' => $books->perPage(),
            ],
        ]);
    }

    /**
     * 获取书籍详情
     */
    public function show(int $id): JsonResponse
    {
        $book = Book::find($id);

        if (!$book) {
            return response()->json(['err' => 'not_found', 'msg' => '书籍不存在'], 404);
        }

        return response()->json(['err' => 'ok', 'data' => $book]);
    }

    /**
     * 获取下载链接（预签名 URL）
     *
     * 验证下载权限和限速后，返回一个临时的预签名下载 URL。
     * 浏览器直接访问该 URL 即可下载文件。
     */
    public function download(Request $request, int $id): JsonResponse
    {
        $user = $request->user();

        // 检查下载上限
        $today = now()->format('Y-m-d');
        $downloadCount = UserDownload::where('user_id', $user->id)
            ->whereDate('created_at', $today)
            ->count();

        $limit = (int) SystemSetting::get('download_limit', '10');

        if ($downloadCount >= $limit) {
            return response()->json([
                'err' => 'download_limit_reached',
                'msg' => "今日下载次数已达上限（{$limit}次），请明天再试",
            ], 403);
        }

        $book = Book::find($id);

        if (!$book || !file_exists($book->file_path)) {
            return response()->json(['err' => 'not_found', 'msg' => '书籍不存在'], 404);
        }

        // 记录下载
        UserDownload::create([
            'user_id' => $user->id,
            'book_id' => $book->id,
        ]);

        // 生成预签名 Token
        $token = $this->generateDownloadToken($book, $user);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'download_url' => url("api/books/file/{$token}"),
                'expires_in' => 300, // 5 分钟
            ],
        ]);
    }

    /**
     * 提供文件下载（预签名 URL 验证）
     *
     * 浏览器直接访问此接口下载文件，无需 Authorization Header。
     */
    public function serveFile(Request $request, string $token)
    {
        $payload = $this->verifyDownloadToken($token);

        if (!$payload) {
            return response()->json(['err' => 'invalid_token', 'msg' => '下载链接已过期或无效'], 403);
        }

        $book = Book::find($payload['book_id']);

        if (!$book || !file_exists($book->file_path)) {
            return response()->json(['err' => 'not_found', 'msg' => '书籍不存在'], 404);
        }

        // 提供文件下载
        return response()->download(
            $book->file_path,
            $this->sanitizeFilename($book->title) . '.' . $book->file_format,
            [],
            'attachment'
        );
    }

    /**
     * 生成下载 Token
     */
    private function generateDownloadToken(Book $book, $user): string
    {
        $payload = [
            'book_id' => $book->id,
            'user_id' => $user->id,
            'exp' => now()->addMinutes(5)->timestamp,
            'nonce' => uniqid('', true),
        ];

        return Crypt::encryptString(json_encode($payload));
    }

    /**
     * 验证下载 Token
     */
    private function verifyDownloadToken(string $token): ?array
    {
        try {
            $decrypted = Crypt::decryptString($token);
            $payload = json_decode($decrypted, true);

            if (!$payload || !isset($payload['exp']) || $payload['exp'] < now()->timestamp) {
                return null;
            }

            return $payload;
        } catch (DecryptException $e) {
            Log::warning('下载 Token 验证失败', ['error' => $e->getMessage()]);
            return null;
        }
    }

    /**
     * 清理文件名中的非法字符
     */
    private function sanitizeFilename(string $filename): string
    {
        return preg_replace('/[^\w\-一-龥]/u', '_', $filename);
    }
}

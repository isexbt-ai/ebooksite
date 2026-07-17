<?php

namespace App\Http\Controllers;

use App\Models\Book;
use App\Models\UserDownload;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Storage;

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
     * 下载书籍
     */
    public function download(Request $request, int $id)
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

        return response()->download($book->file_path);
    }
}

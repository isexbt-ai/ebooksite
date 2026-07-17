<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Card;
use App\Models\Book;
use App\Models\Feedback;
use App\Models\SystemSetting;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;

class AdminController extends Controller
{
    /**
     * 管理员登录
     */
    public function login(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        $user = User::where('username', strtolower($validated['username']))->first();

        if (!$user || !Hash::check($validated['password'], $user->password)) {
            return response()->json(['err' => 'invalid_credentials', 'msg' => '用户名或密码错误'], 400);
        }

        if (!$user->is_admin) {
            return response()->json(['err' => 'forbidden', 'msg' => '需要管理员权限'], 403);
        }

        $token = $user->createToken('admin')->plainTextToken;

        return response()->json([
            'err' => 'ok',
            'data' => [
                'user_id' => $user->id,
                'username' => $user->username,
                'name' => $user->name,
                'token' => $token,
            ],
        ]);
    }

    /**
     * 获取统计数据
     */
    public function stats(): JsonResponse
    {
        return response()->json([
            'err' => 'ok',
            'data' => [
                'total_users' => User::count(),
                'total_books' => Book::count(),
                'total_cards' => Card::count(),
            ],
        ]);
    }

    /**
     * 获取用户列表
     */
    public function users(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        $users = User::orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total' => $users->total(),
                'items' => $users->items(),
                'page' => $users->currentPage(),
                'size' => $users->perPage(),
            ],
        ]);
    }

    /**
     * 删除用户
     */
    public function deleteUser(int $id): JsonResponse
    {
        $user = User::find($id);

        if (!$user) {
            return response()->json(['err' => 'not_found', 'msg' => '用户不存在'], 404);
        }

        $user->delete();

        return response()->json(['err' => 'ok']);
    }

    /**
     * 获取卡密列表
     */
    public function cards(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        $cards = Card::orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total' => $cards->total(),
                'items' => $cards->items(),
                'page' => $cards->currentPage(),
                'size' => $cards->perPage(),
            ],
        ]);
    }

    /**
     * 获取书籍列表
     */
    public function books(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);
        $search = $request->get('search', '');

        $query = Book::query();

        if ($search) {
            $query->search($search);
        }

        $books = $query->orderBy('title')
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
     * 删除书籍
     */
    public function deleteBook(int $id): JsonResponse
    {
        $book = Book::find($id);

        if (!$book) {
            return response()->json(['err' => 'not_found', 'msg' => '书籍不存在'], 404);
        }

        // 删除文件
        if (file_exists($book->file_path)) {
            unlink($book->file_path);
        }

        $book->delete();

        return response()->json(['err' => 'ok']);
    }

    /**
     * 获取反馈列表
     */
    public function feedbacks(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        $feedbacks = Feedback::orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total' => $feedbacks->total(),
                'items' => $feedbacks->items(),
                'page' => $feedbacks->currentPage(),
                'size' => $feedbacks->perPage(),
            ],
        ]);
    }

    /**
     * 删除反馈
     */
    public function deleteFeedback(int $id): JsonResponse
    {
        $feedback = Feedback::find($id);

        if (!$feedback) {
            return response()->json(['err' => 'not_found', 'msg' => '反馈不存在'], 404);
        }

        $feedback->delete();

        return response()->json(['err' => 'ok']);
    }

    /**
     * 获取系统设置
     */
    public function settings(): JsonResponse
    {
        $settings = SystemSetting::all()->pluck('value', 'key')->toArray();

        return response()->json(['err' => 'ok', 'data' => $settings]);
    }

    /**
     * 保存系统设置
     */
    public function saveSettings(Request $request): JsonResponse
    {
        foreach ($request->all() as $key => $value) {
            SystemSetting::set($key, (string) $value);
        }

        return response()->json(['err' => 'ok']);
    }
}

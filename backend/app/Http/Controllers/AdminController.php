<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Book;
use App\Models\Card;
use App\Models\Feedback;
use App\Models\Download;
use App\Models\Setting;
use App\Models\AuditLog;
use App\Services\R2StorageService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Str;

class AdminController extends Controller
{
    /**
     * 仪表盘统计
     */
    public function dashboard(): JsonResponse
    {
        return $this->api->success([
            'total_users'    => User::count(),
            'active_users'   => User::where('active', true)->count(),
            'expired_users'  => User::where('expiry_date', '<', now())->count(),
            'total_books'    => Book::where('upload_status', 'completed')->count(),
            'total_cards'    => Card::count(),
            'used_cards'     => Card::where('used', true)->count(),
            'total_downloads' => Download::count(),
            'today_downloads' => Download::whereDate('created_at', today())->count(),
            'pending_feedbacks' => Feedback::where('status', 'pending')->count(),
        ]);
    }

    /**
     * 用户列表
     */
    public function users(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);
        $search = $request->get('search', '');

        $query = User::query();

        if ($search) {
            $query->where(function ($q) use ($search) {
                $q->where('username', 'like', "%{$search}%")
                  ->orWhere('name', 'like', "%{$search}%");
            });
        }

        $users = $query->orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($users);
    }

    /**
     * 删除用户
     */
    public function deleteUser(int $id): JsonResponse
    {
        $user = User::find($id);

        if (!$user) {
            return $this->api->notFound('用户不存在');
        }

        if ($user->is_admin) {
            return $this->api->error('不能删除管理员', 4001, 403);
        }

        $user->delete();

        AuditLog::log('delete', 'user', $id);

        return $this->api->success(null, '删除成功');
    }

    /**
     * 批量删除用户
     */
    public function batchDeleteUsers(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'ids'   => 'required|array',
            'ids.*' => 'integer',
        ]);

        $deleted = 0;
        foreach ($validated['ids'] as $id) {
            $user = User::find($id);
            if ($user && !$user->is_admin) {
                $user->delete();
                $deleted++;
            }
        }

        AuditLog::log('batch_delete', 'user', null, null, ['count' => $deleted]);

        return $this->api->success(['deleted' => $deleted], "已删除{$deleted}个用户");
    }

    /**
     * 书籍列表（管理）
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

        $books = $query->orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($books);
    }

    /**
     * 删除书籍
     */
    public function deleteBook(int $id): JsonResponse
    {
        $book = Book::find($id);

        if (!$book) {
            return $this->api->notFound('书籍不存在');
        }

        if ($book->r2_key) {
            $r2 = app(R2StorageService::class);
            $r2->delete($book->r2_key);
        }

        $book->delete();

        AuditLog::log('delete', 'book', $id);

        return $this->api->success(null, '删除成功');
    }

    /**
     * 批量删除书籍
     */
    public function batchDeleteBooks(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'ids'   => 'required|array',
            'ids.*' => 'integer',
        ]);

        $r2 = app(R2StorageService::class);
        $deleted = 0;

        foreach ($validated['ids'] as $id) {
            $book = Book::find($id);
            if ($book) {
                if ($book->r2_key) {
                    $r2->delete($book->r2_key);
                }
                $book->delete();
                $deleted++;
            }
        }

        AuditLog::log('batch_delete', 'book', null, null, ['count' => $deleted]);

        return $this->api->success(['deleted' => $deleted], "已删除{$deleted}本书籍");
    }

    /**
     * 书籍去重
     */
    public function dedupBooks(): JsonResponse
    {
        $books = Book::whereNotNull('file_hash')->get();
        $groups = [];

        foreach ($books as $book) {
            $groups[$book->file_hash][] = $book;
        }

        $removed = 0;
        $r2 = app(R2StorageService::class);

        foreach ($groups as $hash => $groupBooks) {
            if (count($groupBooks) > 1) {
                usort($groupBooks, fn($a, $b) => $b->file_size <=> $a->file_size);
                array_shift($groupBooks); // 保留最大的

                foreach ($groupBooks as $book) {
                    if ($book->r2_key) {
                        $r2->delete($book->r2_key);
                    }
                    $book->delete();
                    $removed++;
                }
            }
        }

        AuditLog::log('dedup', 'book', null, null, ['removed' => $removed]);

        return $this->api->success(['removed' => $removed], "已去除{$removed}本重复书籍");
    }

    /**
     * 卡密列表
     */
    public function cards(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);
        $type = $request->get('type', '');

        $query = Card::query();

        if ($type) {
            $query->where('type', $type);
        }

        $cards = $query->orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($cards);
    }

    /**
     * 创建卡密 - 统一4段4位大写字母格式
     */
    public function createCard(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'count'         => 'required|integer|min:1|max:100',
            'type'          => 'required|string|in:register,renew',
            'duration_days' => 'required|integer|min:1|max:3650',
        ]);

        $codes = [];
        for ($i = 0; $i < $validated['count']; $i++) {
            $code = $this->generateCardCode();
            Card::create([
                'code'          => $code,
                'type'          => $validated['type'],
                'duration_days' => $validated['duration_days'],
            ]);
            $codes[] = $code;
        }

        AuditLog::log('create_cards', 'card', null, null, [
            'count' => count($codes),
            'type'  => $validated['type'],
        ]);

        return $this->api->success([
            'count' => count($codes),
            'codes' => $codes,
        ], '创建成功', 201);
    }

    private function generateCardCode(): string
    {
        $parts = [];
        for ($i = 0; $i < 4; $i++) {
            $parts[] = Str::upper(Str::random(4));
        }
        return implode('-', $parts);
    }

    /**
     * 反馈列表
     */
    public function feedbacks(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);
        $status = $request->get('status', '');

        $query = Feedback::query();

        if ($status) {
            $query->where('status', $status);
        }

        $feedbacks = $query->orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($feedbacks);
    }

    /**
     * 更新反馈状态
     */
    public function updateFeedback(Request $request, int $id): JsonResponse
    {
        $feedback = Feedback::find($id);

        if (!$feedback) {
            return $this->api->notFound('反馈不存在');
        }

        $validated = $request->validate([
            'status' => 'required|string|in:pending,replied,resolved',
        ]);

        $feedback->update(['status' => $validated['status']]);

        return $this->api->success(null, '更新成功');
    }

    /**
     * 删除反馈
     */
    public function deleteFeedback(int $id): JsonResponse
    {
        $feedback = Feedback::find($id);

        if (!$feedback) {
            return $this->api->notFound('反馈不存在');
        }

        $feedback->delete();

        AuditLog::log('delete', 'feedback', $id);

        return $this->api->success(null, '删除成功');
    }

    /**
     * 获取系统设置
     */
    public function settings(): JsonResponse
    {
        $settings = Setting::all()->pluck('value', 'key')->toArray();
        return $this->api->success($settings);
    }

    /**
     * 保存系统设置
     */
    public function saveSettings(Request $request): JsonResponse
    {
        $oldSettings = Setting::all()->pluck('value', 'key')->toArray();

        foreach ($request->all() as $key => $value) {
            Setting::set($key, (string) $value);
        }

        AuditLog::log('update', 'settings', null, $oldSettings, $request->all());

        return $this->api->success(null, '保存成功');
    }

    /**
     * 管理员二次验证密码
     */
    public function verifyPassword(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'password' => 'required|string',
        ]);

        $user = $request->user();

        if (!\Illuminate\Support\Facades\Hash::check($validated['password'], $user->password)) {
            return $this->api->error('密码错误', 4002);
        }

        // 生成临时验证token（5分钟有效）
        $token = $user->createToken('admin_verify', ['admin_verify'], now()->addMinutes(5))->plainTextToken;

        return $this->api->success(['verify_token' => $token], '验证通过');
    }
}
